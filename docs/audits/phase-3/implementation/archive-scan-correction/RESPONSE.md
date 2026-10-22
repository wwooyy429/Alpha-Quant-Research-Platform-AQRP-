# Archive scan correction — developer evidence

Final archive commit bc99dc671d7292a8cb9e77cea17d91e84193bc6d failed both CI jobs in run 39682778261 at secret scanning after computation/tests. It is not a passing CI. The original failure ZIP and redacted findings are retained; source execution at 07e7c88745c031feeaee5d1e374a02caada77777 remains separately identified.

The finding is the immutable public synthetic CACHE_HIT event at validation-07e7c88/sdk/research/runs/826873ac-7112-4114-8518-1ae98b5c11d9/events.jsonl:8. Its key_hash 69266f2ffa606b5e7b3f052cb193dcf9de2e8c0b70a71467217e8b848332c554 equals an independently recomputed SHA-256 of the canonical key stored in the matching cache file. It is not authentication material. Original event bytes are unchanged.

A narrow gitleaks allowlist requires BOTH that exact historical path AND the exact extracted cache SHA-256. No directory exclusion, generic key_hash exclusion, scanner version change or disabled control is introduced. Altered lines and findings elsewhere remain subject to all pinned default rules. Positive and negative scanner controls remain mandatory. This correction changes scanner configuration/evidence only; business Python, tests, tools, dependency lock and workflow stay byte-identical to 07e7c88. Final fixed commit CI must separately pass.

No actual OS isolation deployment, formal sealed Test or independent reviewer execution is claimed.

An intermediate GLOBAL allowlist candidate was rejected by an adversarial control: the pinned scanner skipped the matched path before evaluating the exact cache digest. It was never committed. The final exception uses targetRules=[generic-api-key], retaining AND semantics at rule evaluation. All three controls pass: exact original event allowed; same digest elsewhere detected; synthetic credential on a changed line at the original path detected. Pinned primary specification: https://github.com/gitleaks/gitleaks/blob/v8.30.1/README.md#configuration . The pre-existing P1 global exception is unchanged and is not asserted to have been corrected by this narrow P3 fix.

A full-line rule candidate was also rejected on the original multi-event file. Final matching is on the exact extracted public cache SHA-256, scoped to generic-api-key AND the exact historical file path. Original event-file SHA-256 remains pinned in FILE_MANIFEST. No arbitrary hash or changed credential value is allowed.
