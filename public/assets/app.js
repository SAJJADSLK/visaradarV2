(()=>{
const $=s=>document.querySelector(s),esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const cache=async(url,ttl)=>{const k="vr:"+url;try{const c=JSON.parse(localStorage.getItem(k));if(c&&Date.now()-c.t<ttl)return c.d}catch(_){}
 const r=await fetch(url);if(!r.ok)throw new Error(r.status);const d=await r.json();try{localStorage.setItem(k,JSON.stringify({t:Date.now(),d}))}catch(_){}return d};
const KIND=v=>/^\d+$/.test(v)?"vf":v,
 L={vf:"Visa-free",voa:"Visa on arrival",eta:"Electronic authorisation",ev:"e-Visa",vr:"Visa required",na:"Entry not permitted"},
 W={vf:"No visa is needed for a tourist stay.",voa:"The visa is issued at the border.",eta:"Apply online before you fly.",ev:"Apply for an electronic visa before you travel.",vr:"Apply at an embassy or official portal first.",na:"Entry is currently not permitted."};
// Home lookup
const lk=$("#lookup");
if(lk)cache("/data/rules.json",864e5).then(D=>{
 const f=$("#from"),t=$("#to"),ids=Object.keys(D.n).sort((a,b)=>D.n[a].localeCompare(D.n[b])),opt=c=>`<option value="${c}">${esc(D.n[c])}</option>`;
 f.innerHTML=Object.keys(D.r).sort((a,b)=>D.n[a].localeCompare(D.n[b])).map(opt).join("");t.innerHTML=ids.map(opt).join("");
 let s={};try{s=JSON.parse(localStorage.getItem("vr:sel"))||{}}catch(_){}
 f.value=s.f||"US";t.value=s.t||"JP";
 const go=()=>{try{localStorage.setItem("vr:sel",JSON.stringify({f:f.value,t:t.value}))}catch(_){}
  const v=f.value===t.value?null:D.r[f.value]?.[t.value],o=$("#stamp");
  if(!v){o.innerHTML="<p>Pick two different countries.</p>";return}
  const k=KIND(v);o.innerHTML=`<div class="stamp pop k-${k}"><b>${L[k]}</b>${/^\d+$/.test(v)?`<span>${v} days</span>`:""}</div><div class="why"><p>${W[k]}</p><a href="/passport/${f.value.toLowerCase()}/">All ${esc(D.n[f.value])} passport rules</a><br><a href="/country/${t.value.toLowerCase()}/">Travel to ${esc(D.n[t.value])}</a></div>`};
 f.onchange=t.onchange=go;go()});
// Live destination panel: REST Countries + Open-Meteo + ExchangeRate-API
const live=$("#live");
if(live){const cc=live.dataset.cc,out=$("#facts"),rows=[];const add=(a,b)=>rows.push(`<div class="row"><b>${a}</b><span>${b}</span></div>`),show=()=>out.innerHTML=rows.join("")||"<p class='mute'>Live details are unavailable right now.</p>";
 const WC=c=>c==0?"Clear":c<=3?"Partly cloudy":c<=48?"Fog":c<=57?"Drizzle":c<=67?"Rain":c<=77?"Snow":c<=82?"Showers":"Thunderstorms";
 cache(`https://restcountries.com/v3.1/alpha/${cc}?fields=name,capital,capitalInfo,currencies,languages,idd,timezones,car,flag,population`,6048e5).then(async c=>{
  const cur=Object.entries(c.currencies||{})[0],ll=c.capitalInfo?.latlng;
  add("Capital",esc((c.capital||["—"]).join(", ")));add("Languages",esc(Object.values(c.languages||{}).join(", ")||"—"));
  add("Calling code",esc((c.idd?.root||"")+(c.idd?.suffixes?.length===1?c.idd.suffixes[0]:"")));add("Time zone",esc((c.timezones||[])[0]||"—"));
  add("Drives on the",esc(c.car?.side||"—"));add("Population",(c.population||0).toLocaleString());
  const jobs=[];
  if(ll)jobs.push(cache(`https://api.open-meteo.com/v1/forecast?latitude=${ll[0]}&longitude=${ll[1]}&current=temperature_2m,weather_code&daily=temperature_2m_max,temperature_2m_min&timezone=auto&forecast_days=3`,18e5).then(w=>
   add(`Weather in ${esc(c.capital[0])}`,`${Math.round(w.current.temperature_2m)}°C, ${WC(w.current.weather_code)}. Next 3 days ${Math.round(Math.min(...w.daily.temperature_2m_min))}–${Math.round(Math.max(...w.daily.temperature_2m_max))}°C`)).catch(()=>{}));
  if(cur)jobs.push(cache("https://open.er-api.com/v6/latest/USD",216e5).then(x=>{const r=x.rates[cur[0]];if(r)add("Currency",`${esc(cur[1].name)} (${cur[0]}). 1 USD = ${r.toLocaleString(undefined,{maximumFractionDigits:r>100?0:2})} ${cur[0]}${x.rates.EUR?`, 1 EUR = ${(r/x.rates.EUR).toLocaleString(undefined,{maximumFractionDigits:r>100?0:2})} ${cur[0]}`:""}`)}).catch(()=>{}));
  await Promise.all(jobs);show()}).catch(show)}
})();
document.getElementById("theme")?.addEventListener("click",()=>{const d=document.documentElement,n=d.dataset.theme==="dark"?"light":"dark";d.dataset.theme=n;try{localStorage.setItem("vr:theme",n)}catch(_){}});
(()=>{
const $=s=>document.querySelector(s),J=u=>fetch(u).then(r=>r.json()),esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const K=v=>/^\d+$/.test(v)?"vf":v,L={vf:"Visa-free",voa:"Visa on arrival",eta:"eTA",ev:"e-Visa",vr:"Visa required",na:"No admission"},lab=v=>v===undefined?"—":L[K(v)]+(/^\d+$/.test(v)?" · "+v+" days":"");
const cnt=a=>{const c={vf:0,voa:0,eta:0,ev:0,vr:0,na:0};a.forEach(v=>c[K(v)]++);return c};
const rk=$("#rk");
if(rk){const tb=rk.tBodies[0];$("#flt").oninput=e=>{const q=e.target.value.toLowerCase();[...tb.rows].forEach(r=>r.hidden=!r.cells[1].textContent.toLowerCase().includes(q))};
 rk.tHead.onclick=e=>{const th=e.target.closest("th");if(!th)return;const i=th.cellIndex,d=th.dataset.d=th.dataset.d==="1"?"-1":"1";[...tb.rows].sort((a,b)=>{const x=a.cells[i].textContent,y=b.cells[i].textContent,n=parseFloat(x)-parseFloat(y);return(isNaN(n)?x.localeCompare(y):n)*d}).forEach(r=>tb.append(r))}}
const C=$("[data-cmp]");
if(C)J("/data/rules.json").then(D=>{
 const mode=C.dataset.cmp,sels=[...C.querySelectorAll("select[data-i]")],me=$("#me"),out=$("#out"),nm=c=>D.n[c],opt=c=>`<option value="${c}">${esc(nm(c))}</option>`;
 const ids=Object.keys(mode=="p"?D.r:D.n).sort((a,b)=>nm(a).localeCompare(nm(b))),d0=mode=="p"?["AE","US"]:["JP","TH"];
 sels.forEach((s,i)=>{s.innerHTML=(i>1?'<option value="">None</option>':"")+ids.map(opt).join("");s.value=i<2?d0[i]:"";s.onchange=draw});
 if(me){me.innerHTML='<option value="">Choose your passport</option>'+Object.keys(D.r).sort((a,b)=>nm(a).localeCompare(nm(b))).map(opt).join("");me.onchange=draw}
 const T=(head,rows)=>`<table class="tbl"><thead><tr><th></th>${head.map(h=>`<th>${esc(h)}</th>`).join("")}</tr></thead><tbody>${rows.map(r=>`<tr><th>${r[0]}</th>${r.slice(1).map(c=>`<td>${c}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
 function draw(){const sel=[...new Set(sels.map(s=>s.value).filter(Boolean))];let h="";
  if(mode=="p"){const cs=sel.map(p=>cnt(Object.values(D.r[p])));
   h=T(sel.map(nm),[["Travel freedom score",c=>c.vf+c.voa+c.eta],["Visa-free",c=>c.vf],["Visa on arrival",c=>c.voa],["eTA",c=>c.eta],["e-Visa",c=>c.ev],["Visa required",c=>c.vr+c.na]].map(([t,f])=>[t,...cs.map(f)]));
   if(sel.length>1){const df=Object.keys(D.n).filter(d=>!sel.includes(d)&&new Set(sel.map(p=>K(D.r[p][d]))).size>1);
    h+=`<h2>Where they differ <span class="mute">${df.length}</span></h2>`+(df.length?T(sel.map(nm),df.slice(0,150).map(d=>[`<a href="/country/${d.toLowerCase()}/">${esc(nm(d))}</a>`,...sel.map(p=>lab(D.r[p][d]))]))+(df.length>150?`<p class="mute">Showing the first 150.</p>`:""):"<p>These passports have the same rule everywhere.</p>")}}
  else{const cs=sel.map(d=>cnt(Object.values(D.r).map(r=>r[d]).filter(v=>v!==undefined)));
   h=T(sel.map(nm),[...(me&&me.value?[["Your passport",...sel.map(d=>d===me.value?"Home country":lab(D.r[me.value][d]))]]:[]),...[["Passports entering visa-free, on arrival or with eTA",c=>c.vf+c.voa+c.eta],["Visa-free",c=>c.vf],["Visa on arrival",c=>c.voa],["eTA",c=>c.eta],["e-Visa",c=>c.ev],["Visa required",c=>c.vr+c.na]].map(([t,f])=>[t,...cs.map(f)])])}
  out.innerHTML=sel.length>1?h:"<p>Choose at least two.</p>"}
 draw()});
const M=$("#map");
if(M&&window.d3&&window.topojson)Promise.all([J("/data/rules.json"),J("/data/iso.json"),J("https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json")]).then(([D,I,W])=>{
 const mp=$("#mp"),F=topojson.feature(W,W.objects.countries).features,path=d3.geoPath(d3.geoNaturalEarth1().fitSize([960,500],{type:"FeatureCollection",features:F}));
 mp.innerHTML=Object.keys(D.r).sort((a,b)=>D.n[a].localeCompare(D.n[b])).map(c=>`<option value="${c}">${esc(D.n[c])}</option>`).join("");mp.value="AE";
 const svg=d3.select(M).append("svg").attr("viewBox","0 0 960 500"),ps=svg.selectAll("path").data(F).join("path").attr("d",path).attr("class","cty");
 ps.append("title");
 const draw=()=>{const p=mp.value;ps.each(function(f){const c=I[String(f.id).padStart(3,"0")],v=c&&D.r[p][c],k=c===p?"self":v?K(v):"";this.setAttribute("class","cty"+(k?" m-"+k:""));this.firstChild.textContent=c?`${D.n[c]||c}: ${c===p?"your passport":lab(v)}`:""})};
 mp.onchange=draw;draw()}).catch(()=>M.textContent="The map could not load. Check your connection and refresh.");
})();
(()=>{const SC=document.getElementById("sc");if(!SC)return;
const day=s=>{const[y,m,d]=s.split("-").map(Number);return Date.UTC(y,m-1,d)/864e5},fmt=n=>new Date(n*864e5).toISOString().slice(0,10),T=document.getElementById("trips"),R=document.getElementById("ref"),O=document.getElementById("res");
const win=(set,d)=>{let c=0;for(let k=d-179;k<=d;k++)if(set.has(k))c++;return c};
function calc(){const used=new Set();let err="";T.querySelectorAll(".trip").forEach(r=>{const[a,b]=[...r.querySelectorAll("input")].map(i=>i.value);if(a&&b){const x=day(a),y=day(b);if(y<x)err="An exit date is before its entry date.";else for(let d=x;d<=y;d++)used.add(d)}});
 if(err){O.innerHTML=`<p class="down">${err}</p>`;return}
 const ref=R.value?day(R.value):Math.floor(Date.now()/864e5),u=win(used,ref),s2=new Set(used);let n=0;
 for(let d=ref;d<ref+400;d++){s2.add(d);if(win(s2,d)>90)break;n++}
 O.innerHTML=`<p>Days used in the 180 days ending ${fmt(ref)}: <b>${u}</b> of 90.</p><p>Days left on that date: <b>${Math.max(0,90-u)}</b>.</p><p>${n?`If you enter on ${fmt(ref)}, you can stay up to <b>${n}</b> day${n>1?"s":""}, until ${fmt(ref+n-1)}.`:`You have no days left if you enter on ${fmt(ref)}.`}</p><p class="mute">Entry and exit days both count. Border officers rely on EES records, so use this as a planning guide only.</p>`}
function add(a="",b=""){const r=document.createElement("div");r.className="trip";r.innerHTML=`<label>Entry date<input type="date" value="${a}"></label><label>Exit date<input type="date" value="${b}"></label><button type="button" class="x" aria-label="Remove trip">&times;</button>`;r.querySelector(".x").onclick=()=>{r.remove();calc()};r.querySelectorAll("input").forEach(i=>i.onchange=calc);T.append(r)}
document.getElementById("addT").onclick=()=>add();R.value=fmt(Math.floor(Date.now()/864e5));R.onchange=calc;add();calc()})();
(()=>{
const K=v=>/^\d+$/.test(v)?"vf":v,L={vf:"Visa-free",voa:"Visa on arrival",eta:"eTA",ev:"e-Visa",vr:"Visa required",na:"No admission"},EA={vf:0,voa:1,eta:2,ev:3,vr:4,na:5},esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const lab=v=>L[K(v)]+(/^\d+$/.test(v)?" · "+v+" days":""),rk=v=>EA[K(v)]*1000-(/^\d+$/.test(v)?+v:0);
const T=document.getElementById("trip"),DU=document.getElementById("dual");if(!T&&!DU)return;
fetch("/data/rules.json").then(r=>r.json()).then(D=>{
const nm=c=>D.n[c],srt=o=>Object.keys(o).sort((a,b)=>nm(a).localeCompare(nm(b))),opt=c=>`<option value="${c}">${esc(nm(c))}</option>`;
if(T){const $=s=>T.querySelector(s),SCH=new Set("AT BE BG HR CZ DK EE FI FR DE GR HU IS IT LV LI LT LU MT NL NO PL PT SK SI ES SE CH".split(" "));
 const adv={vf:"No visa needed for a tourist stay.",voa:"Carry the fee and photos.",eta:"Apply online before you fly.",ev:"Apply online before you travel.",vr:"Apply for a visa first.",na:"Entry is currently not permitted."},cls={vf:"up",voa:"up",eta:"mid",ev:"mid",vr:"down",na:"down",home:"up"};
 const tp=$("#tp"),stops=$("#stops"),out=$("#tout"),q=new URLSearchParams(location.search),ids=srt(D.n);
 tp.innerHTML=srt(D.r).map(opt).join("");tp.value=D.r[q.get("p")]?q.get("p"):"AE";
 const add=(v)=>{const r=document.createElement("div");r.className="stop";r.innerHTML=`<select aria-label="Destination">${ids.map(opt).join("")}</select><button type="button" class="x" aria-label="Remove destination">&times;</button>`;const s=r.querySelector("select");s.value=v;s.onchange=draw;r.querySelector(".x").onclick=()=>{r.remove();draw()};stops.append(r)};
 function draw(){const p=tp.value,ds=[...stops.querySelectorAll("select")].map(s=>s.value);try{history.replaceState(null,"",`?p=${p}&d=${ds.join(",")}`)}catch(_){}
  if(!ds.length){out.innerHTML="<p>Add a destination.</p>";return}
  const need=[];let h="";
  ds.forEach((d,i)=>{const v=d===p?null:D.r[p][d],k=v?K(v):"home";if(["eta","ev","vr","na"].includes(k))need.push(d);
   h+=`<a class="row" href="/country/${d.toLowerCase()}/"><span>${i+1}. ${esc(nm(d))}</span><span class="mute">${v?lab(v):"Home country"}</span><span class="${cls[k]}">${v?adv[k]:"No entry rules"}</span></a>`});
  h=`<div class="ledger">${h}</div><p><b>${need.length}</b> of ${ds.length} stops need action before you fly${need.length?": "+need.map(d=>esc(nm(d))).join(", "):""}.</p>`;
  if(ds.filter(d=>SCH.has(d)).length>1)h+=`<p class="note">Your Schengen stops share one 90 days in 180 limit. Use the <a href="/eu/calculator/">calculator</a>.</p>`;
  out.innerHTML=h}
 const want=(q.get("d")||"JP,TH,FR").split(",").filter(c=>D.n[c]);want.slice(0,10).forEach(add);
 $("#addS").onclick=()=>{if(stops.children.length<10){add("JP");draw()}};tp.onchange=draw;
 $("#shr").onclick=e=>{navigator.clipboard&&navigator.clipboard.writeText(location.href).then(()=>e.target.textContent="Link copied")};draw()}
if(DU){const sels=[...DU.querySelectorAll("select")],out=document.getElementById("dout");
 sels.forEach((s,i)=>{s.innerHTML=(i>1?'<option value="">None</option>':"")+srt(D.r).map(opt).join("");s.value=i<2?["AE","IN"][i]:"";s.onchange=draw});
 function draw(){const sel=[...new Set(sels.map(s=>s.value).filter(Boolean))];if(sel.length<2){out.innerHTML="<p>Choose at least two passports.</p>";return}
  const win={},open=c=>["vf","voa","eta"].includes(K(c));sel.forEach(p=>win[p]=[]);let comb=0,diff=0;const each={};sel.forEach(p=>each[p]=Object.values(D.r[p]).filter(open).length);
  Object.keys(D.n).forEach(d=>{if(sel.includes(d))return;const o=sel.map(p=>({p,v:D.r[p][d]})).filter(x=>x.v!==undefined).sort((a,b)=>rk(a.v)-rk(b.v));if(!o.length)return;
   if(open(o[0].v))comb++;if(o.length>1&&rk(o[0].v)<rk(o[1].v)){diff++;win[o[0].p].push([d,o[0].v,o[1].v])}});
  let h=`<p class="lede">Together these passports reach <b>${comb}</b> destinations visa-free, on arrival or with an eTA. ${sel.map(p=>`${esc(nm(p))} alone: ${each[p]}`).join(", ")}.</p><p>In <b>${diff}</b> destinations one passport gives a clearly easier entry.</p>`;
  sel.forEach(p=>{const w=win[p];h+=`<details${w.length?" open":""}><summary>Use ${esc(nm(p))} for ${w.length} destinations</summary><div class="chips">${w.slice(0,120).map(([d,a,b])=>`<a class="chip" href="/country/${d.toLowerCase()}/">${esc(nm(d))}<i>${lab(a)} vs ${lab(b)}</i></a>`).join("")||"<span class='mute'>No destination where this passport is clearly better.</span>"}</div></details>`});
  out.innerHTML=h}
 draw()}
})})();
(()=>{const P=document.getElementById("pv");if(!P)return;
const g=i=>document.getElementById(i).value,day=s=>{const[y,m,d]=s.split("-").map(Number);return new Date(Date.UTC(y,m-1,d))},addM=(d,n)=>{const x=new Date(d);x.setUTCMonth(x.getUTCMonth()+n);return x},f=d=>d.toISOString().slice(0,10);
function run(){const o=document.getElementById("pres");if(!g("pe")||!g("pen")){o.innerHTML="<p class='mute'>Enter your passport expiry and entry date.</p>";return}
 const exp=day(g("pe")),en=day(g("pen")),ex=g("pex")?day(g("pex")):en,r=g("pr"),pi=g("pi")?day(g("pi")):null;let need,why;
 if(r==="stay"){need=ex;why="the day you leave"}else if(r==="in3"){need=addM(en,3);why="3 months after entry"}else if(r==="in6"){need=addM(en,6);why="6 months after entry"}else if(r==="out3"||r==="sch"){need=addM(ex,3);why="3 months after departure"}else{need=addM(ex,6);why="6 months after departure"}
 let ok=exp>=need;const msg=[`Your passport expires on <strong>${f(exp)}</strong>. It must be valid until at least <strong>${f(need)}</strong> (${why}).`];
 if(r==="sch"){if(!pi)msg.push("Add the issue date to check the 10-year rule.");else if(pi<addM(en,-120)){ok=false;msg.push(`It was issued on ${f(pi)}, more than 10 years before entry, so it can be refused even if it has not expired.`)}}
 o.innerHTML=`<p class="${ok?"up":"down"}"><strong>${ok?"Meets this rule":"Does not meet this rule"}</strong></p><p>${msg.join("</p><p>")}</p><p class="mute">Also check blank pages and the exact wording on the official site.</p>`}
["pe","pi","pen","pex","pr"].forEach(i=>document.getElementById(i).onchange=run);run()})();
