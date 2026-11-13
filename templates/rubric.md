# Screening rubric

Record user-defined hard conditions, weighted criteria totaling 100, and decision thresholds. Keep missing facts distinct from disqualifiers. Do not invent a policy threshold.

## Hard gates

Conditions that rule a role out whatever its score (for example a sector they won't work in, or a location they can't do). They have no weight.

- 

## Weighted criteria

Weights total 100 (`python3 -m toolkit lint` checks this).

| Criterion | Weight | What evidence qualifies? |
| --- | --- | --- |
| | | |

## How each criterion is scored

Give each criterion a fraction of its weight, so different agents score the same way:

- **Full** (100%): clear, direct match, evidenced in the posting and the experience files.
- **Most** (75%): a match with one minor gap, or direct evidence from an older role.
- **Half** (50%): adjacent experience, or the posting is unclear on this point.
- **Little** (25%): weak or indirect match.
- **None** (0%): no match, or a known mismatch.

Facts that are unknown (salary not published, say) score Half and go in `unknowns`, not `hard_gaps`.

## Thresholds

- Pursue threshold and conditions:
- Hold conditions:
- Skip conditions:
- Known exceptions explicitly approved for screening:
