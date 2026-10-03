# Verification Record

Date: 4 October 2026 (Asia/Kolkata)

## Passed

- Read every page of the attached four-page Track A brief and checked the official Devpost overview, rules, and update. Requirements are mapped in `submission_checklist.md`.
- UCI workbook retrieval from the official endpoint: clean-start path verified using a certifi CA bundle. Re-downloaded workbook SHA-256 matched the original. Audit remains 303 × 59, zero missing values, zero exact duplicates, and same target counts.
- Data target encoding and source consistency: CAD `Cath` / CAD-Normal; vessel labels `Stenotic`/`Normal`; 302 of 303 Cath outcomes match the OR of the three vessel labels.
- Leakage check: 54 model predictor fields contain none of `Cath`, `LAD`, `LCX`, `RCA`. Constant field exclusion and `Fmale` normalization are recorded.
- Nested repeated stratified 5-fold training (two repeats), inner 3-fold candidate selection, threshold 0.50 fixed. Saved final model families: CAD Extra Trees, LAD Random Forest, LCX Random Forest, RCA Logistic Regression.
- Artifact reload equivalence: all four saved model pipelines reproduced their bundle probabilities to 12 decimal places. Six Python unit tests passed, including median/mode demo contract, missing-artifact handling, and static asset revalidation headers. Continuous JavaScript probability boundary tests passed for 0, values on both sides of 0.33/0.67, exact boundaries, 1, and invalid inputs.
- Final API check: health=ok; 54-field schema; valid demo input returned all four predictions and SHAP contributions in 2.69 seconds; absolute SHAP additivity error was 0 for all four targets; all-missing input was accepted and imputed; invalid category and out-of-range numeric input returned HTTP 422; missing model artifacts returned a friendly HTTP 503. Temporary screenshot-capture endpoint was removed (now returns 404).
- Frontend JavaScript syntax checked with `node --check`. Three.js files are bundled locally; no external font or runtime CDN is required.
- Browser integration: visible updated 3D WebGL render and exact synthetic median/mode demo label. Changing Typical Chest Pain from 1 to 0 changed all four predictions: CAD 83.1%→53.4%, LAD 74.4%→41.7%, LCX 53.4%→38.0%, RCA 50.6%→32.3%. Each matching probability color changed; all four outcome/vessel selections updated their selected state and patient-specific explanation, with zero displayed additivity discrepancy. Drag changed all projected vessel label positions; wheel input changed their projection relative to reset view; Reset restored the initial camera. Boundary thresholds are [0,0.33), [0.33,0.67), and [0.67,1], illustrative only. All-blank inference showed each input as imputed. At a 390 px viewport earlier, document and body widths remained 390 px; the latest view was checked at desktop size.
- Deployment configuration: `render.yaml` declares a free Docker web service and `/api/health` check; Docker is unavailable, so the YAML/container startup and hosted behavior remain unverified. GitHub authentication now succeeds; remote publication status is tracked in the final audit table.
- Public repository verification: remote `main` contents and commit were read through GitHub API. A clean shallow clone from the public remote installed all pinned `requirements.txt` dependencies in a new Python 3.14 virtual environment; all four unit tests passed in that clone. Running its app locally returned `/api/health` status `ok`, four predictions, four SHAP explanation groups, and additivity errors below 2.3×10⁻¹⁶ on the synthetic demo sample.
- Report PDF: 5 pages (<6); all pages were rendered and visually inspected for layout, tables, figures, attribution, and footer. Every one of the 36 report metric cells was compared to `/api/performance` and the saved `evaluation.json`; all match after correcting LAD specificity to 0.70 ± 0.13. Figure 2 is code-derived from updated routes and actual synthetic median/mode demo predictions; it is not described as an application screenshot or anatomical validation.
- Dataset attribution and CC BY 4.0 notice, Three.js MIT notice, and AI-use disclosure are included.

## Not verified / remaining

- Docker is not installed in the environment; image build/start is unverified.
- Cross-browser/device coverage, screen-reader audit, performance across GPU-free devices, external or temporal clinical validation, clinician review, fairness analysis, and prospective testing were not performed.
- Calibration is assessed descriptively (Brier, five-bin ECE/reliability) only. No recalibration or validation of clinical risk probabilities is claimed.
- YouTube recording and external Devpost submission were not performed. Official upload/file-size limits were not stated in the pages reviewed; check the current entry form.
