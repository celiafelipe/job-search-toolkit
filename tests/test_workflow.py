import datetime as dt
import tempfile
from pathlib import Path
import unittest

from examples.demo import DESTINATION, ROLE, demo_receipt, enable_demo, fixture
from toolkit import core, pdf, quality


class Workflow(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root, self.folder, self.package, self.review, self.approval = fixture(
            Path(self.temp.name) / "private", with_cv=False)
        self.owner = "test-run"
        core.lock(self.root, self.owner)

    def act(self, action, simulation=True):
        return core.authorize_action(self.root, self.package, self.review, self.approval,
                                     self.owner, action, simulation)

    def change(self, file, **updates):
        doc = core.read(file)
        doc.update(updates)
        core.atomic(file, doc)

    def rebind(self, package_key, file, **updates):
        self.change(file, **updates)
        self.change(self.package, **{package_key: core.record(file)})
        self.change(self.review, package=core.record(self.package))
        self.change(self.approval, review_sha256=core.digest(self.review))

    def job(self, role_id, requisition, aliases=(), refresh=False):
        path = self.folder / f"{role_id}.json"
        original = core.read(self.folder / "job.json")
        original.update(role_id=role_id, requisition_id=requisition,
                        posting_url=f"https://jobs.example/{role_id}", aliases=list(aliases))
        core.atomic(path, original)
        return core.intake(self.root, path, refresh)

    def test_default_and_exact_scope(self):
        with self.assertRaisesRegex(ValueError, "Preparation-only"):
            self.act("transmit")
        enable_demo(self.root)
        with self.assertRaisesRegex(ValueError, "Simulation must use"):
            self.act("transmit", simulation=False)
        self.change(self.approval, actions=["transmit"])
        self.act("transmit")
        with self.assertRaisesRegex(ValueError, "Approval must match"):
            self.act("submit")

    def test_scoped_policy_expiry_and_screening(self):
        core.atomic(self.root / "policy.json", {
            "mode": "scoped", "actions": ["transmit", "submit"], "role_ids": [ROLE],
            "destination_hosts": ["careers.orchard-lantern.example"], "min_score": 89,
            "authorized_by": "Fictional candidate", "simulation": True,
            "authorized_at": core.now(), "expires_at": core.now(), "evidence": "Fictional policy"
        })
        with self.assertRaisesRegex(ValueError, "Below scoped policy"):
            self.act("transmit")
        self.change(self.root / "policy.json", min_score=88)
        with self.assertRaisesRegex(ValueError, "expired"):
            self.act("transmit")
        self.change(self.root / "policy.json",
                    expires_at=(core.instant(core.now()) + dt.timedelta(hours=1)).isoformat())
        self.act("transmit")
        self.act("submit")

    def test_opt_in_allows_new_roles_only_in_approved_tenant_and_rubric(self):
        rubric = self.root / "rubric.md"
        preferences = self.root / "search-preferences.md"
        self.rebind("screen", self.folder / "screen.json", rubric=core.record(rubric),
                    search_preferences=core.record(preferences))
        policy = self.root / "policy.json"
        core.atomic(policy, {"mode": "scoped", "selection": "eligible_roles",
                    "actions": ["transmit", "submit"], "role_ids": [],
                    "destination_hosts": ["careers.orchard-lantern.example"],
                    "destination_prefixes": ["https://careers.orchard-lantern.example/role"],
                    "rubric_sha256": core.digest(rubric), "search_preferences_sha256": core.digest(preferences),
                    "min_score": 80, "authorized_by": "Fictional candidate", "simulation": True,
                    "authorized_at": core.now(),
                    "expires_at": (core.instant(core.now()) + dt.timedelta(hours=1)).isoformat(),
                    "evidence": "Fictional opt-in limited to the employer tenant"})
        with self.assertRaisesRegex(ValueError, "authorized URL prefixes"):
            self.act("transmit")
        self.change(policy, destination_prefixes=["https://careers.orchard-lantern.example/roles"])
        self.change(policy, rubric_sha256="f" * 64)
        with self.assertRaisesRegex(ValueError, "different rubric"):
            self.act("transmit")
        self.change(policy, rubric_sha256=core.digest(rubric))
        self.act("transmit")
        self.assertEqual(self.act("submit")["state"], "submit_started")

    def test_answers_changed_and_same_context(self):
        answers = self.folder / "answers.json"
        original = answers.read_bytes()
        with answers.open("ab") as stream:
            stream.write(b" ")
        with self.assertRaisesRegex(ValueError, "Bytes changed"):
            quality.gate(self.root, self.package, self.review)
        answers.write_bytes(original)
        self.change(self.review, review_session="fictional-prep-run")
        with self.assertRaisesRegex(ValueError, "different fresh session"):
            quality.gate(self.root, self.package, self.review)

    def test_transmission_checkpoint_requires_current_review(self):
        enable_demo(self.root)
        self.act("transmit")
        self.change(self.review, review_session="fictional-review-run-2")
        self.change(self.approval, review_sha256=core.digest(self.review))
        with self.assertRaisesRegex(ValueError, "Review changed"):
            self.act("submit")
        self.act("transmit")
        self.act("submit")

    def test_final_requires_complete_form(self):
        enable_demo(self.root)
        self.rebind("inspection", self.folder / "inspection.json", coverage="observed_only")
        self.act("transmit")
        with self.assertRaisesRegex(ValueError, "conditional fields"):
            self.act("submit")

    def test_empty_required_answer_and_letter_limit(self):
        fields = core.read(self.folder / "answers.json")["fields"]
        fields[0]["value"] = " "
        self.rebind("answers", self.folder / "answers.json", fields=fields)
        with self.assertRaisesRegex(ValueError, "missing or blank"):
            quality.gate(self.root, self.package, self.review)
        fields[0]["value"] = "Rowan Example"
        fields.append({"prompt": "Letter", "kind": "letter", "value": "Evidence text", "source": "EX-A"})
        self.rebind("answers", self.folder / "answers.json", fields=fields)
        self.rebind("inspection", self.folder / "inspection.json", letter_mode="text_required",
                    letter_prompt="Letter", letter_max_chars=2)
        with self.assertRaisesRegex(ValueError, "character limit"):
            quality.gate(self.root, self.package, self.review)

    def test_recovery_does_not_retry_then_verified_once(self):
        enable_demo(self.root)
        self.act("transmit")
        attempt = self.act("submit")
        with self.assertRaisesRegex(ValueError, "submit_started"):
            self.act("submit")
        evidence = self.folder / "orphan.json"
        core.atomic(evidence, {"owner": self.owner, "kind": "host_confirmed_terminated",
                               "observed_at": core.now(), "observation": "Fictional worker ended"})
        core.recover_lock(self.root, self.owner, evidence)
        self.owner = "replacement"
        core.lock(self.root, self.owner)
        with self.assertRaisesRegex(ValueError, "uncertain"):
            self.act("transmit")
        proof = demo_receipt(self.folder, attempt["id"], "portal_history", "Fictional matching receipt")
        with self.assertRaisesRegex(ValueError, "does not establish"):
            core.resolve(self.root, ROLE, attempt["id"], "no_submission", proof, self.owner)
        core.resolve(self.root, ROLE, attempt["id"], "submitted_verified", proof, self.owner)
        row = core.read(self.root / "ledger.json")["roles"][ROLE]
        self.assertEqual(len(row["attempts"]), 1)
        self.assertEqual(row["state"], "submitted_verified")
        with self.assertRaisesRegex(ValueError, "submitted_verified"):
            self.act("transmit")

    def test_authoritative_no_submission_reopens_without_erasing_attempt(self):
        enable_demo(self.root)
        self.act("transmit")
        first = self.act("submit")
        proof = demo_receipt(self.folder, first["id"], "portal_explicit_no_submission",
                             "Fictional portal specifically confirms this attempt was not submitted")
        core.resolve(self.root, ROLE, first["id"], "no_submission", proof, self.owner)
        with self.assertRaisesRegex(ValueError, "transmission authority"):
            self.act("submit")
        self.act("transmit")
        second = self.act("submit")
        self.assertNotEqual(second["id"], first["id"])
        self.assertEqual(len(core.read(self.root / "ledger.json")["roles"][ROLE]["attempts"]), 2)

    def test_role_identity_bridge_and_missing_requisition(self):
        self.job("r1", "")
        self.job("r1", "new-id", refresh=True)
        repost = self.job("r2", "new-id")
        self.assertEqual(repost["role_id"], "r1")
        self.job("r3", "independent")
        with self.assertRaisesRegex(ValueError, "multiple registered roles"):
            self.job("r4", "", ["https://jobs.example/r2", "https://jobs.example/r3"])
        with self.assertRaisesRegex(ValueError, "Conflicting requisition IDs"):
            self.job("r1", "different-id")
        self.assertEqual(set(core.read(self.root / "ledger.json")["roles"]), {ROLE, "r1", "r3"})

    def test_external_receipt_blocks_duplicate(self):
        proof = self.folder / "external-receipt.json"
        core.atomic(proof, {"role_id": ROLE, "kind": "user_verified_receipt",
                            "destination_url": DESTINATION, "observed_at": core.now(),
                            "observation": "Fictional applicant showed receipt", "simulation": True})
        core.existing_submission(self.root, ROLE, proof, self.owner)
        enable_demo(self.root)
        with self.assertRaisesRegex(ValueError, "submitted_verified"):
            self.act("transmit")


@unittest.skipUnless(all(pdf.tools().values()), "Chrome and Poppler are required for integration")
class PDFIntegration(unittest.TestCase):
    def test_real_build_then_pdf_tamper(self):
        with tempfile.TemporaryDirectory() as temp:
            root, _, package, review, _ = fixture(Path(temp) / "private", with_cv=True)
            plan = quality.gate(root, package, review, final=True)
            outgoing = Path(plan["attachments"][0]["file"]["path"])
            self.assertTrue(outgoing.read_bytes().startswith(b"%PDF"))
            with outgoing.open("ab") as stream:
                stream.write(b"% altered")
            with self.assertRaisesRegex(ValueError, "Bytes changed"):
                quality.gate(root, package, review, final=True)
