#!/usr/bin/env python3
"""Visa Radar generator. Pulls the latest Passport Index data (MIT), writes ./public. Run: pip install pycountry && python3 build.py"""
import csv,json,os,re,shutil,datetime,html,hashlib,urllib.request,pycountry
SITE=os.environ.get("SITE_URL","https://visaradar.com"); OUT="public"; TODAY=datetime.date.today()
RAW="https://raw.githubusercontent.com/imorte/passport-index-data/main/"; e=html.escape
ADS=os.environ.get("ADSENSE_ID","").strip(); MAIL=os.environ.get("CONTACT_EMAIL","contact@visaradar.com")
V=lambda f:hashlib.md5(open(f"src/{f}","rb").read()).hexdigest()[:8]
TH='<script>try{document.documentElement.dataset.theme=localStorage.getItem("vr:theme")||"light"}catch(e){}</script>'
RADAR='<svg class="radar" viewBox="0 0 400 400" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.2"><circle cx="200" cy="200" r="60"/><circle cx="200" cy="200" r="110"/><circle cx="200" cy="200" r="160"/><circle cx="200" cy="200" r="196"/><path d="M200 4V396M4 200H396"/><g class="sweep"><path d="M200 200L200 6" stroke-width="2.5"/><path d="M200 200L200 6A194 194 0 0 1 300 32Z" fill="currentColor" fill-opacity=".18" stroke="none"/></g></g></svg>'
MARK='<svg viewBox="0 0 40 40" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="20" cy="20" r="17"/><circle cx="20" cy="20" r="9"/><path d="M20 20L33 9"/></svg>'
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
def page(path,title,desc,body,ld="",noidx=False):
    url=f"{SITE}/{path}"
    if not noidx: PAGES.append(url)
    p=f"{OUT}/{path}index.html"; os.makedirs(os.path.dirname(p),exist_ok=True)
    age=f" ({AGE} days before this build)" if AGE is not None else ""
    ads=f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADS}" crossorigin="anonymous"></script>' if ADS else ""
    open(p,"w").write(f'<!DOCTYPE html><html lang="en" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website">{TH}<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Hanken+Grotesk:wght@400;500;600&display=swap"><link rel="stylesheet" href="/assets/style.css?v={V("style.css")}">{ld}{ads}</head><body><header><a class="mark" href="/">{MARK}Visa Radar</a><nav><a href="/passport/">Passports</a><a href="/country/">Destinations</a><a href="/about/">About</a><button id="theme" type="button" aria-label="Switch between light and dark mode">&#9680;</button></nav></header><main>{body}</main><footer><p class="flinks"><a href="/about/">About</a><a href="/disclaimer/">Disclaimer</a><a href="/terms/">Terms of use</a><a href="/privacy/">Privacy policy</a><a href="/contact/">Contact</a></p><p>Visa Radar is an independent information service. It is not a government agency, embassy or visa service, and nothing here is legal or immigration advice. Always confirm entry rules with the official government source before you travel.</p><p>Visa data: Passport Index snapshot dated {UPD}{age}, MIT licence. Live details: REST Countries, Open-Meteo and <a href="https://www.exchangerate-api.com">Rates By Exchange Rate API</a>.</p><p>&copy; {TODAY.year} Visa Radar</p></footer><script src="/assets/app.js?v={V("app.js")}" defer></script></body></html>')
def stamp(v): k=kind(v); return f'<div class="stamp k-{k}"><b>{INFO[k][0]}</b>'+(f"<span>{v} days</span>" if v.isdigit() else "")+"</div>"
def chip(p,d): v=R[p][d]; return f'<a class="chip" href="/{sl(p,d) if (p,d) in CORR else "country/"+d.lower()+"/"}">{e(N[d])}'+(f"<i>{v}d</i>" if v.isdigit() else "")+"</a>"
LIVE=lambda c:f'<section class="live" id="live" data-cc="{c}"><h2>Right now in {e(N[c])}</h2><div id="facts" class="ledger"><p class="mute">Loading live details…</p></div></section>'
def index_page(path,title,items,url):
    page(path,title+" | Visa Radar",title,f"<h1>{title}</h1><div class='chips big'>"+"".join(f'<a class="chip" href="/{url}{c.lower()}/">{e(N[c])}</a>' for c in sorted(items,key=lambda c:N[c]))+"</div>")
def legal():
    ad=("<h2>Advertising</h2><p>This site uses Google AdSense. Google and its partners are third-party vendors that use cookies, including the DoubleClick cookie, to serve ads based on your visits to this and other sites. You can opt out of personalised advertising in <a href='https://adssettings.google.com'>Google Ads Settings</a> or at <a href='https://www.aboutads.info'>aboutads.info</a>. Where the law requires it, we ask for your consent through a consent banner before personalised ads are shown.</p>" if ADS else "<h2>Advertising</h2><p>This site does not currently show advertising. If that changes, this policy will be updated first.</p>")
    P={"about":("About Visa Radar","<h1>About Visa Radar</h1><p class='lede'>Visa Radar helps travellers see, in seconds, whether their passport needs a visa for a destination.</p><h2>Where the data comes from</h2><p>Visa rules come from the open Passport Index dataset (MIT licence), snapshot dated "+UPD+". It covers "+str(len(R))+" passports. Country facts, weather and exchange rates are fetched live from REST Countries, Open-Meteo and ExchangeRate-API.</p><h2>How we keep it current</h2><p>The site rebuilds from the latest dataset every week. The snapshot date is shown in every page footer. Community datasets can lag behind government changes, so we ask you to verify with the official source.</p><h2>Corrections</h2><p>Found a mistake? Email <a href='mailto:"+MAIL+"'>"+MAIL+"</a> with the page address and an official source link.</p>"),
    "disclaimer":("Disclaimer","<h1>Disclaimer</h1><p class='lede'>Visa Radar is for general information only.</p><ul><li>We are not a government agency, embassy, consulate, airline or visa service, and we are not affiliated with any of them.</li><li>Entry rules change often and without notice. Our data is a community snapshot dated "+UPD+" and may be out of date or incomplete.</li><li>Nothing on this site is legal, immigration or travel advice. Border officers and airlines make the final decision on whether you may travel.</li><li>Always confirm requirements, fees, passport validity and health rules with the official government or embassy website before you book or travel.</li><li>Live information from third parties (weather, currency, country facts) is provided as is and may be delayed or unavailable.</li><li>Links to other sites are for convenience. We do not control or endorse their content.</li><li>Advertising, if shown, is not an endorsement of any product or service.</li><li>To the fullest extent the law allows, we are not liable for any loss, denied boarding, fees or other harm resulting from use of this site.</li></ul>"),
    "terms":("Terms of use","<h1>Terms of use</h1><p>Last updated "+TODAY.strftime('%d %B %Y')+". By using Visa Radar you agree to these terms.</p><h2>Use of the site</h2><p>You may use the site for personal, lawful purposes. You may not scrape it in a way that harms its performance, attempt to break or overload it, or present its content as an official source.</p><h2>No advice, no guarantee</h2><p>Content is provided as is, without warranties of accuracy, completeness or fitness for a purpose. See the <a href='/disclaimer/'>disclaimer</a>. You are responsible for checking official sources.</p><h2>Intellectual property</h2><p>The design, text and code of this site belong to the operator. Visa data is derived from the Passport Index dataset under the MIT licence. Third-party names and data remain the property of their owners.</p><h2>Third-party services and links</h2><p>The site calls third-party services and links to other websites. Their terms and privacy policies apply to your use of them.</p><h2>Limitation of liability</h2><p>To the fullest extent permitted by law, the operator is not liable for indirect or consequential loss arising from use of the site.</p><h2>Changes and law</h2><p>We may update these terms; continued use means you accept the update. These terms are governed by the laws of the country where the operator is established.</p><p>Questions: <a href='mailto:"+MAIL+"'>"+MAIL+"</a></p>"),
    "privacy":("Privacy policy","<h1>Privacy policy</h1><p>Last updated "+TODAY.strftime('%d %B %Y')+". We keep data collection to a minimum.</p><h2>What we collect</h2><p>We do not offer accounts and do not ask you for personal data. Our hosting provider (Vercel) keeps standard server logs, such as IP address, browser and pages requested, for security and reliability.</p><h2>Stored in your browser</h2><p>The site saves your last passport and destination, your light or dark preference, and short-lived copies of API responses in your browser's local storage. This stays on your device and you can clear it at any time.</p><h2>Third-party services</h2><p>To show live details, your browser contacts REST Countries, Open-Meteo and ExchangeRate-API, which can see your IP address and browser details under their own policies. Fonts are loaded from Google Fonts.</p>"+ad+"<h2>Your rights</h2><p>Depending on where you live (for example under the GDPR or CCPA), you may have rights to access, correct or delete personal data, or to object to its use. Contact us and we will respond.</p><h2>Children</h2><p>This site is not directed at children under 13.</p><h2>Contact</h2><p><a href='mailto:"+MAIL+"'>"+MAIL+"</a></p>"),
    "contact":("Contact","<h1>Contact</h1><p class='lede'>Email <a href='mailto:"+MAIL+"'>"+MAIL+"</a>.</p><p>To report a data error, include the page address and a link to the official source. We cannot give individual visa advice or process visa applications.</p>")}
    for k,(t,b) in P.items(): page(k+"/",t+" | Visa Radar",t+" for Visa Radar.",f"<div class='prose'>{b}</div>")
    if ADS: open(f"{OUT}/ads.txt","w").write(f"google.com, {ADS.replace('ca-','')}, DIRECT, f08c47fec0942fa0\n")
def build():
    shutil.rmtree(OUT,ignore_errors=True); os.makedirs(f"{OUT}/assets"); os.makedirs(f"{OUT}/data")
    for f in ("style.css","app.js"): shutil.copy(f"src/{f}",f"{OUT}/assets/{f}")
    json.dump({"u":UPD,"n":N,"r":R},open(f"{OUT}/data/rules.json","w"),separators=(",",":"))
    top="".join(f'<a class="row" href="/passport/{p.lower()}/"><span class="rank">{i+1}</span><span>{e(N[p])}</span><span class="mute">{score(p)} destinations</span></a>' for i,p in enumerate(RANK[:10]))
    pop="".join(f'<a class="row" href="/{sl(p,d)}"><span>{e(N[p])} → {e(N[d])}</span><span class="mute">{lab(R[p][d])}</span></a>' for p,d in [("US","JP"),("GB","US"),("IN","GB"),("AE","FR"),("PK","TR"),("EG","DE"),("PH","JP"),("SA","GB")] if (p,d) in CORR)
    page("","Visa Radar: visa rules for every passport",f"Check visa requirements for {len(R)} passports and {len(N)} destinations, with live weather, currency and country details.",f'''<section class="hero">{RADAR}<div><h1>Where can your passport take you?</h1><p class="lede">Pick a passport and a destination. See the entry rule, how long you can stay and what to do next.</p><p class="mute">Covers {len(R)} passports, {len(N)} destinations and {sum(len(d) for d in R.values()):,} routes.</p></div><form class="ticket" id="lookup" onsubmit="return false"><label>Passport<select id="from"></select></label><label>Destination<select id="to"></select></label><div id="stamp" aria-live="polite"><noscript>Turn on JavaScript to use the lookup, or browse the passport pages below.</noscript></div><p class="fine">Confirm on the official government site before you travel. <a href="/disclaimer/">Read the disclaimer</a>.</p></form></section>
<section><h2>Strongest passports</h2><p class="mute">Ranked by destinations reachable without a visa, on arrival or with an electronic authorisation.</p><div class="ledger">{top}</div><p><a href="/passport/">All {len(R)} passports</a></p></section>
<section><h2>Popular routes</h2><div class="ledger">{pop}</div></section><section><h2>How this site works</h2><p class="lede">Visa rules come from the open Passport Index dataset, dated {UPD}. Country details, weather and exchange rates are fetched live. Every page links back to the official-source reminder because rules change quickly. Read <a href="/about/">about us</a>, the <a href="/disclaimer/">disclaimer</a> and <a href="/terms/">terms of use</a>.</p></section>''')
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
    legal()
    open(f"{OUT}/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"".join(f"<url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>" for u in PAGES)+"</urlset>")
    open(f"{OUT}/robots.txt","w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n"); print(len(PAGES),"pages; data",UPD)
build()
