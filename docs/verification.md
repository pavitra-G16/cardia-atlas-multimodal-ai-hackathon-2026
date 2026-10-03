# Verification Record

Date: 4 October 2026 (Asia/Kolkata)

## Passed

- Read every page of the attached four-page Track A brief and checked the official Devpost overview, rules, and update. Requirements are mapped in `submission_checklist.md`.
- UCI workbook retrieval from the official endpoint: clean-start path verified using a certifi CA bundle. Re-downloaded workbook SHA-256 matched the original. Audit remains 303 × 59, zero missing values, zero exact duplicates, and same target counts.
- Data target encoding and source consistency: CAD `Cath` / CAD-Normal; vessel labels `Stenotic`/`Normal`; 302 of 303 Cath outcomes match the OR of the three vessel labels.
- Leakage check: 54 model predictor fields contain none of `Cath`, `LAD`, `LCX`, `RCA`. Constant field exclusion and `Fmale` normalization are recorded.
- Nested repeated stratified 5-fold training (two repeats), inner 3-fold candidate selection, threshold 0.50 fixed. Saved final model families: CAD Extra Trees, LAD Random Forest, LCX Random Forest, RCA Logistic Regression.
- Artifact reload equivalence: all four saved model pipelines reproduced their bundle probabilities to 12 decimal places. Focused unit tests: 4 passed, including missing-artifact handling.
- Final API check: health=ok; 54-field schema; valid demo input returned all four predictions and SHAP contributions in 2.69 seconds; absolute SHAP additivity error was 0 for all four targets; all-missing input was accepted and imputed; invalid category and out-of-range numeric input returned HTTP 422; missing model artifacts returned a friendly HTTP 503. Temporary screenshot-capture endpoint was removed (now returns 404).
- Frontend JavaScript syntax checked with `node --check`. Three.js files are bundled locally; no external font or runtime CDN is required.
- Browser integration: visible 3D WebGL render, demo input/result flow, probability legend, vessel selection updates corresponding SHAP explanation, drag rotates the model, and projected artery labels move with their vessel markers. At a 390 px viewport, the document and body widths both remained 390 px (no horizontal page overflow). Desktop and narrow layouts were inspected in the Codex in-app browser. A distinct zoom change was not re-verified in this final audit.
- Input sensitivity: changing the synthetic Typical Chest Pain code from 1 to 0 changed all four predictions and the corresponding SHAP contribution; the displayed additivity discrepancy remained 0.000. All-blank inference showed each input as imputed.
- Deployment configuration: `render.yaml` declares a free Docker web service and `/api/health` check; Docker is unavailable, so the YAML/container startup and hosted behavior remain unverified. GitHub authentication now succeeds; remote publication status is tracked in the final audit table.
- Report PDF: 5 pages (<6), rendered all pages, visually inspected layout, headings, tables, figures, attribution, and footer. Actual outer-fold performance and a canvas screenshot from the live demo are included.
- Dataset attribution and CC BY 4.0 notice, Three.js MIT notice, and AI-use disclosure are included.

## Not verified / remaining

- Docker is not installed in the environment; image build/start is unverified.
- Cross-browser/device coverage, screen-reader audit, performance across GPU-free devices, external or temporal clinical validation, clinician review, fairness analysis, and prospective testing were not performed.
- Calibration is assessed descriptively (Brier, five-bin ECE/reliability) only. No recalibration or validation of clinical risk probabilities is claimed.
- YouTube recording and external Devpost submission were not performed. Official upload/file-size limits were not stated in the pages reviewed; check the current entry form.
