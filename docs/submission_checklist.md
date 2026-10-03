# Official Requirements and Submission Checklist

Sources: all four pages of the participant-provided Track A brief; official Devpost event rules, overview and update; official UCI repository entry. Track requirements below follow the PDF. Unspecified limits are not inferred.

## Track A mandatory requirements

| Requirement | Status | Evidence |
|---|---|---|
| Predict overall CAD | Complete | `artifacts/cardia_models.joblib` → `CAD`; source label `Cath` |
| Predict LAD, LCX, RCA stenosis | Complete | Same bundle contains `LAD`, `LCX`, `RCA` |
| Use demographic, exam, ECG, lab, echo features | Complete | 54 predictor schema in `artifacts/features.json`, `artifacts/ui_schema.json` |
| Exclude `LAD`, `LCX`, `RCA`, `Cath` from every predictor matrix | Complete | `scripts/train.py`; `tests/test_model_contract.py` |
| Classification evaluation: accuracy, precision, recall, F1, ROC-AUC | Complete | `artifacts/evaluation.json`; report PDF |
| Interactive 3D torso/heart | Complete | `app/static/app.js`; browser-rendered and inspected original schematic |
| Vessel probability coloring for LAD/LCX/RCA | Complete | `app/static/app.js`; color legend in application |
| Rotate, zoom, select anatomical region/vessel | Complete | Local browser interaction verified; labels track 3D vessel markers |
| Show CAD and vessel probabilities with 3D | Complete | Application dashboard |
| Patient-specific interpretability and physiological inputs | Complete | Approximate permutation SHAP on deployed pipeline; app form and charts |
| Clinical safety disclaimer | Complete | Visible UI callout and report |
| Responsive, modern browser, no dedicated GPU requirement | Implemented; limited check | 3D uses WebGL/Three.js; narrow and desktop view inspected on one browser/device only |
| Working integrated web prototype | Complete | Local FastAPI + bundled browser application, `scripts/run_local.sh` |
| Clean code, model weights, documentation, max-six-page report | Complete | Complete source and serialized models in submission ZIP; report is 5 pages |
| 3–10 minute YouTube demo | Script ready; recording outstanding | `demo_script.md`; recording/upload is a user action |

## Judging criteria from Track A brief

| Criterion | Weight | Project evidence |
|---|---:|---|
| Predictive performance, estimation quality, validation | 30% | Nested repeated stratified CV, fixed 0.50 threshold, ROC-AUC/PR-AUC/Brier/ECE and confusion counts in report/artifacts |
| 3D visualization and spatial mapping | 25% | Original rotatable/zoomable anterior coronary schematic with anatomy labels and explicit probability legend |
| Clinical interpretability | 20% | Patient-specific SHAP feature contributions, source values, explanations and safety limitations |
| System integration | 15% | Patient form → local API → four model outputs → 3D colors and SHAP |
| Technical implementation | 10% | Reproducible scripts, pinned dependencies, model artifacts, API health/schema, attribution and source documentation |

## Dataset and model audit evidence

- Official UCI dataset 411, Extension of Z-Alizadeh Sani, CC BY 4.0; SHA-256 of downloaded workbook: `739343245c2ba578b541370217531750d8e936022f928b83e0d91756caa3ff0b`.
- Primary sheet: 303 records × 59 columns; zero missing values; zero exact duplicate rows; no identifier column.
- Positive/negative counts: CAD 216/87, LAD 177/126, LCX 119/184, RCA 114/189.
- One invariant predictor `Exertional CP` removed; `Fmale` normalized to `Female`; 54 remaining predictors.
- 302/303 source `Cath` labels agree with the OR of vessel labels; the source label is preserved and the mismatch disclosed.
- Outer evaluation uses two repeats of stratified 5-fold CV; inner 3-fold ROC-AUC selects among three fixed model families. Final family selection uses separate 5-fold ROC-AUC on all records, followed by fit on all records. No independent test cohort exists.
- Brier and 5-bin ECE/reliability diagnostics were computed; no recalibration or calibration validation is claimed.
- SHAP uses 24 fixed background rows and six permutations; additivity and source-feature mapping verified. It explains model associations, not causes.

## Event-wide rules, deadlines and limits

- Event development period: 30 September–14 October 2026 EOD.
- Devpost deadline: **15 October 2026, 12:15 AM IST** (just after midnight following 14 October).
- Team rule: solo to four people; one track per team and one submitting team per individual.
- Eligibility discrepancy: the event overview says “students only”; the separate Rules page says individuals aged 14+ and broader eligibility. Confirm eligibility with the organizer if needed.
- AI coding assistants are allowed; disclose them in Devpost “Built With” and the README and be able to explain the work. README discloses OpenAI Codex.
- Devpost is the submission destination. Track PDF limit: report ≤6 pages; video 3–10 minutes.
- **Not stated in the reviewed official materials:** Devpost required-field details, archive/file-size cap, number of allowed assets/links, required hosting platform for source code, or any additional common-rule document. No limits have been invented. No separate common-rules attachment was present.

## Deliverables and user actions

- Local app, code, model weights, preprocessing, source dataset, attribution, report PDF/source, and demo script are included in the submission ZIP.
- The report is verified at 5 pages; page renders were visually checked.
- Video has not been recorded here. Record the supplied 5-minute script, upload to YouTube if required by the Track A brief, add the link to the Devpost entry, and disclose Codex under Built With.
- Before submission, confirm entrant eligibility (overview/rules discrepancy), log in to Devpost, inspect current submission form/file limits, and submit before the deadline. Submission/public upload was not performed.

## Final audit status (4 October 2026)

Status meanings: **PASS** = directly checked in the local project; **FAIL** = known unmet requested outcome; **UNVERIFIED** = not checked or dependent on unavailable access.

| Requirement or task | Status | Evidence / blocker |
|---|---|---|
| Track A outcome set, predictor families, and target exclusion | PASS | 4 serialized targets; 54 predictor fields; tests and data audit |
| Leakage-safe fold preprocessing and fixed threshold | PASS | Training pipelines and saved nested repeated CV results; fixed 0.50 threshold |
| Required actual metrics for every target | PASS | Accuracy, precision, recall, F1, and ROC-AUC in evaluation JSON/report/app |
| Integrated 3D dashboard and patient SHAP | PASS | Local browser demo renders all targets, source feature values, contributions, baseline, and schematic controls |
| Clinical disclaimer, probability bands, and uncertainty | PASS | UI labels schematic and bands; not a diagnostic or imaging substitute |
| Anatomically informed original 3D visualization | PARTIAL | Original procedural chamber, great-vessel and artery geometry; broad LAD/LCX/RCA courses checked against NHLBI/NCBI references. The chamber illustration is simplified, not a clinical mesh, and has not had clinician review or segment-level anatomical validation. Provenance is documented in `docs/third_party_notices.md`. |
| Local automated and browser interaction checks | PASS | 6 Python unit tests; continuous probability-boundary tests; frontend syntax; live local predictions, colors, vessel selection, explanations, rotation and wheel zoom response; see `docs/verification.md` |
| Container build and hosted service | PASS | Render successfully built and started the Docker service on Free; `/api/health`, schema, performance, predictions, and explanations returned successfully. Local Docker build and long-term resource behavior were not tested. |
| GitHub publication | PASS | New public repository `https://github.com/pavitra-G16/cardia-atlas-multimodal-ai-hackathon-2026`; latest `main` publication verified via GitHub API. |
| Public deployment and live prediction/explanation smoke tests | PASS | `https://cardia-atlas.onrender.com`, Render service `cardia-atlas`; the published Render revision is Live. Public API returned actual demo inference for all four outcomes and explanations with 0.000 pp displayed additivity difference. The public browser UI, color bins, input update, vessel selection, and explanations were checked. Free instance may cold-start after inactivity. |
| YouTube demo and hackathon submission | FAIL | Neither was uploaded or submitted. Entrant must record/upload video and complete Devpost entry. |

The official Track A PDF and Devpost rules/overview were reviewed earlier in this project. No separate common-rules document or submission form was supplied. No submission field or archive limit has been inferred.
