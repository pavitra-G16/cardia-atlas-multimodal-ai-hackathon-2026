# Cardia Atlas

Cardia Atlas is an educational web prototype for Track A of the Multimodal AI Hackathon 2026. It estimates overall coronary artery disease (CAD) and LAD, LCX, and RCA stenosis probabilities from the UCI Extension of Z-Alizadeh Sani dataset. It combines a local prediction API, patient-specific SHAP explanations, and an original interactive 3D coronary schematic.

**Developed by Pavitra Gangwar.**

> **Safety:** This is a research and educational prototype, not a diagnostic device or clinical risk calculator. It is not a substitute for a clinician or formal diagnostic imaging. Probabilities are model outputs, not measured stenosis percentages or lesion locations.

## Run the application

Verified runtime: Python 3.14.2, a modern WebGL-enabled browser. No API key, paid service, or external font/model request is needed at runtime. The Docker image targets Python 3.14; container startup still needs a local Docker verification.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000/>. The example button loads synthetic feature-wise median/mode values explicitly labeled as a demo; those values are not a study patient and are not evaluation evidence. Inputs are sent to the configured app API for inference and are not stored by the application. Use synthetic data only; do not submit identifiable or real patient data.

## Reproduce the data audit and training

The licensed UCI workbook is already included in `data/raw/`. To retrieve it afresh from the official UCI endpoint and rerun the complete workflow:

```bash
.venv/bin/python scripts/prepare_data.py
.venv/bin/python scripts/build_ui_schema.py
.venv/bin/python scripts/train.py
```

The preparation script verifies expected dimensions, records missingness, duplicates, target distributions, and the CAD/vessel label relationship, then writes a clean CSV and JSON audit. Training uses seed `271828`, 54 predictors, fold-local imputation/encoding/scaling, and nested repeated stratified 5-fold CV (two repeats). In each outer training partition, inner 3-fold ROC-AUC selects one of Logistic Regression, Extra Trees, or Random Forest. The threshold remains 0.50 throughout. A separate 5-fold comparison on all records selects the final pipeline for each target, and each final pipeline is refit on all 303 records. Outer-fold results estimate generalization; final models are not externally validated.

The final serialized artifact is `artifacts/cardia_models.joblib`; per-target pipelines, data audit, feature/UI schema, and metrics are also saved under `artifacts/`. Imputers, encoders, and scalers live inside each serialized pipeline. The source workbook is never modified. The single observed `Fmale` category is normalized to `Female`; invariant `Exertional CP` (all 303 rows equal `N`) is excluded. No record ID exists. The four outcome columns `Cath`, `LAD`, `LCX`, and `RCA` are never predictors. Other observed clinical/ECG/laboratory/echo fields are retained. One row has a CAD/Cath label inconsistent with the OR of the three vessel targets (302/303 agree); the supplied Cath label is preserved for overall CAD.

The UI expands documented clinical shorthand such as DM, HTN, CVA, and CHF using a published description of this dataset's feature names. The UCI variable table does not define numeric code meanings or measurement units; source codes and categories therefore remain unchanged, with unknown code meanings labeled as such. No units are inferred.

## Results (actual experiment)

Performance in the accompanying report comes from repeated outer-fold validation, reported as outer-fold mean ± standard deviation, with a fixed 0.50 threshold. Brier score and 5-bin expected calibration error/reliability bins were also computed on outer-fold probabilities as descriptive calibration checks; no recalibration was performed and the scores are not validated clinical risks. Targets are imbalanced, and results vary by fold. LAD performed better than LCX/RCA; no result establishes clinical utility. The model family chosen from the complete dataset is CAD Extra Trees, LAD Random Forest, LCX Random Forest, and RCA Logistic Regression (the artifact records the separate all-data 5-fold selection scores). Refer to `artifacts/evaluation.json` for full metrics, confusion matrices, fold-level values, and model selection evidence.

## Architecture

- `app/main.py`: FastAPI API, input validation, inference, feature mapping, SHAP, health/schema/performance endpoints.
- `app/static/`: responsive browser UI and bundled Three.js modules; the heart and simplified vessel geometry are original procedural code, not a downloaded medical mesh.
- `scripts/prepare_data.py`: reproducible official-source data acquisition and audit.
- `scripts/train.py`: nested model comparison and final refit.
- `scripts/build_ui_schema.py`: constructs the form schema from observed feature values.
- `artifacts/`: serialized model pipelines, schema, audit and real experiment outputs.
- `reports/`: editable report source, generated PDF and actual validation figure.
- `docs/`: requirement checklist and third-party attribution.

The visualization is an anterior-view educational schematic. RCA is routed on the viewer-left side to represent the patient's right, LAD along the anterior center, and LCX toward the patient's left/viewer-right. Rotate with drag, zoom with wheel/pinch, and select via artery label/card. Color bins are illustrative only: <33% green, 33–67% amber, >67% red. Selecting a vessel updates its SHAP summary. No output paints a measured lesion location.

## API

- `GET /api/health`
- `GET /api/schema`
- `GET /api/performance`
- `GET /api/example`
- `POST /api/predict` with `{"values": {"Age": 58, ...}}`

Fields may be omitted or blank and are imputed. Unknown fields, invalid categories, non-finite values, and numeric values outside the observed source range are rejected with HTTP 422; the prototype blocks extrapolation beyond the small dataset's observed range. Scores are returned for CAD/LAD/LCX/RCA. SHAP uses a fixed 24-row background, six permutation cycles, and the deployed preprocessing/model. One-hot contributions are summed back to source input fields. Output and contributions are in positive-class probability units; the expected baseline plus all contributions equals the model score (verified). Permutation SHAP is approximate with finite permutations; contributions are associations, not causes.

## Checks

Run the focused artifact/schema/serialization checks:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

The integrated local API was exercised with the synthetic demo profile, all fields missing, and an invalid category; model probability, 422 validation and SHAP additivity were inspected. WebGL rendering, input flow, visible outputs, and vessel selection were inspected in the local browser. See the report and `docs/verification.md` for checks that remain unavailable in this environment.

## Build and container

`Dockerfile` packages the local API, bundled UI, model pipelines, and data required for example inputs and SHAP. It listens on `PORT` (default 10000), exposes `/api/health` as its health check, and `render.yaml` prepares a single Docker web service. The deployment blueprint and container were not verified here because Docker and an authenticated hosting account were unavailable. The configured free service may have cold starts and resource limits; performance and SHAP latency must be smoke-tested on the host before sharing a public URL.

```bash
docker build -t cardia-atlas .
docker run --rm -e PORT=8000 -p 8000:8000 cardia-atlas
```

For Render, authenticate and connect this GitHub repository, create a Blueprint from `render.yaml`, and deploy the Docker web service. It serves both the frontend and API in one process/container; no external model download or API secret is configured. Verify `/api/health`, `/?demo=1`, `POST /api/predict`, and browser 3D interactions after deployment. Do not treat deployment as complete until those public checks pass.

## Data and third-party attribution

- Dataset: Alizadehsani, R., Roshanzamir, M., & Sani, Z. (2013). *extention of Z-Alizadeh sani dataset*. UCI Machine Learning Repository, DOI [10.24432/C5461K](https://doi.org/10.24432/C5461K), CC BY 4.0. Source entry: <https://archive.ics.uci.edu/dataset/411/extention%2Bof%2Bz%2B>.
- Three.js 0.180.0, MIT License; runtime modules are bundled under `app/static/vendor/`, with copyright/license headers preserved. Source: <https://github.com/mrdoob/three.js>.
- No external anatomical mesh or image is used. The procedural heart/artery drawing is original schematic code and is not anatomically precise.
- AI disclosure: OpenAI Codex was used to assist with code, model workflow, interface, testing and documentation. The entrant must understand and be able to explain the submitted work. Disclose OpenAI Codex in the Devpost “Built With” field as well as here.
