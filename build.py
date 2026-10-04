#!/usr/bin/env python3
"""VisaRadar static site generator. Run: python3 build.py  -> writes ./public/
Add countries to C and rules to RULES (or point SEED at api/seed.sql); every page, link and sitemap entry regenerates."""
import re, os, html, datetime, shutil, json
SITE="https://visaradar.com"; OUT="public"; TODAY=datetime.date.today().isoformat()
SEED=os.environ.get("SEED","seed.sql")
# code: name, region, capital, currency, language, plug, drive side, calling code
C={k:dict(zip("name region capital cur lang plug drive call".split(),v.split("|"))) for k,v in {
"AE":"United Arab Emirates|Middle East|Abu Dhabi|AED|Arabic|G|Right|+971","US":"United States|North America|Washington, D.C.|USD|English|A, B|Right|+1",
"GB":"United Kingdom|Europe|London|GBP|English|G|Left|+44","DE":"Germany|Europe|Berlin|EUR|German|C, F|Right|+49","FR":"France|Europe|Paris|EUR|French|C, E|Right|+33",
"IT":"Italy|Europe|Rome|EUR|Italian|C, F, L|Right|+39","ES":"Spain|Europe|Madrid|EUR|Spanish|C, F|Right|+34","TR":"Turkey|Middle East|Ankara|TRY|Turkish|C, F|Right|+90",
"EG":"Egypt|Africa|Cairo|EGP|Arabic|C, F|Right|+20","SA":"Saudi Arabia|Middle East|Riyadh|SAR|Arabic|G|Right|+966","QA":"Qatar|Middle East|Doha|QAR|Arabic|D, G|Right|+974",
"JP":"Japan|Asia|Tokyo|JPY|Japanese|A|Left|+81","KR":"South Korea|Asia|Seoul|KRW|Korean|C, F|Right|+82","CN":"China|Asia|Beijing|CNY|Mandarin|A, C, I|Right|+86",
"IN":"India|Asia|New Delhi|INR|Hindi, English|C, D, M|Left|+91","PK":"Pakistan|Asia|Islamabad|PKR|Urdu, English|C, D, G, K|Left|+92","SG":"Singapore|Asia|Singapore|SGD|English|G|Left|+65",
"TH":"Thailand|Asia|Bangkok|THB|Thai|A, B, C, F, O|Left|+66","MY":"Malaysia|Asia|Kuala Lumpur|MYR|Malay|G|Left|+60","ID":"Indonesia|Asia|Jakarta|IDR|Indonesian|C, F|Left|+62",
"PH":"Philippines|Asia|Manila|PHP|Filipino, English|A, B, C|Right|+63","AU":"Australia|Oceania|Canberra|AUD|English|I|Left|+61","NZ":"New Zealand|Oceania|Wellington|NZD|English|I|Left|+64",
"CA":"Canada|North America|Ottawa|CAD|English, French|A, B|Right|+1"}.items()}
REQ={"visa_free":("Visa-free","ok","No visa is needed for short tourist stays. You still need a valid passport and may be asked for onward travel and funds."),
"visa_on_arrival":("Visa on arrival","ok","A visa is issued at the border. Carry cash or a card for the fee, passport photos and proof of onward travel."),
"esta":("Electronic authorisation","warn","Apply online for an electronic travel authorisation before you fly. Airlines check it at check-in."),
"visa_required":("Visa required","bad","Apply for a visa before travelling. Allow extra time for appointments, biometrics and processing.")}
STEPS={"visa_free":["Check passport validity (many countries require 6 months beyond your stay).","Book onward or return travel.","Carry proof of accommodation and funds.","Check health or customs rules on the official government site."],
"visa_on_arrival":["Check passport validity and blank pages.","Carry the fee in cash and card, plus passport photos.","Print your return ticket and hotel booking.","Confirm the airport or border crossing offers visa on arrival."],
"esta":["Apply on the official government site only. Lookalike sites charge extra.","Apply well ahead of departure and keep the approval email.","Use the same passport to travel that you applied with.","Check the fee and validity period on the official site."],
"visa_required":["Find the embassy, consulate or official e-visa portal.","Gather passport, photos, bank statements, itinerary and insurance.","Book biometrics or interview appointments early.","Apply before booking non-refundable travel.","Track the application and allow buffer time."]}
RULES={}
def load():
    if os.path.exists(SEED):
        for m in re.finditer(r"^\('(\w+)','(\w+)','(\w+)',(NULL|\d+),'((?:[^']|'')*)','([\d-]+)'\)",open(SEED).read(),re.M):
            f,t,r,s,n,u=m.groups(); RULES[(f,t)]=dict(req=r,stay=None if s=="NULL" else int(s),notes=n.replace("''","'"),upd=u)
    # correction: the UK now requires an ETA for US visitors (verify the fee on gov.uk)
    RULES[("US","GB")]=dict(req="esta",stay=180,notes="UK Electronic Travel Authorisation (ETA) is required before travel. Apply via the official UK government site or app.",upd=TODAY)
    N=" Corrected in editorial review; confirm on the official site."
    def fix(f,t,req,stay,n): RULES[(f,t)]=dict(req=req,stay=stay,notes=n+N,upd=TODAY)
    SCH="Schengen Area entry is visa-free for up to 90 days in any 180-day period. Check for any new pre-travel registration (such as ETIAS) before you go."
    for t in ("DE","FR","IT","ES"): fix("AE",t,"visa_free",90,"UAE citizens. "+SCH)
    fix("AE","GB","esta",180,"UAE citizens need a UK Electronic Travel Authorisation (ETA) before travel; apply via the official UK government site or app.")
    fix("JP","GB","esta",180,"Japanese citizens need a UK Electronic Travel Authorisation (ETA) before travel; apply via the official UK government site or app.")
    fix("PH","JP","visa_required",None,"Philippine passport holders need a visa for Japan; check the Japanese embassy or official e-visa options.")
    fix("IN","AE","visa_required",None,"Indian passport holders generally need a visa. Visa on arrival applies only to holders of certain US, UK or EU visas or residence permits.")
    RULES[("IN","SG")]["stay"]=None
    for k in [k for k in RULES if k[0] not in C or k[1] not in C or k[0]==k[1]]: del RULES[k]
e=html.escape
def nm(c): return C[c]["name"]
def page(path,title,desc,body,prio="0.6",extra="",noidx=False):
    p=f"{OUT}/{path}index.html" if path.endswith("/") or path=="" else f"{OUT}/{path}"
    os.makedirs(os.path.dirname(p),exist_ok=True); url=f"{SITE}/{path}"; rb="noindex,follow" if noidx else "index,follow"
    if not noidx: PAGES.append((url,prio))
    open(p,"w").write(f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}"><meta name="robots" content="{rb}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta property="og:type" content="website">{extra}<link rel="stylesheet" href="/assets/style.css"></head><body><nav><a class="logo" href="/">VISA <b>RADAR</b></a><a href="/countries/">Countries</a><a href="/visa/">Visa Rules</a></nav><main>{body}</main><footer><p><a href="/about/">About</a> · <a href="/privacy/">Privacy</a> · <a href="/contact/">Contact</a></p><p>Informational only. Rules change often, so always confirm with the official embassy or government portal before you travel. Last build: {TODAY}.</p></footer></body></html>''')
def badge(r): return f'<span class="b {REQ[r][1]}">{REQ[r][0]}</span>'
def slug(f,t): return f"visa/{f.lower()}-to-{t.lower()}/"
def card(f,t): r=RULES[(f,t)]; return f'<a class="card" href="/{slug(f,t)}"><b>{nm(f)} → {nm(t)}</b>{badge(r["req"])}</a>'
def ld(f,t,r):
    nav=[("Home","/"),("Visa rules","/visa/"),(f"{nm(f)} to {nm(t)}","/"+slug(f,t))]
    d=[{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":SITE+u} for i,(n,u) in enumerate(nav)]},
       {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":f"Do {nm(f)} citizens need a visa for {nm(t)}?","acceptedAnswer":{"@type":"Answer","text":REQ[r["req"]][0]+". "+r["notes"]}}]}]
    return "".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in d)
def extras():
    page("about/","About Visa Radar","How Visa Radar collects, reviews and labels visa information.","<h1>About Visa Radar</h1><p>Visa Radar publishes passport-to-destination entry rules and country travel guides. Every rule page shows when it was last reviewed, and pages older than 180 days carry a warning.</p><h2>How we work</h2><ul><li>Rules are stored in one dataset and rebuilt into static pages.</li><li>Corrections are logged and dated.</li><li>We are not a government agency or a visa service, and nothing here is legal advice.</li></ul><p>Spot an error? <a href='/contact/'>Tell us</a> and include an official source link.</p>","0.4")
    page("privacy/","Privacy Policy | Visa Radar","What data Visa Radar collects.","<h1>Privacy policy</h1><p>This site does not use accounts, analytics or advertising cookies and does not collect personal data through forms. Our hosting provider may keep standard server logs (such as IP address and page requested) for security and reliability.</p><p>If we add analytics, advertising or email alerts, this policy will be updated first and consent will be requested where required.</p>","0.3")
    page("contact/","Contact | Visa Radar","Report a data error or get in touch.","<h1>Contact</h1><p>Email <a href='mailto:contact@visaradar.com'>contact@visaradar.com</a>. For data corrections, include the page URL and a link to the official source.</p>","0.3")
    page("404.html","Page not found | Visa Radar","Page not found.","<h1>Page not found</h1><p>Try the <a href='/visa/'>visa rules</a> or <a href='/countries/'>country guides</a>.</p>",noidx=True)
    open(f"{OUT}/_headers","w").write("/*\n  X-Content-Type-Options: nosniff\n  X-Frame-Options: DENY\n  Referrer-Policy: strict-origin-when-cross-origin\n  Permissions-Policy: geolocation=(), camera=(), microphone=()\n/assets/*\n  Cache-Control: public, max-age=86400\n")
PAGES=[]
def build():
    load(); shutil.rmtree(OUT,ignore_errors=True); os.makedirs(f"{OUT}/assets")
    open(f"{OUT}/assets/style.css","w").write(":root{--bg:#0b0f17;--fg:#e8ecf3;--mut:#93a0b4;--gold:#c9a84c;--card:#141b28}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.65 system-ui,sans-serif}nav{display:flex;gap:20px;align-items:center;padding:14px 5%;border-bottom:1px solid #222c3d}nav a{color:var(--mut);text-decoration:none}.logo{color:var(--fg);letter-spacing:.15em;margin-right:auto}.logo b{color:var(--gold)}main{max-width:960px;margin:auto;padding:32px 5%}h1{font-size:2rem;margin:.2em 0}h2{margin-top:2em;color:var(--gold)}table{width:100%;border-collapse:collapse}td,th{padding:9px;border-bottom:1px solid #222c3d;text-align:left}th{color:var(--mut);width:40%}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px}.card{display:flex;flex-direction:column;gap:6px;background:var(--card);padding:14px;border-radius:10px;color:var(--fg);text-decoration:none;border:1px solid #222c3d}.card:hover{border-color:var(--gold)}.b{display:inline-block;width:fit-content;padding:2px 10px;border-radius:99px;font-size:.8rem;font-weight:600}.ok{background:#12351f;color:#5fe08d}.warn{background:#3b2f0e;color:#f3c64f}.bad{background:#3d1519;color:#ff7b86}.note{background:var(--card);border-left:3px solid var(--gold);padding:12px 16px;border-radius:6px;color:var(--mut)}footer{padding:30px 5%;color:var(--mut);font-size:.85rem;border-top:1px solid #222c3d}a{color:var(--gold)}")
    regions=sorted({c["region"] for c in C.values()})
    for code,c in C.items():
        into=[f for (f,t) in RULES if t==code]; outof=[t for (f,t) in RULES if f==code]
        near=[k for k,v in C.items() if v["region"]==c["region"] and k!=code]
        facts="".join(f"<tr><th>{k}</th><td>{e(v)}</td></tr>" for k,v in [("Capital",c["capital"]),("Region",c["region"]),("Currency",c["cur"]),("Languages",c["lang"]),("Plug types",c["plug"]),("Drives on the",c["drive"]),("Calling code",c["call"])])
        body=f'<h1>{nm(code)} travel &amp; visa guide</h1><p>Quick facts, entry rules and a travel checklist for {nm(code)}.</p><table>{facts}</table>'
        if into: body+=f'<h2>Entering {nm(code)}: rules by passport</h2><div class="grid">{"".join(card(f,code) for f in into)}</div>'
        if outof: body+=f'<h2>Travelling from {nm(code)}: passport rules</h2><div class="grid">{"".join(card(code,t) for t in outof)}</div>'
        body+=f'<h2>Before you go to {nm(code)}</h2><ul><li>Passport valid for at least 6 months, with blank pages.</li><li>Travel insurance covering medical care and cancellation.</li><li>Notify your bank, and carry some {c["cur"]} cash.</li><li>Check that your devices fit {c["plug"]} plugs, and save the {c["call"]} calling code for emergencies.</li><li>Drive on the {c["drive"].lower()} side if renting a car, and check whether you need an international driving permit.</li></ul>'
        if near: body+=f'<h2>More in {c["region"]}</h2><div class="grid">{"".join(f"<a class=card href=/country/{k.lower()}/><b>{nm(k)}</b><span>{C[k]["capital"]}</span></a>" for k in near)}</div>'
        page(f"country/{code.lower()}/",f"{nm(code)} Travel & Visa Guide | Visa Radar",f"Visa requirements, currency, plugs, language and travel checklist for {nm(code)}.",body,"0.8",noidx=not(into or outof))
    for (f,t),r in RULES.items():
        stay=f'<tr><th>Maximum stay</th><td>{r["stay"]} days</td></tr>' if r["stay"] else ""
        age=(datetime.date.today()-datetime.date.fromisoformat(r["upd"])).days; stale=f'<div class="note"><b>Possibly outdated:</b> last reviewed {age} days ago. Verify before you book.</div><br>' if age>180 else ""; sib=[x for x in C if (f,x) in RULES and x!=t][:6]; rev=f'<p>Going the other way? <a href="/{slug(t,f)}">{nm(t)} → {nm(f)}</a></p>' if (t,f) in RULES else ""
        body=f'<h1>{nm(f)} passport holders travelling to {nm(t)}</h1><p>{badge(r["req"])}</p><p>{REQ[r["req"]][2]}</p><table><tr><th>Requirement</th><td>{REQ[r["req"]][0]}</td></tr>{stay}<tr><th>Details</th><td>{e(r["notes"])}</td></tr><tr><th>Last reviewed</th><td>{r["upd"]}</td></tr></table>{stale}<div class="note">Confirm this on the official {nm(t)} government or embassy site. Entry rules can change with little notice.</div><h2>Your checklist</h2><ol>{"".join(f"<li>{s}</li>" for s in STEPS[r["req"]])}</ol><h2>Useful links</h2><p><a href="/country/{t.lower()}/">{nm(t)} travel guide</a> · <a href="/country/{f.lower()}/">{nm(f)} guide</a></p>{rev}'
        if sib: body+=f'<h2>Other destinations for {nm(f)} passports</h2><div class="grid">{"".join(card(f,x) for x in sib)}</div>'
        page(slug(f,t),f"{nm(f)} to {nm(t)} Visa | Visa Radar",f"Do {nm(f)} citizens need a visa for {nm(t)}? {REQ[r['req']][0]}. Checklist, details and official-source reminder.",body,"0.7",extra=ld(f,t,r))
    page("visa/","Visa Requirements by Passport | Visa Radar","Browse visa requirements by passport and destination.",'<h1>Visa rules</h1>'+"".join(f'<h2>{nm(f)} passport</h2><div class="grid">{"".join(card(f,t) for (ff,t) in RULES if ff==f)}</div>' for f in sorted({f for f,_ in RULES})),"0.8")
    page("countries/","Country Travel Guides | Visa Radar","Travel facts and entry rules for every country we cover.",'<h1>Country guides</h1>'+"".join(f'<h2>{rg}</h2><div class="grid">{"".join(f"<a class=card href=/country/{k.lower()}/><b>{v["name"]}</b><span>{v["capital"]} · {v["cur"]}</span></a>" for k,v in C.items() if v["region"]==rg)}</div>' for rg in regions),"0.8")
    page("","Visa Radar: Visa Requirements & Country Travel Guides",f"Visa rules for {len(RULES)} passport routes and travel guides for {len(C)} countries.",f'<h1>Know before you go.</h1><p>{len(C)} country guides and {len(RULES)} passport-to-destination visa pages, each with a checklist and a clear note on when it was last reviewed.</p><h2>Popular routes</h2><div class="grid">{"".join(card(f,t) for f,t in list(RULES)[:12])}</div><h2>Browse by region</h2><div class="grid">{"".join(f"<a class=card href=/countries/><b>{rg}</b><span>{sum(1 for v in C.values() if v["region"]==rg)} countries</span></a>" for rg in regions)}</div>',"1.0")
    extras()
    open(f"{OUT}/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"".join(f"<url><loc>{u}</loc><lastmod>{TODAY}</lastmod><priority>{p}</priority></url>" for u,p in PAGES)+"</urlset>")
    open(f"{OUT}/robots.txt","w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    print(len(PAGES),"pages")
build()
