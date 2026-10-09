# ECON-001 descriptive baseline and identification gap

## Verified arithmetic, not a productivity effect

Three published rounded Census rates for the collection period ending May3,2026 are Information39.7%, Finance and Insurance33.9%, National19.8%. The frozen comparisons give5.8,19.9,14.1 percentage points and rate ratios1.171091445428,2.005050505051,1.712121212121. All selected cells remain included. Thirteen author tests passed; an independently written exact-rational evaluator checked every point and rounding endpoint. Deliberately changing a reported difference or source rate is rejected. Source facts were separately read from the official Census article.

Conditional rounding envelopes assume nearest0.1pp publication precision. They are not sampling confidence intervals. Standard errors, covariances, sample counts, microdata and productivity outcomes are unavailable here. National observations overlap sector observations. No significance, adoption growth, causal effect, TFP, labor outcome or investment recommendation is inferred. The November17,2025 question break is retained. Parent ECON-001 remains OPEN; originality claim NONE.

## Scope and proposed future identification

See problems/ECON-001/experiments/identification-plan.md for a proposed DAG, missing identification requirements, future offer-effect design, observational alternatives, pretrend/placebo requirements, alternative outcomes and an algebraic misclassification sensitivity relation. The document is a research design proposal, not an empirical estimate or authorized study execution. It was completed by the coordinator after the worker paused for main-project priority. Its causal-design reasoning has not received an additional independent external/methodological review. Verified numerical arithmetic must not be read as validating that proposal.

## Chronology and failures

Fresh search and local frozen admission preceded the deterministic author computation. No local pre-computation Git commit or public preregistration snapshot was created; do not claim one. Source/spec SHA256 values are preserved. Worker handed off at11:59UTC for higher-priority engineering review capacity; coordinator then compared all outputs, added fixed verifier tampering checks and completed documentation without a new stochastic experiment.

Initial Git clone lacked authentication; the exact public base was reconstructed through connector reads and SHA-verified. Two reconstruction attempts failed due signature formatting before successful verification. NBER page opens failed twice; no full NBER paper is claimed read. Direct Census HTML retrieval returned403; web source text was readable. No raw HTML snapshot is archived. The factual three-cell transcription has its own hash, not a claim of a source-page byte hash. Source methodology v4 is2023 and was not verified as the latest2026 specification. The page displays publicationMay26 and last-revisedMay22; no revision ordering is inferred.

## Reproduce offline

Python3 standard library, no packages, network or paid resources. From repo root:

    python3 -m unittest discover -s problems/ECON-001/experiments -p 'test_btos_baseline.py' -v
    python3 problems/ECON-001/experiments/btos_baseline.py --root . --round 20261009T115523985642Z-gpt-ECON-001 --output /tmp/econ-btos.json
    python3 problems/ECON-001/experiments/independent_review/verify_economics.py runs/20261009T115523985642Z-gpt-ECON-001/frozen-spec.json runs/20261009T115523985642Z-gpt-ECON-001/source-extract.json problems/ECON-001/results/btos-baseline.json
    python3 problems/ECON-001/experiments/independent_review/test_negative_controls.py runs/20261009T115523985642Z-gpt-ECON-001/frozen-spec.json runs/20261009T115523985642Z-gpt-ECON-001/source-extract.json problems/ECON-001/results/btos-baseline.json

Pinned governance9c3ae2dbaa1c814f3ef451c041dedfe3b77d926f metadata checks are separate from substantive verification. Own candidate branch/draft PR only; owner review required, no merge.

Initial local path validation rejected identification-plan.md directly under the problem directory. It was relocated under the already registered experiments/ path without changing the frozen question or gate. No gate bypass or artifact-root modification.
