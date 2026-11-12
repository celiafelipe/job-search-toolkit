"""Private, file-based workspace and requisition ledger."""
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def instant(value):
    result = dt.datetime.fromisoformat(value)
    require(result.tzinfo is not None, "Timestamps require a timezone")
    return result


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def record(path):
    return {"path": str(Path(path).resolve()), "sha256": digest(path)}


def atomic(path, value):
    path = Path(path)
    fd, temp = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
        dir_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dir_fd)
        finally:
            os.close(dir_fd)
    finally:
        Path(temp).unlink(missing_ok=True)


def workspace(path, initialized=True):
    path = Path(path).expanduser().resolve()
    require(not path.is_relative_to(ROOT), "Keep private workspace outside the toolkit")
    require(not any((p / ".git").exists() for p in [path, *path.parents]),
            "Keep private workspace outside a Git checkout")
    if initialized:
        require((path / "ledger.json").is_file(), "Initialize the private workspace first")
    return path


def inside(root, path, file=True):
    path = (root / path).resolve()
    require(path.is_relative_to(root), "Artifact must be inside the private workspace")
    if file:
        require(path.is_file(), f"Missing artifact: {path}")
    return path


def checked(root, item):
    path = inside(root, item["path"])
    require(digest(path) == item["sha256"], f"Bytes changed: {path}")
    return path


def url(value):
    parts = urlsplit(value)
    require(parts.scheme == "https" and parts.hostname and not parts.username and not parts.password,
            "Use an observed HTTPS URL without credentials")
    # Keep query and fragment: either may carry a real requisition identifier.
    return urlunsplit(("https", parts.netloc.lower(), parts.path or "/", parts.query, parts.fragment))


def text(value, label):
    require(isinstance(value, str) and value.strip(), f"Missing {label}")
    return value.strip()


@contextlib.contextmanager
def transaction(root):
    with (root / ".ledger.lock").open("a", encoding="utf-8") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        data = read(root / "ledger.json")
        yield data
        atomic(root / "ledger.json", data)


def init(root, demo):
    import shutil
    root.mkdir(mode=0o700)
    for template in (ROOT / "templates").iterdir():
        if template.is_file():
            shutil.copyfile(template, root / template.name)
    (root / "roles").mkdir()
    atomic(root / "ledger.json", {"schema": 1, "demo": demo, "browser_owner": None, "roles": {}})
    return str(root)


def snapshot(root, job):
    folder = root / "job-snapshots"
    folder.mkdir(exist_ok=True)
    path = folder / f"{uuid4()}.json"
    atomic(path, job)
    return record(path)


def intake(root, source, refresh=False):
    job = read(inside(root, source))
    for key in ("role_id", "company", "title", "observed_at", "identity_evidence"):
        text(job[key], key)
    instant(job["observed_at"])
    require(isinstance(job["aliases"], list), "aliases must be a list of URLs")
    require(isinstance(job["requisition_id"], str), "Use empty requisition_id if none observed")
    links = {url(job["posting_url"]), *(url(x) for x in job["aliases"])}
    with transaction(root) as data:
        matches = []
        for key, existing in data["roles"].items():
            same_req = (job["requisition_id"] and job["requisition_id"] == existing["requisition_id"]
                        and job["company"].strip().casefold() == existing["company"].strip().casefold())
            overlap = links & set(existing["urls"])
            if key == job["role_id"]:
                require(same_req or overlap, "Role ID collision: reconcile canonical identity manually")
            if same_req or overlap:
                matches.append(key)
        require(len(matches) <= 1, "New evidence links multiple registered roles; reconcile identity before action")
        key = matches[0] if matches else job["role_id"]
        if matches:
            existing = data["roles"][key]
            require(job["company"].strip().casefold() == existing["company"].strip().casefold(),
                    "Conflicting employer on a known alias; reconcile identity")
            previous_req, observed_req = existing["requisition_id"], job["requisition_id"]
            require(not (previous_req and observed_req and previous_req != observed_req),
                    "Conflicting requisition IDs on a known alias; reconcile identity before action")
            if observed_req and not previous_req:
                existing["requisition_id"] = observed_req
            existing["urls"] = sorted(links | set(existing["urls"]))
            if refresh:
                require(job["role_id"] == key and existing["state"] in
                        ("discovered", "no_submission"),
                        "Refresh requires canonical role ID and no active transmission or attempt")
                existing["job"] = snapshot(root, job)
                existing["title"] = job["title"]
            return {"role_id": key, "existing": True, "state": existing["state"], "job": existing["job"]}
        entry = {name: job[name] for name in ("company", "title", "requisition_id")}
        entry.update(urls=sorted(links), job=snapshot(root, job), attempts=[], state="discovered")
        data["roles"][key] = entry
        return {"role_id": job["role_id"], "existing": False, "state": "discovered", "job": entry["job"]}


def lock(root, owner, release=False):
    text(owner, "run identity")
    with transaction(root) as data:
        current = data["browser_owner"]
        if release:
            require(current and current["id"] == owner, "Only the recorded owner may release the browser")
            data["browser_owner"] = None
        else:
            require(not current, "Browser already owned; inspect tracker and defer")
            data["browser_owner"] = {"id": owner, "acquired_at": now()}
        return {"browser_owner": data["browser_owner"]}


def owned(data, owner):
    require(data["browser_owner"] and data["browser_owner"]["id"] == owner,
            "Acquire this workspace's browser lease before application actions")


def live_mode(data, plan, simulate):
    host = urlsplit(plan["destination_url"]).hostname
    require(simulate == data["demo"], "Simulation must use a workspace initialized with --demo")
    require(not simulate or (host and host.endswith(".example")), "Demo destination must end in .example")
    require(simulate or not host.endswith((".example", ".test", ".invalid", ".localhost")),
            "Reserved destinations cannot be used for live attempts")


def allowed_prefix(destination, prefix):
    target, scope = urlsplit(destination), urlsplit(url(prefix))
    require(not scope.query and not scope.fragment and
            (scope.path == "/" or not scope.path.endswith("/")),
            "A destination prefix must be an exact origin or path without a trailing slash")
    # Fail closed for encoded or dot-segment paths that browsers/servers may normalize.
    for path in (target.path, scope.path):
        if "%" in path or "\\" in path or "//" in path or {"..", "."} & set(path.split("/")):
            return False
    return (target.netloc == scope.netloc and
            (scope.path == "/" or target.path == scope.path or target.path.startswith(scope.path + "/")))


def authorized(root, plan, review, policy, approval, simulate, action):
    require(policy["mode"] in ("ask-per-package", "scoped"),
            "Preparation-only policy: no application transmission authorized")
    require(action in policy["actions"], f"Policy does not authorize {action}")
    if policy["mode"] == "ask-per-package":
        grant = read(inside(root, text(approval, "path to recorded explicit approval")))
        require(grant["role_id"] == plan["role_id"] and
                grant["destination_url"] == plan["destination_url"] and
                grant["review_sha256"] == review["sha256"] and action in grant["actions"],
                "Approval must match role, destination, exact review, and action")
    else:
        grant = policy
        require(urlsplit(plan["destination_url"]).hostname in grant["destination_hosts"],
                "Destination outside the configured policy scope")
        screen = read(checked(root, plan["screen"]))
        selection = grant.get("selection", "listed_roles")
        if selection == "listed_roles":
            require(plan["role_id"] in grant["role_ids"], "Role outside the configured policy scope")
        else:
            require(selection == "eligible_roles", "Unknown scoped selection mode")
            require(any(allowed_prefix(plan["destination_url"], prefix)
                        for prefix in grant["destination_prefixes"]),
                    "Destination outside the explicitly authorized URL prefixes")
            job = read(checked(root, plan["job"]))
            require(plan["destination_url"] in {url(link) for link in job["aliases"] + [job["posting_url"]]},
                    "Scoped discovery requires the employer destination in the registered job snapshot")
            for key in ("rubric", "search_preferences"):
                check = screen[key]
                checked(root, check)
                require(check["sha256"] == grant[f"{key}_sha256"],
                        f"Screening used different {key} bytes than the authorized policy")
        require(screen["verdict"] == "pursue" and not screen["hard_gaps"] and not screen["unknowns"],
                "Scoped policy requires eligible screening with no hard gaps or unresolved criteria")
        require(type(screen["score"]) in (int, float) and type(grant["min_score"]) in (int, float)
                and 0 <= grant["min_score"] <= screen["score"] <= 100,
                "Below scoped policy score or invalid score")
    text(grant["authorized_by"], "authorizing person")
    text(grant["evidence"], "explicit approval source and scope")
    require(grant["simulation"] is simulate, "Simulation grants cannot authorize live actions")
    clock = instant(now())
    require(instant(grant["authorized_at"]) <= clock < instant(grant["expires_at"]),
            "Approval is future-dated or expired")


def authorize_action(root, package, review_file, approval, owner, action, simulate):
    from .quality import gate
    with transaction(root) as data:
        owned(data, owner)
        review_path = inside(root, review_file)
        plan = gate(root, package, review_file, final=(action == "submit"))
        review = record(review_path)
        live_mode(data, plan, simulate)
        entry = data["roles"][plan["role_id"]]
        checked(root, entry["job"])
        require(entry["job"] == plan["job"], "Package does not use the registered job snapshot")
        require(entry["state"] in ("discovered", "transmission_authorized", "no_submission"),
                f"Role is {entry['state']}; reconcile before more transmission")
        for key, other in data["roles"].items():
            if key != plan["role_id"]:
                require(plan["destination_url"] not in other["urls"],
                        f"Destination already associated with {key}; reconcile identity")
        if action == "submit":
            require(entry.get("transmission"), "Check and record transmission authority first")
            require(entry["transmission"]["review"] == review,
                    "Review changed; recheck and record transmission authority for this version")
            require(entry["transmission"]["destination_url"] == plan["destination_url"],
                    "Destination changed; reconcile any transmitted data before proceeding")
        policy_path = inside(root, "policy.json")
        policy = read(policy_path)
        if action == "submit":
            require("transmit" in policy["actions"], "Submission also requires transmission scope")
            authorized(root, plan, review, policy, approval, simulate, "transmit")
        authorized(root, plan, review, policy, approval, simulate, action)
        if plan["destination_url"] not in entry["urls"]:
            entry["urls"].append(plan["destination_url"])
        evidence = {"owner": owner, "at": now(), "destination_url": plan["destination_url"],
                    "review": review, "policy": record(policy_path),
                    "approval": record(inside(root, approval)) if approval else None}
        if action == "transmit":
            entry["state"] = "transmission_authorized"
            entry["transmission"] = evidence
            entry.setdefault("transmission_history", []).append(evidence)
            return evidence
        attempt = {**evidence, "id": str(uuid4()), "state": "submit_started",
                   "package": record(inside(root, package)), "simulation": simulate}
        entry["state"] = "submit_started"
        entry["attempts"].append(attempt)
        return attempt


def resolve(root, role, attempt_id, outcome, evidence_file, owner):
    evidence_path = inside(root, evidence_file)
    proof = read(evidence_path)
    with transaction(root) as data:
        owned(data, owner)
        entry = data["roles"][role]
        require(entry["state"] in ("submit_started", "uncertain"), "No unresolved submission")
        attempt = entry["attempts"][-1]
        require(attempt["id"] == attempt_id == proof["attempt_id"] and proof["role_id"] == role
                and proof["destination_url"] == attempt["destination_url"],
                "Evidence does not match the role, destination, and attempt")
        require(instant(attempt["at"]) <= instant(proof["observed_at"]) <= instant(now()),
                "Evidence must be contemporaneous with or later than the attempt")
        text(proof["observation"], "receipt wording or authoritative observation")
        kind = proof["kind"]
        allowed = {"submitted_verified": {"portal_confirmation", "portal_history", "user_verified_receipt"},
                   "no_submission": {"portal_explicit_no_submission", "employer_explicit_no_submission"},
                   "uncertain": {"ambiguous"}}
        require(kind in allowed[outcome], "Evidence kind does not establish the requested outcome")
        require(proof["simulation"] is data["demo"], "Evidence simulation flag does not match workspace")
        entry["state"] = outcome
        attempt["state"] = outcome
        attempt.setdefault("observations", []).append(record(evidence_path))
        if outcome == "no_submission":
            entry.pop("transmission", None)
        return {"role_id": role, "attempt_id": attempt_id, "state": outcome}


def recover_lock(root, owner, evidence):
    proof = read(inside(root, evidence))
    require(proof["owner"] == owner, "Recovery evidence belongs to another run")
    require(proof["kind"] in ("user_confirmed_inactive", "host_confirmed_terminated"),
            "A timeout does not prove the owner stopped")
    text(proof["observation"], "proof the owning run stopped")
    with transaction(root) as data:
        current = data["browser_owner"]
        require(current and current["id"] == owner, "Owner changed; stop and inspect")
        require(instant(current["acquired_at"]) <= instant(proof["observed_at"]) <= instant(now()),
                "Stale owner evidence")
        for entry in data["roles"].values():
            if (entry["state"] == "submit_started" and entry["attempts"][-1]["owner"] == owner):
                entry["state"] = entry["attempts"][-1]["state"] = "uncertain"
        data.setdefault("lock_recoveries", []).append(record(inside(root, evidence)))
        data["browser_owner"] = None
        return {"browser_owner": None, "next": "Reconcile any uncertain attempt read-only."}



def existing_submission(root, role, evidence_file, owner):
    """Import a verified manual application without inventing a toolkit attempt."""
    path = inside(root, evidence_file)
    proof = read(path)
    with transaction(root) as data:
        owned(data, owner)
        entry = data["roles"][role]
        require(entry["state"] == "discovered", "Use attempt reconciliation for a tracked execution")
        require(proof["role_id"] == role and proof["kind"] in
                ("portal_confirmation", "portal_history", "user_verified_receipt"),
                "Verified external receipt must identify this role")
        require(proof["simulation"] is data["demo"], "Evidence simulation flag does not match workspace")
        require(instant(proof["observed_at"]) <= instant(now()), "Future observation")
        text(proof["observation"], "receipt wording or authoritative observation")
        destination = url(proof["destination_url"])
        live_mode(data, {"destination_url": destination}, data["demo"])
        for key, other in data["roles"].items():
            require(key == role or destination not in other["urls"],
                    "Destination already belongs to another registered role")
        entry["urls"] = sorted(set(entry["urls"]) | {destination})
        entry["external_receipt"] = record(path)
        entry["state"] = "submitted_verified"
        return {"role_id": role, "state": entry["state"], "source": "verified_external_receipt"}
