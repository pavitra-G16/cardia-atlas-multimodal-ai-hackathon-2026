import * as THREE from './vendor/three.module.js';
import { OrbitControls } from './vendor/OrbitControls.js';

const state={schema:null,example:null,result:null,selected:'CAD',scene:null,camera:null,renderer:null,controls:null,arteries:{},labels:{},raycaster:new THREE.Raycaster(),pointer:new THREE.Vector2()};
const $=id=>document.getElementById(id);
const vesselLabels={LAD:'LAD · anterior descending',LCX:'LCX · circumflex',RCA:'RCA · right coronary'};
const targetNames={CAD:'Overall CAD',LAD:'LAD',LCX:'LCX',RCA:'RCA'};
const colors={low:0x69c69a,moderate:0xe5b66c,high:0xee7270,neutral:0x779096};
function riskColor(p){return p<.33?colors.low:p<.67?colors.moderate:colors.high}
function hexColor(n){return `#${n.toString(16).padStart(6,'0')}`}
function esc(s){return String(s).replace(/[&<>"']/g,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[x]))}

async function init(){
  try{
    const [s,e,p]=await Promise.all([fetch('/api/schema'),fetch('/api/example'),fetch('/api/performance')]);
    const failed=[s,e,p].find(x=>!x.ok);if(failed){let detail='The local API did not return its setup files.';try{detail=(await failed.json()).detail||detail}catch{}throw new Error(detail)}
    state.schema=await s.json();state.example=await e.json();const perf=await p.json();
    renderForm();renderPerformance(perf);mountThree();await loadExample(false);
  }catch(err){showError(err.message||String(err));$('analysis-state').innerHTML='<i></i> API unavailable';}
  $('clinical-form').addEventListener('submit',onSubmit);
  $('load-example').addEventListener('click',()=>loadExample(true));
  $('clear-form').addEventListener('click',clearForm);
  $('explain-target').addEventListener('change',e=>{state.selected=e.target.value;renderExplanation()});
  $('reset-view').addEventListener('click',()=>{if(state.controls){state.controls.reset();state.camera.position.set(0,0,5.3)}});
  if(new URLSearchParams(location.search).get('demo')==='1'){
    await loadExample(false);
    await onSubmit({preventDefault(){}});
  }
}
function renderForm(){
  const groups=state.schema.fields.reduce((a,f)=>((a[f.group]??=[]).push(f),a),{});
  $('field-count').textContent=`${state.schema.fields.length} predictors`;
  $('field-groups').innerHTML=Object.entries(groups).map(([group,fields],i)=>`<details class="field-group" ${i<2?'open':''}><summary>${esc(group)} <span>${fields.length} fields</span></summary><div class="fields">${fields.map(renderField).join('')}</div></details>`).join('');
  document.querySelectorAll('#clinical-form input,#clinical-form select').forEach(el=>el.addEventListener('input',()=>delete el.dataset.demoExact));
}
function renderField(f){
  let input='';
  if(f.type==='select'||f.type==='coded_select'){
    input=`<select name="${esc(f.name)}"><option value="">Not provided</option>${f.options.map(x=>`<option value="${esc(x.value)}">${esc(x.label)}</option>`).join('')}</select>`;
  }else{
    const step=f.step==='any'?'any':f.step;
    input=`<input name="${esc(f.name)}" type="number" step="${step}" min="${f.min}" max="${f.max}" placeholder="${Number.isInteger(f.median)?f.median:f.median.toFixed(2)}">`;
  }
  const showRange=x=>Number.isInteger(Number(x))?String(x):Number(x).toFixed(2);
  let hint=f.type==='number'?`Source range ${showRange(f.min)}–${showRange(f.max)}; units unspecified.`:f.type==='coded_select'?'Source-coded value; meaning not defined in the dataset metadata.':'Blank is allowed.';
  return `<div class="field"><label for="f-${esc(f.name)}">${esc(f.label)}</label>${input.replace(`name="${esc(f.name)}"`,`id="f-${esc(f.name)}" name="${esc(f.name)}"`)}<small>${esc(hint)}</small></div>`;
}
async function loadExample(show=true){
  for(const [key,value] of Object.entries(state.example.values||{})){
    const input=document.querySelector(`[name="${CSS.escape(key)}"]`);if(input){const field=state.schema.fields.find(f=>f.name===key);input.dataset.demoExact=String(value);input.value=field?.name==='BMI'?Number(value).toFixed(1):(field?.type==='number'&&field?.step==='any'?Number(value).toFixed(2):value)}
  }
  $('example-note').textContent=state.example.label||'Synthetic demonstration values only.';
  if(show){$('example-note').classList.add('flash');setTimeout(()=>$('example-note').classList.remove('flash'),800)}
}
function clearForm(){document.querySelectorAll('#clinical-form input,#clinical-form select').forEach(x=>{x.value='';delete x.dataset.demoExact});$('example-note').textContent='All fields cleared. Blank fields will be imputed by the fitted pipeline.';state.result=null;$('result-content').classList.add('hidden');$('results-empty').classList.remove('hidden');$('analysis-state').innerHTML='<i></i> Awaiting inputs';setArteryProbabilities(null)}
async function onSubmit(e){
  e.preventDefault();clearError();const button=$('predict');button.disabled=true;button.innerHTML='<span>Calculating models & explanations…</span><span class="spinner"></span>';$('analysis-state').className='status-badge waiting';$('analysis-state').innerHTML='<i></i> Computing';
  try{
    const values={};for(const f of state.schema.fields){const el=document.querySelector(`[name="${CSS.escape(f.name)}"]`);let v=el?.dataset.demoExact??el?.value??'';values[f.name]=v===''?null:(f.type==='number'||f.type==='coded_select'?Number(v):v)}
    const res=await fetch('/api/predict',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({values})});
    const payload=await res.json();if(!res.ok)throw new Error(payload.detail||`Request failed (${res.status})`);
    state.result=payload;state.selected='CAD';renderResults();$('analysis-state').className='status-badge ready';$('analysis-state').innerHTML='<i></i> Analysis complete';
  }catch(err){showError(err.message||String(err));$('analysis-state').className='status-badge';$('analysis-state').innerHTML='<i></i> Could not analyze'}
  finally{button.disabled=false;button.innerHTML='<span>Generate analysis</span><span aria-hidden="true">→</span>'}
}
function renderResults(){
  $('results-empty').classList.add('hidden');$('result-content').classList.remove('hidden');
  const preds=state.result.predictions;
  $('prediction-cards').innerHTML=Object.entries(preds).map(([key,d])=>`<button class="prediction-card ${key===state.selected?'selected':''}" data-target="${key}"><span class="name">${targetNames[key].toUpperCase()}</span><div class="prob" style="color:${hexColor(riskColor(d.probability))}">${(d.probability*100).toFixed(1)}%</div><span class="class">${d.predicted_class==='positive'?'Model positive':'Model negative'} · ${esc(d.model)}</span><div class="meter"><i style="width:${d.probability*100}%;background:${hexColor(riskColor(d.probability))}"></i></div></button>`).join('');
  document.querySelectorAll('.prediction-card').forEach(el=>el.addEventListener('click',()=>selectTarget(el.dataset.target)));
  $('explain-target').innerHTML=Object.keys(preds).map(k=>`<option value="${k}">${targetNames[k]}</option>`).join('');$('explain-target').value=state.selected;
  setArteryProbabilities(preds);renderVessels(preds);renderExplanation();
}
function selectTarget(t){state.selected=t;$('explain-target').value=t;document.querySelectorAll('.prediction-card').forEach(x=>x.classList.toggle('selected',x.dataset.target===t));document.querySelectorAll('.vessel-item').forEach(x=>x.classList.toggle('active',x.dataset.target===t));renderExplanation()}
function renderVessels(preds){
  $('vessel-list').innerHTML=['LAD','LCX','RCA'].map(k=>{const p=preds[k].probability;return `<button class="vessel-item ${state.selected===k?'active':''}" data-target="${k}"><span class="v-name"><i class="vessel-dot" style="background:${hexColor(riskColor(p))}"></i>${k}</span><div class="v-prob" style="color:${hexColor(riskColor(p))}">${(p*100).toFixed(1)}%</div><div class="v-caption">predicted probability</div></button>`}).join('');
  document.querySelectorAll('.vessel-item').forEach(el=>el.addEventListener('click',()=>selectTarget(el.dataset.target)));
}
function renderExplanation(){
  if(!state.result)return;const key=state.selected,exp=state.result.explanations[key];if(!exp)return;
  $('baseline-line').textContent=`${targetNames[key]} estimate ${(exp.prediction_probability*100).toFixed(1)}%  ·  Background baseline ${(exp.baseline_probability*100).toFixed(1)}%  ·  Additivity difference ${(exp.additivity_error*100).toFixed(3)} percentage points`;
  const vals=exp.contributions||[],max=Math.max(...vals.map(x=>Math.abs(x.value)),.0001);
  $('shap-bars').innerHTML=vals.map(x=>{const width=Math.max(2,Math.abs(x.value)/max*47);const feature=state.schema.fields.find(f=>f.name===x.feature);const patientValue=x.input===null?'Blank → imputed':(typeof x.input==='number'?Number(x.input).toLocaleString(undefined,{maximumFractionDigits:2}):String(x.input));const unit=feature?.unit&& !feature.unit.includes('does not specify')?feature.unit:'';return `<div class="shap-row"><span class="shap-label" title="${esc(x.feature)}">${esc(feature?.label||x.feature)}</span><span class="shap-patient-value" title="Input value from this analysis">${esc(patientValue)}${unit?` ${esc(unit)}`:''}</span><div class="shap-track"><i class="shap-zero"></i><i class="shap-fill ${x.value>=0?'pos':'neg'}" style="width:${width}%"></i></div><span class="shap-value">${x.value>=0?'+':''}${(x.value*100).toFixed(2)} pp</span></div>`}).join('');
}
function setArteryProbabilities(preds){
  for(const [key,obj] of Object.entries(state.arteries)){const p=preds?.[key]?.probability;const color=p==null?colors.neutral:riskColor(p);obj.material.color.setHex(color);obj.material.emissive.setHex(color);obj.material.emissiveIntensity=.18;obj.children?.forEach?.(c=>c.material?.color?.setHex(color))}
  if(state.scene){state.scene.traverse(o=>{if(o.userData.vessel){const p=preds?.[o.userData.vessel]?.probability,c=p==null?colors.neutral:riskColor(p);if(o.material?.color)o.material.color.setHex(c)}})}
}
function renderPerformance(report){
  const show=x=>`${x.mean.toFixed(2)} ± ${x.sd.toFixed(2)}`;
  const order=['CAD','LAD','LCX','RCA'];$('performance-grid').innerHTML=order.map(k=>{const r=report.targets[k],m=r.outer_fold_mean_sd;return `<article class="metric-card"><div class="metric-title">${targetNames[k].toUpperCase()}</div><div class="metric-model">${esc(r.selected_final_model)} · fixed threshold 0.50</div><div class="metric-pairs"><span><b>${show(m.accuracy)}</b><small>Accuracy · mean ± SD</small></span><span><b>${show(m.precision)}</b><small>Precision · mean ± SD</small></span><span><b>${show(m.recall_sensitivity)}</b><small>Recall · mean ± SD</small></span><span><b>${show(m.f1)}</b><small>F1 score · mean ± SD</small></span><span><b>${show(m.roc_auc)}</b><small>ROC-AUC · mean ± SD</small></span><span><b>${show(m.specificity)}</b><small>Specificity · mean ± SD</small></span></div></article>`}).join('');
  $('method-note').textContent=`${report.validation} ${report.predictor_count} predictors, 303 records. Threshold 0.50 was fixed before evaluation; no threshold optimization. The repeat-fold summaries are internal estimates, not independent validation.`;
}
function showError(message){$('error-box').textContent=message;$('error-box').classList.remove('hidden')}
function clearError(){$('error-box').classList.add('hidden');$('error-box').textContent=''}

function mountThree(){
  const canvas=$('heart-canvas'),wrap=$('canvas-wrap');
  const scene=new THREE.Scene();scene.background=new THREE.Color('#101b21');
  const camera=new THREE.PerspectiveCamera(39,1,.1,100);camera.position.set(0,0,5.2);
  const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:false});renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.12;
  const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.06;controls.minDistance=3.7;controls.maxDistance=7.6;controls.maxPolarAngle=Math.PI*.78;
  scene.add(new THREE.HemisphereLight(0xbde5dd,0x203039,2.0));const key=new THREE.DirectionalLight(0xffddd0,3);key.position.set(-2,3,5);scene.add(key);const rim=new THREE.DirectionalLight(0x7cd7cb,1.8);rim.position.set(2,1,-2);scene.add(rim);
  const group=new THREE.Group();scene.add(group);
  const torsoMat=new THREE.MeshStandardMaterial({color:0x49636a,roughness:.82,metalness:.04,transparent:true,opacity:.22,side:THREE.DoubleSide});
  const chest=new THREE.Mesh(new THREE.SphereGeometry(1,32,24),torsoMat);chest.scale.set(1.15,1.5,.27);chest.position.set(0,-.02,-.62);group.add(chest);
  for(const x of [-.7,.7]){const shoulder=new THREE.Mesh(new THREE.SphereGeometry(1,24,16),torsoMat);shoulder.scale.set(.62,.42,.28);shoulder.position.set(x,.95,-.58);group.add(shoulder)}
  const neck=new THREE.Mesh(new THREE.CylinderGeometry(.22,.27,.48,20),torsoMat);neck.position.set(0,1.65,-.58);group.add(neck);
  // An original, schematic heart silhouette generated from a parametric 2D outline; not a licensed anatomical mesh.
  const heartShape=new THREE.Shape();let first=true;
  for(let i=0;i<=120;i++){const t=i/120*Math.PI*2;const x=16*Math.pow(Math.sin(t),3)*.064;const y=(13*Math.cos(t)-5*Math.cos(2*t)-2*Math.cos(3*t)-Math.cos(4*t))*.064;if(first){heartShape.moveTo(x,y);first=false}else heartShape.lineTo(x,y)}heartShape.closePath();
  const heartGeom=new THREE.ExtrudeGeometry(heartShape,{depth:.28,bevelEnabled:true,bevelSegments:4,steps:1,bevelSize:.09,bevelThickness:.08});heartGeom.center();
  const heart=new THREE.Mesh(heartGeom,new THREE.MeshStandardMaterial({color:0x8a4e53,roughness:.45,metalness:.06,emissive:0x2e1118,emissiveIntensity:.4}));heart.scale.set(.92,.96,.9);heart.position.set(0,-.03,.04);group.add(heart);
  const aorta=new THREE.Mesh(new THREE.TorusGeometry(.34,.09,12,40,Math.PI*1.6),new THREE.MeshStandardMaterial({color:0xb97370,roughness:.42,metalness:.05}));aorta.rotation.z=Math.PI*.04;aorta.position.set(.07,.73,-.04);group.add(aorta);
  addTube('RCA',[[-.17,.55,.34],[-.38,.42,.36],[-.59,.19,.34],[-.6,-.15,.3],[-.42,-.45,.31],[-.13,-.58,.34]],colors.neutral,group);
  addTube('LAD',[[.02,.54,.36],[.08,.31,.38],[.12,.03,.39],[.04,-.27,.36],[-.02,-.55,.32]],colors.neutral,group);
  addTube('LCX',[[.14,.52,.34],[.36,.43,.37],[.58,.25,.33],[.62,.02,.29],[.46,-.18,.3],[.25,-.27,.31]],colors.neutral,group);
  // Faint anterior orientation marks; positional anatomy is schematic only.
  const seam=new THREE.Mesh(new THREE.TorusGeometry(.28,.012,6,32,Math.PI),new THREE.MeshBasicMaterial({color:0xe3b3a5,transparent:true,opacity:.36}));seam.position.set(0,-.13,.24);seam.rotation.z=Math.PI;group.add(seam);
  state.scene=scene;state.camera=camera;state.renderer=renderer;state.controls=controls;
  const resize=()=>{const r=wrap.getBoundingClientRect();renderer.setSize(r.width,r.height,false);camera.aspect=r.width/r.height;camera.updateProjectionMatrix()};new ResizeObserver(resize).observe(wrap);resize();
  renderer.domElement.addEventListener('pointerdown',onCanvasPick);
  const animate=()=>{requestAnimationFrame(animate);controls.update();scene.updateMatrixWorld(true);updateVesselLabels();renderer.render(scene,camera)};animate();
}
function addTube(key,points,color,group){
  const curve=new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p)));const mesh=new THREE.Mesh(new THREE.TubeGeometry(curve,64,.033,10,false),new THREE.MeshStandardMaterial({color,roughness:.32,metalness:.14,emissive:color,emissiveIntensity:.15}));mesh.userData.vessel=key;mesh.name=`artery-${key}`;group.add(mesh);state.arteries[key]=mesh;
  const p=curve.getPointAt(.53);const marker=new THREE.Mesh(new THREE.SphereGeometry(.08,16,12),new THREE.MeshStandardMaterial({color,emissive:color,emissiveIntensity:.24}));marker.position.copy(p);marker.userData.vessel=key;group.add(marker);
  const el=document.createElement('button');el.className='canvas-label';el.style.pointerEvents='auto';el.textContent=key;el.addEventListener('click',()=>selectTarget(key));$('canvas-labels').append(el);state.labels[key]={element:el,anchor:marker};
}
function updateVesselLabels(){
  const width=state.renderer.domElement.clientWidth,height=state.renderer.domElement.clientHeight;
  for(const {element,anchor} of Object.values(state.labels)){
    const point=anchor.getWorldPosition(new THREE.Vector3()).project(state.camera);
    const visible=point.z>-1&&point.z<1;element.style.display=visible?'block':'none';
    if(visible){element.style.left=`${(point.x*.5+.5)*width}px`;element.style.top=`${(-point.y*.5+.5)*height}px`}
  }
}
function onCanvasPick(event){const r=state.renderer.domElement.getBoundingClientRect();state.pointer.x=((event.clientX-r.left)/r.width)*2-1;state.pointer.y=-((event.clientY-r.top)/r.height)*2+1;state.raycaster.setFromCamera(state.pointer,state.camera);const items=[];state.scene.traverse(o=>{if(o.userData.vessel)items.push(o)});const hit=state.raycaster.intersectObjects(items,false)[0];if(hit?.object?.userData?.vessel)selectTarget(hit.object.userData.vessel)}
init();
