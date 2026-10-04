#!/usr/bin/env python3
"""Visa Radar generator. Pulls the latest Passport Index data (MIT), writes ./public. Run: pip install pycountry && python3 build.py"""
import csv,json,os,re,shutil,datetime,html,urllib.request,pycountry
SITE=os.environ.get("SITE_URL","https://visaradar.com"); OUT="public"; TODAY=datetime.date.today()
RAW="https://raw.githubusercontent.com/imorte/passport-index-data/main/"; e=html.escape
def fetch(n):
    try: return urllib.request.urlopen(RAW+n,timeout=30).read().decode()
    except Exception as x: print("offline, using cached",n); return None
t=fetch("passport-index-tidy-iso2.csv"); rd=fetch("README.md")
if t: open("data/passport-index-tidy-iso2.csv","w").write(t)
else: t=open("data/passport-index-tidy-iso2.csv").read()
m=re.search(r"Last updated: \*\*(.+?)\*\*",rd or "")
if m: open("data/updated.txt","w").write(m[1])
UPD=open("data/updated.txt").read().strip()
try: AGE=(TODAY-datetime.datetime.strptime(UPD,"%d %B %Y").date()).days
except: AGE=None
FIX=dict(US="United States",GB="United Kingdom",RU="Russia",KR="South Korea",KP="North Korea",IR="Iran",SY="Syria",VN="Vietnam",TR="Turkey",CZ="Czechia",BO="Bolivia",TZ="Tanzania",VE="Venezuela",MD="Moldova",LA="Laos",BN="Brunei",PS="Palestine",TW="Taiwan",XK="Kosovo",CD="DR Congo",CG="Congo",FM="Micronesia",VA="Vatican City",MK="North Macedonia",CV="Cape Verde",SZ="Eswatini",HK="Hong Kong",MO="Macao")
def nm(c):
    if c in FIX: return FIX[c]
    x=pycountry.countries.get(alpha_2=c); return (getattr(x,"common_name",None) or x.name) if x else c
SH={"visa free":"vf","visa on arrival":"voa","eta":"eta","e-visa":"ev","visa required":"vr","no admission":"na"}
R={}
for r in csv.DictReader(t.splitlines()):
    if r["Requirement"]=="-1": continue
    R.setdefault(r["Passport"],{})[r["Destination"]]=r["Requirement"] if r["Requirement"].isdigit() else SH.get(r["Requirement"],"vr")
K=["vf","voa","eta","ev","vr","na"]
kind=lambda v:"vf" if v.isdigit() else v
INFO={"vf":("Visa-free","No visa is needed for a tourist stay. Carry a valid passport, onward travel and proof of funds.",["Check passport validity; many countries want six months beyond your stay.","Book onward or return travel.","Carry accommodation details and proof of funds."]),
"voa":("Visa on arrival","The visa is issued at the border.",["Check passport validity and blank pages.","Carry the fee in cash and by card, plus photos.","Keep your return ticket and hotel booking to hand."]),
"eta":("Electronic authorisation","Apply online before you fly. Airlines check it at check-in.",["Apply only on the official government site; lookalike sites charge extra.","Apply well before departure and keep the approval.","Travel on the same passport you applied with."]),
"ev":("e-Visa","Apply online for an electronic visa before you travel.",["Use the official e-visa portal only.","Upload a passport scan, photo and itinerary.","Print the approval and carry it with you."]),
"vr":("Visa required","Apply through the embassy, consulate or official portal before you travel.",["Find the embassy or official application route.","Gather passport, photos, bank statements, itinerary and insurance.","Book biometrics early and apply before buying non-refundable tickets."]),
"na":("Entry not permitted","Entry is currently not permitted for this passport.",["Check your government's travel advice and the destination's official site."])}
lab=lambda v:INFO[kind(v)][0]+(f" · {v} days" if v.isdigit() else "")
N={c:nm(c) for c in set(R)|{d for v in R.values() for d in v}}
CNT={p:{k:sum(1 for v in d.values() if kind(v)==k) for k in K} for p,d in R.items()}
score=lambda p:CNT[p]["vf"]+CNT[p]["voa"]+CNT[p]["eta"]
RANK=sorted(R,key=lambda p:(-score(p),N[p])); POS={p:i+1 for i,p in enumerate(RANK)}
PP="AE SA QA KW IN PK EG PH GB US DE FR CA AU NG ZA".split()
DD="AE US GB FR DE IT ES TR TH JP SG MY ID IN CN KR EG SA QA AU CA NZ GR PT NL CH AT MV LK VN MA ZA BR MX".split()
CORR={(p,d) for p in PP for d in DD if p!=d and p in R and d in R[p]}
sl=lambda p,d:f"visa/{p.lower()}-to-{d.lower()}/"
PAGES=[]
def page(path,title,desc,body,ld=""):
    url=f"{SITE}/{path}"; PAGES.append(url); p=f"{OUT}/{path}index.html"; os.makedirs(os.path.dirname(p),exist_ok=True)
    age=f" ({AGE} days before this build)" if AGE is not None else ""
    open(p,"w").write(f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Hanken+Grotesk:wght@400;500;600&display=swap"><link rel="stylesheet" href="/assets/style.css">{ld}</head><body><header><a class="mark" href="/">Visa Radar</a><nav><a href="/passport/">Passports</a><a href="/country/">Destinations</a></nav></header><main>{body}</main><footer><p>Visa data: Passport Index snapshot dated {UPD}{age}, MIT licence. Rules change without notice, so confirm on the official government site before you travel.</p><p>Live details come from REST Countries, Open-Meteo and <a href="https://www.exchangerate-api.com">Rates By Exchange Rate API</a>.</p></footer><script src="/assets/app.js" defer></script></body></html>')
def stamp(v): k=kind(v); return f'<div class="stamp k-{k}"><b>{INFO[k][0]}</b>'+(f"<span>{v} days</span>" if v.isdigit() else "")+"</div>"
def chip(p,d): v=R[p][d]; return f'<a class="chip" href="/{sl(p,d) if (p,d) in CORR else "country/"+d.lower()+"/"}">{e(N[d])}'+(f"<i>{v}d</i>" if v.isdigit() else "")+"</a>"
LIVE=lambda c:f'<section class="live" id="live" data-cc="{c}"><h2>Right now in {e(N[c])}</h2><div id="facts" class="ledger"><p class="mute">Loading live details…</p></div></section>'
def index_page(path,title,items,url):
    page(path,title+" | Visa Radar",title,f"<h1>{title}</h1><div class='chips big'>"+"".join(f'<a class="chip" href="/{url}{c.lower()}/">{e(N[c])}</a>' for c in sorted(items,key=lambda c:N[c]))+"</div>")
def build():
    shutil.rmtree(OUT,ignore_errors=True); os.makedirs(f"{OUT}/assets"); os.makedirs(f"{OUT}/data")
    for f in ("style.css","app.js"): shutil.copy(f"src/{f}",f"{OUT}/assets/{f}")
    json.dump({"u":UPD,"n":N,"r":R},open(f"{OUT}/data/rules.json","w"),separators=(",",":"))
    top="".join(f'<a class="row" href="/passport/{p.lower()}/"><span class="rank">{i+1}</span><span>{e(N[p])}</span><span class="mute">{score(p)} destinations</span></a>' for i,p in enumerate(RANK[:10]))
    pop="".join(f'<a class="row" href="/{sl(p,d)}"><span>{e(N[p])} → {e(N[d])}</span><span class="mute">{lab(R[p][d])}</span></a>' for p,d in [("US","JP"),("GB","US"),("IN","GB"),("AE","FR"),("PK","TR"),("EG","DE"),("PH","JP"),("SA","GB")] if (p,d) in CORR)
    page("","Visa Radar: visa rules for every passport",f"Check visa requirements for {len(R)} passports and {len(N)} destinations, with live weather, currency and country details.",f'''<section class="hero"><h1>Where can your passport take you?</h1><p class="lede">Choose a passport and a destination. We show the entry rule, the stay allowed and what to do next.</p>
<form class="ticket" id="lookup" onsubmit="return false"><label>Passport<select id="from"></select></label><label>Destination<select id="to"></select></label><div id="stamp" aria-live="polite"><noscript>Enable JavaScript to use the lookup, or browse the passport pages below.</noscript></div></form></section>
<section><h2>Strongest passports</h2><p class="mute">Ranked by destinations reachable without a visa, on arrival or with an electronic authorisation.</p><div class="ledger">{top}</div><p><a href="/passport/">All {len(R)} passports</a></p></section>
<section><h2>Popular routes</h2><div class="ledger">{pop}</div></section>''')
    index_page("passport/","Visa rules by passport",R,"passport/"); index_page("country/","Destination guides",N,"country/")
    for p in R:
        c=CNT[p]; body=f'<h1>{e(N[p])} passport</h1><p class="lede">Ranked {POS[p]} of {len(R)}. Visa-free to {c["vf"]} destinations, visa on arrival in {c["voa"]}, electronic authorisation for {c["eta"]}, e-visa for {c["ev"]}, and a visa needed for {c["vr"]+c["na"]}.</p>'
        for k in K:
            ds=sorted([d for d,v in R[p].items() if kind(v)==k],key=lambda d:N[d])
            if ds: body+=f'<section><h2>{INFO[k][0]} <span class="mute">{len(ds)}</span></h2><div class="chips">{"".join(chip(p,d) for d in ds)}</div></section>'
        page(f"passport/{p.lower()}/",f"{N[p]} Passport Visa Requirements | Visa Radar",f"Where {N[p]} passport holders can travel: {c['vf']} visa-free, {c['voa']} on arrival, {c['eta']} eTA, {c['ev']} e-visa destinations.",body)
    for d in N:
        inb={p:R[p][d] for p in R if d in R[p]}; cc={k:sum(1 for v in inb.values() if kind(v)==k) for k in K}
        body=f'<h1>Travel to {e(N[d])}</h1><p class="lede">Visa-free for {cc["vf"]} passports, on arrival for {cc["voa"]}, electronic authorisation for {cc["eta"]}, e-visa for {cc["ev"]}, and a visa required for {cc["vr"]+cc["na"]}.</p>'+LIVE(d)
        for k in K:
            ps=sorted([p for p,v in inb.items() if kind(v)==k],key=lambda p:N[p])
            if ps: body+=f'<details{" open" if k=="vf" else ""}><summary>{INFO[k][0]} ({len(ps)} passports)</summary><div class="chips">{"".join(f"<a class=chip href=/passport/{p.lower()}/>{e(N[p])}</a>" for p in ps)}</div></details>'
        page(f"country/{d.lower()}/",f"Travel to {N[d]}: Entry Rules & Live Details | Visa Radar",f"Who needs a visa for {N[d]}, plus live weather, currency and country facts.",body)
    for p,d in sorted(CORR):
        v=R[p][d]; k=kind(v); oth=[x for x in DD if (p,x) in CORR and x!=d][:8]
        body=f'<h1>{e(N[p])} passport to {e(N[d])}</h1>{stamp(v)}<p class="lede">{INFO[k][1]}</p><h2>What to do</h2><ol>{"".join(f"<li>{s}</li>" for s in INFO[k][2])}</ol><p class="note">Confirm this on the official {e(N[d])} government or embassy site. Dataset snapshot dated {UPD}.</p>'+LIVE(d)+f'<h2>More from {e(N[p])}</h2><div class="chips">{"".join(chip(p,x) for x in oth)}</div><p><a href="/passport/{p.lower()}/">All {e(N[p])} passport rules</a> · <a href="/country/{d.lower()}/">Everyone entering {e(N[d])}</a></p>'
        q=f"Do {N[p]} citizens need a visa for {N[d]}?"; ld=f'<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":lab(v)+". "+INFO[k][1]}}]})}</script>'
        page(sl(p,d),f"{N[p]} to {N[d]} Visa: {INFO[k][0]} | Visa Radar",f"{q} {lab(v)}. Steps, stay allowed and live destination details.",body,ld)
    open(f"{OUT}/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"".join(f"<url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in PAGES)+"</urlset>")
    open(f"{OUT}/robots.txt","w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n"); print(len(PAGES),"pages; data",UPD)
build()
