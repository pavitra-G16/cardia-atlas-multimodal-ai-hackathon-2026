from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, Image, PageBreak, KeepTogether, HRFlowable)

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/cardia_atlas_report.pdf'
E=json.loads((ROOT/'artifacts/evaluation.json').read_text())
A=json.loads((ROOT/'artifacts/data_audit.json').read_text())

# Actual outer-fold ROC-AUC means and SDs from the saved experiment JSON.
labels=['CAD','LAD','LCX','RCA']
means=[E['targets'][k]['outer_fold_mean_sd']['roc_auc']['mean'] for k in labels]
sds=[E['targets'][k]['outer_fold_mean_sd']['roc_auc']['sd'] for k in labels]
fig,(ax,calax)=plt.subplots(1,2,figsize=(7.1,2.55),dpi=200,gridspec_kw={'width_ratios':[1.05,1.25]})
barcols=['#76b89e','#76b89e','#d7a45d','#d7a45d']
ax.bar(labels,means,yerr=sds,capsize=4,color=barcols,edgecolor='#233b34',linewidth=.6)
ax.axhline(.5,color='#7c8d91',linestyle='--',linewidth=.8)
ax.set_ylim(.45,1.02);ax.set_ylabel('ROC-AUC (outer-fold mean ± SD)',fontsize=8,color='#33444b')
ax.set_title('Nested repeated 5-fold validation',fontsize=9,color='#1c292d',pad=8)
ax.tick_params(axis='both',labelsize=8,colors='#3b4a4e');ax.grid(axis='y',alpha=.18)
for spine in ['top','right']:ax.spines[spine].set_visible(False)
calax.plot([0,1],[0,1],color='#7c8d91',linestyle='--',linewidth=.8,label='Ideal')
for key,color in zip(labels,barcols):
    bins=[b for b in E['targets'][key]['reliability_bins_5'] if b['count']>0]
    if bins:calax.plot([b['mean_predicted_probability'] for b in bins],[b['observed_positive_rate'] for b in bins],marker='o',markersize=3,linewidth=1,label=key,color=color)
calax.set_xlim(0,1);calax.set_ylim(0,1);calax.set_xlabel('Mean predicted probability',fontsize=7,color='#33444b')
calax.set_ylabel('Observed positive rate',fontsize=7,color='#33444b');calax.set_title('Reliability · 5 fixed bins',fontsize=9,color='#1c292d',pad=8)
calax.tick_params(axis='both',labelsize=7,colors='#3b4a4e');calax.grid(alpha=.18);calax.legend(fontsize=6,frameon=False,loc='upper left',ncol=2)
for spine in ['top','right']:calax.spines[spine].set_visible(False)
fig.tight_layout()
chart=ROOT/'reports/outer_cv_roc_auc.png';fig.savefig(chart,bbox_inches='tight',facecolor='white');plt.close(fig)

styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleX',parent=styles['Title'],fontName='Helvetica-Bold',fontSize=24,leading=27,textColor=colors.HexColor('#17352d'),spaceAfter=4))
styles.add(ParagraphStyle(name='SubX',parent=styles['Normal'],fontName='Helvetica',fontSize=10,leading=14,textColor=colors.HexColor('#58686d'),spaceAfter=8))
styles.add(ParagraphStyle(name='H1X',parent=styles['Heading1'],fontName='Helvetica-Bold',fontSize=15,leading=18,textColor=colors.HexColor('#17352d'),spaceBefore=4,spaceAfter=7))
styles.add(ParagraphStyle(name='H2X',parent=styles['Heading2'],fontName='Helvetica-Bold',fontSize=10.5,leading=13,textColor=colors.HexColor('#235644'),spaceBefore=8,spaceAfter=4))
styles.add(ParagraphStyle(name='BodyX',parent=styles['BodyText'],fontName='Helvetica',fontSize=8.4,leading=11.2,textColor=colors.HexColor('#26383e'),spaceAfter=6))
styles.add(ParagraphStyle(name='SmallX',parent=styles['BodyText'],fontName='Helvetica',fontSize=7.2,leading=9.3,textColor=colors.HexColor('#526267'),spaceAfter=3))
styles.add(ParagraphStyle(name='CaptionX',parent=styles['BodyText'],fontName='Helvetica-Oblique',fontSize=7,leading=8.5,textColor=colors.HexColor('#627175'),alignment=TA_CENTER,spaceBefore=4,spaceAfter=6))
styles.add(ParagraphStyle(name='CalloutX',parent=styles['BodyText'],fontName='Helvetica-Bold',fontSize=9,leading=12,textColor=colors.HexColor('#7c4238'),backColor=colors.HexColor('#fbf1e9'),borderColor=colors.HexColor('#ddbd9d'),borderWidth=.5,borderPadding=7,spaceBefore=5,spaceAfter=8))
styles.add(ParagraphStyle(name='CellX',parent=styles['BodyText'],fontName='Helvetica',fontSize=6.3,leading=7.5,textColor=colors.HexColor('#26383e')))
styles.add(ParagraphStyle(name='CellHeadX',parent=styles['BodyText'],fontName='Helvetica-Bold',fontSize=6.1,leading=7,textColor=colors.white))


def P(txt,style='BodyX'):return Paragraph(txt,styles[style])
def fmt(m):return f"{m['mean']:.2f} ± {m['sd']:.2f}"
def header_footer(canvas,doc):
    canvas.saveState();w,h=letter
    canvas.setStrokeColor(colors.HexColor('#d5dfda'));canvas.setLineWidth(.5)
    canvas.line(.65*inch,h-.43*inch,w-.65*inch,h-.43*inch)
    canvas.setFont('Helvetica',7);canvas.setFillColor(colors.HexColor('#637378'))
    canvas.drawString(.65*inch,h-.34*inch,'CARDIA ATLAS  |  TRACK A')
    canvas.drawRightString(w-.65*inch,h-.34*inch,'Multimodal AI Hackathon 2026')
    canvas.line(.65*inch,.42*inch,w-.65*inch,.42*inch)
    canvas.drawString(.65*inch,.27*inch,'Educational research prototype · not for clinical use')
    canvas.drawRightString(w-.65*inch,.27*inch,f'{doc.page}')
    canvas.restoreState()

story=[]
story += [Spacer(1,12),P('Cardia Atlas','TitleX'),P('Cardiovascular Risk Visualization & Prediction  ·  Track A','SubX'),
  P('Developed by Pavitra Gangwar','SmallX'),
  HRFlowable(width='100%',thickness=1,color=colors.HexColor('#a8c8b7'),spaceBefore=2,spaceAfter=13),
  P('<b>Project summary.</b> Cardia Atlas is a local browser application for estimating overall coronary artery disease (CAD) and LAD, LCX, and RCA stenosis probabilities from clinical, examination, ECG, laboratory, and echocardiographic features. It integrates four trained model pipelines, patient-specific SHAP explanations, and an interactive original 3D coronary schematic.'),
  P('The application is an educational decision-support prototype. It is not a diagnosis, a validated clinical risk calculator, or a substitute for clinical assessment or diagnostic imaging. Model probabilities are not measured stenosis percentages or lesion locations.','CalloutX'),
  P('What is implemented','H2X'),
  P('A responsive web interface accepts known clinical inputs and permits blank fields; fitted imputers handle unavailable entries. A local FastAPI backend returns four model probabilities and approximate SHAP contributions. The Three.js view supports rotation, zoom, and vessel selection. Performance and limitations are visible in the application and in this report.'),
  P('Key data and validation facts','H2X')]
keydata=[
 [P('<b>303</b><br/>records','CellX'),P('<b>54</b><br/>predictors','CellX'),P('<b>4</b><br/>predicted outcomes','CellX'),P('<b>2×</b><br/>outer CV repeats','CellX')],
 [P('UCI primary sheet','CellX'),P('after target + constant exclusions','CellX'),P('CAD, LAD, LCX, RCA','CellX'),P('5-fold outer validation','CellX')]]
t=Table(keydata,colWidths=[1.29*inch]*4,rowHeights=[.43*inch,.34*inch])
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#edf4f0')),('BACKGROUND',(0,1),(-1,-1),colors.HexColor('#f8faf8')),('BOX',(0,0),(-1,-1),.6,colors.HexColor('#c9d9d1')),('INNERGRID',(0,0),(-1,-1),.4,colors.HexColor('#d5dfda')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('ALIGN',(0,0),(-1,-1),'CENTER'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5)]))
story += [t,Spacer(1,8),P('Project name: Cardia Atlas · Built from a fresh workspace. The attached Track A brief controls track requirements. Event-level submission details that were not published in the materials reviewed are listed in the submission checklist.','SmallX'),PageBreak()]

story += [Spacer(1,6),P('Data, targets & leakage controls','H1X'),
 P(f"The primary sheet of the official UCI Extension of Z-Alizadeh Sani workbook contains <b>{A['n_rows']} records and {A['n_columns']} columns</b>. UCI describes CAD as at least 50% diameter narrowing; CAD is associated with one or more stenotic LAD, LCX, or RCA labels. The positive targets here are Cath=CAD and each vessel=Stenotic."),
 P('Observed source target balance','H2X')]
data=[['Outcome','Positive','Negative','Source encoding']]
for k,col,pos,neg in [('CAD','Cath','CAD','Normal'),('LAD','LAD','Stenotic','Normal'),('LCX','LCX','Stenotic','Normal'),('RCA','RCA','Stenotic','Normal')]:
 vc=A['target_distributions'][col];data.append([k,str(vc.get(pos,0)),str(vc.get(neg,0)),f'{pos} / {neg}'])
t=Table([[P(str(c),'CellHeadX') for c in data[0]]]+[[P(str(c),'CellX') for c in row] for row in data[1:]],colWidths=[1.05*inch,.75*inch,.75*inch,2.6*inch])
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#245948')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f2f6f3')]),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#cad7d1')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]));story += [t,Spacer(1,5),
 P('Audit results: zero missing values, zero exact duplicate rows, no row identifier in the primary sheet. There are 55 non-target fields before removing one invariant field; the resulting schema contains 54 predictors. The four target fields Cath, LAD, LCX, and RCA are explicitly excluded from all four predictor matrices. No target values enter preprocessing, model fitting, or SHAP backgrounds.'),
 P('Leakage and preprocessing decisions','H2X'),
 P('The 303 observed `Exertional CP` values are all N, so this constant input was removed. The source value `Fmale` was normalized to `Female`; no row was removed or relabeled. The source CAD label was retained as supplied: 302/303 Cath labels agree with the logical OR of vessel labels, leaving one internal inconsistency documented in the audit. Clinical, ECG, laboratory, and echo fields described by the brief were otherwise kept, including Region RWMA as an echocardiographic input, not a lesion coordinate.'),
 P('For each fold, median/mode imputers, one-hot category encoding, and numeric scaling are fit only on the training partition. The source has no missing values, but the local form accepts blanks and uses these training-fitted imputers. No resampling or feature selection is used. Numeric UI values are limited to observed source ranges; UCI does not specify units for many variables, so units are not guessed.'),
 P('Dataset citation: Alizadehsani, R., Roshanzamir, M., & Sani, Z. (2013). <i>extention of Z-Alizadeh sani dataset</i>. UCI Machine Learning Repository. DOI 10.24432/C5461K; CC BY 4.0.','SmallX'),PageBreak()]

story += [Spacer(1,6),P('Model selection & evaluation','H1X'),
 P('Three fixed pipeline families were compared: regularized Logistic Regression (balanced class weights), Extra Trees, and Random Forest. Nested repeated stratified 5-fold outer validation (two repeats) estimates performance. In each outer training partition, 3-fold ROC-AUC selects among the families; the held-out outer fold provides the estimate. The 0.50 threshold is fixed, not optimized. The final pipeline family is chosen separately via 5-fold ROC-AUC on all records and then refit on all records. This final refit has no independent holdout.'),
 P('Outer-fold performance (mean ± standard deviation)','H2X')]
cols=['Outcome','Deploy<br/>family','Acc.','Prec.','Sens.','Spec.','F1','ROC<br/>AUC','PR<br/>AUC','Brier','ECE']
rows=[[P(c,'CellHeadX') for c in cols]]
for k in labels:
 r=E['targets'][k];m=r['outer_fold_mean_sd']
 rows.append([P(k,'CellX'),P(r['selected_final_model'].replace('LogisticRegression','Logistic<br/>regression'),'CellX'),
   P(fmt(m['accuracy']),'CellX'),P(fmt(m['precision']),'CellX'),P(fmt(m['recall_sensitivity']),'CellX'),P(fmt(m['specificity']),'CellX'),P(fmt(m['f1']),'CellX'),P(fmt(m['roc_auc']),'CellX'),P(fmt(m['pr_auc_average_precision']),'CellX'),P(fmt(m['brier_score']),'CellX'),P(fmt(m['expected_calibration_error_5_bins']),'CellX')])
widths=[.52*inch,.76*inch]+[.61*inch]*9
mt=Table(rows,colWidths=widths,repeatRows=1)
mt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#245948')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f2f6f3')]),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#cad7d1')),('ALIGN',(2,1),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),2),('RIGHTPADDING',(0,0),(-1,-1),2),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
story += [mt,Spacer(1,4),P('Sensitivity = recall; PR-AUC = average precision; ECE = 5-bin expected calibration error. Brier scores and ECE summarize probability reliability but do not validate calibration. Pooled held-out confusion counts (TN/FP/FN/TP, two out-of-fold repeats per record): CAD 140/34/52/380; LAD 175/77/62/292; LCX 277/91/88/150; RCA 269/109/102/126.','SmallX'),
 Image(str(chart),width=6.55*inch,height=2.36*inch),P('Figure 1. Left: ROC-AUC outer-fold means and SD from saved nested-CV results; error bars are fold-to-fold SD, not confidence intervals. Right: five-bin reliability from pooled outer-fold predictions; bin counts and small cohort make this a descriptive check, not calibration validation.','CaptionX'),
 P('CAD performed best in these internal estimates. Vessel-specific results are weaker, especially LCX/RCA, with notable fold variability. The sample is small and targets imbalanced; model family selection can still create optimism despite the nested outer design. No external cohort was available.','SmallX'),PageBreak()]

story += [Spacer(1,6),P('Patient explanations & 3D visualization','H1X'),
 P('After a user selects known clinical fields, the local API returns four positive-class probabilities and one explanation per target. The selected family in the final artifact is CAD Extra Trees, LAD Random Forest, LCX Random Forest, and RCA Logistic Regression. It was selected from all-data 5-fold ROC-AUC comparison and refit on all 303 records.'),
 P('SHAP explains the actual fitted preprocessing-plus-estimator path: a fixed background of 24 source rows, six permutation cycles, and one-hot contributions summed back to their source feature. The displayed baseline and contributions use predicted-probability units. The API checks additivity; the browser smoke run observed a zero displayed discrepancy to four decimal percentage points. Finite permutations can vary, and correlated clinical variables complicate attribution. Contributions describe model associations, not causal effects.'),
 P('Interactive schematic view','H2X')]
img=Image(str(ROOT/'submission/assets/cardia-atlas-3d-canvas.png'),width=6.55*inch,height=6.55*inch*342/658)
story += [img,P('Figure 2. Actual Three.js application canvas from the synthetic demo mode. The original procedural heart/torso and artery paths are schematic, not a medical mesh. The example profile is feature-wise median/mode input, not an actual patient. Vessel colors show model probabilities only.','CaptionX'),
 P('The anterior view routes RCA on viewer-left (patient-right), LAD centrally, and LCX toward viewer-right, consistent with the broad vessel names in the official Track A brief and NHLBI overview. Drag rotates; wheel or pinch zooms; artery markers, labels, and result cards select a vessel and its explanation. Bands are illustrative: under 33% lower, 33 to under 67% middle, and 67% or more higher. The drawing does not place a measured stenosis on anatomy.'),
 P('The form groups demographic, history/examination, ECG, and laboratory/echo features, displays source-observed numeric ranges, offers source-coded categorical choices, and accepts missing fields. It clearly identifies synthetic demonstration values. The UI includes a visible educational safety disclaimer, model performance, and limitations.'),PageBreak()]

story += [Spacer(1,6),P('Architecture, verification & limits','H1X'),
 P('The browser application is plain JavaScript with bundled Three.js 0.180.0. A FastAPI service validates the prediction contract and returns predictions and SHAP values. Four scikit-learn pipelines serialize preprocessing with each estimator. A health endpoint checks model presence; schema and performance endpoints serve the exact fit-time feature definition and saved experiment JSON. The original schematic is procedurally generated; no external anatomical mesh, image, paid service, or API key is used.'),
 P('Checks completed','H2X'),
 P('Automated unit tests: 4 passed. Verified source dimensions, class balance, missingness, duplicates, CAD/vessel consistency, target-leakage exclusions, 54-field schema, all four saved models, serialization/reload prediction equivalence. Integrated local API: health/schema/performance endpoints, valid synthetic demo predictions, all-fields-missing imputation, invalid-category HTTP 422, and friendly missing-artifact HTTP 503. SHAP: positive-class output, feature mapping, and baseline-plus-contributions additivity checked. Browser: Three.js WebGL canvas rendered; input/result flow and vessel-card explanation selection were exercised; mobile-size layout inspected.'),
 P('Not verified','H2X'),
 P('Container build/start was not run because a container engine was unavailable in the environment. Cross-browser compatibility, GPU-free speed on other devices, accessibility audit, clinical review, clinical probability calibration validation or recalibration, external/temporal evaluation, and a recorded YouTube video were not completed. Descriptive Brier, five-bin ECE, and reliability checks were computed on outer-fold predictions. Automated browser headless screenshot capture was blocked by the environment; the included 3D canvas image was captured from the running browser application.'),
 P('Important limitations','H2X'),
 P('These 303 source records are one small cohort and do not demonstrate performance in other populations or current clinical settings. No independent validation, prospective study, calibration study, fairness analysis, or clinical threshold validation was performed. CAD class balance differs substantially from the vessel targets. The interface blocks values outside the observed source range, but values inside the range can still be invalid or clinically implausible. The schema provides no source units for many inputs. All performance claims are research summaries, not evidence of safety or clinical utility.'),
 P('Source and asset attribution','H2X'),
 P('Dataset: Alizadehsani R, Roshanzamir M, Sani Z. (2013). UCI Machine Learning Repository, DOI 10.24432/C5461K, CC BY 4.0. Anatomy labels: NHLBI, “How the Heart Works: How Blood Flows through the Heart,” nhlbi.nih.gov/health/heart/blood-flow. SHAP method: official SHAP documentation, shap.readthedocs.io. Three.js 0.180.0, MIT License, github.com/mrdoob/three.js; original library headers are retained. Schematic heart and vessels are original code, not anatomically precise. OpenAI Codex assisted implementation, model workflow, interface, checks and documentation; this is disclosed in the README and must be entered in Devpost Built With.'),
 P('Track A source: participant-provided four-page Track A brief. Event deadline checked on official Devpost: 15 October 2026, 12:15 AM IST. Report length: 5 pages (limit: 6). Demo video duration required by the brief: 3–10 minutes; a timed script is included separately.','SmallX')]

doc=SimpleDocTemplate(str(OUT),pagesize=letter,rightMargin=.65*inch,leftMargin=.65*inch,topMargin=.62*inch,bottomMargin=.58*inch,title='Cardia Atlas - Track A Report',author='Cardia Atlas project team')
doc.build(story,onFirstPage=header_footer,onLaterPages=header_footer)
print(f'Wrote {OUT}')
