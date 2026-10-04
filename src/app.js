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
