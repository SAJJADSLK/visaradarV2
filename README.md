# Visa Radar Pro

Luxury-design static site: 933 pages (199 passports, 199 destinations, 532 popular routes) built from the Passport Index dataset (MIT) with live country, weather and currency panels.

## Data
- Visa rules: github.com/imorte/passport-index-data (updated 17 Feb 2026 at build time). `build.py` downloads the latest CSV and README date on every run; cached copy in `data/` is used offline.
- The snapshot date and its age are printed in every page footer. This is a community dataset, not an official feed. Always confirm on government sites.
- `.github/workflows/refresh.yml` rebuilds weekly and commits `public/`, which triggers a new Vercel deploy.

## Live APIs (called in the visitor's browser, cached in localStorage)
- REST Countries v3.1: capital, languages, calling code, time zone, driving side, population (7-day cache).
- Open-Meteo: capital-city weather (30 min cache). Free tier is non-commercial; move to a paid plan before adding ads or affiliate links.
- open.er-api.com (ExchangeRate-API open endpoint): USD and EUR rates, refreshed daily (6 h cache). Attribution link is in the footer; keep it.

## Run and deploy
    pip install pycountry && python3 build.py
Vercel: import the repo, Framework "Other". `vercel.json` serves `public/`.
Edit design in `src/style.css`, behaviour in `src/app.js`, pages in `build.py`.

## Not included yet
About, Privacy and Contact pages, the calculator and compare tools, and email alerts. Add privacy and contact pages before applying for ads.

## Settings (environment variables for `build.py`)
- `SITE_URL`: your live domain (used in canonicals and the sitemap).
- `CONTACT_EMAIL`: shown on the legal pages. Default is a placeholder; set your real address.
- `ADSENSE_ID`: e.g. `ca-pub-1234567890123456`. When set, the AdSense script and `ads.txt` are added. Leave empty until Google approves the site; the privacy page switches wording automatically.
Example: `SITE_URL=https://yourdomain.com CONTACT_EMAIL=you@yourdomain.com python3 build.py`

## Cache note
CSS and JS URLs carry a content hash (`style.css?v=...`), so visitors always get the newest design after a deploy.

## AdSense (auto ads)
1. Apply at adsense.google.com with your live domain and add the site.
2. Build with `ADSENSE_ID=ca-pub-XXXXXXXXXXXXXXXX` (and push). This adds the AdSense script to content pages, the `google-adsense-account` meta tag everywhere, and `ads.txt`. Legal pages, noindex pages and the 404 page never load ads.
3. In AdSense, turn on **Auto ads** for the site. Ads appear automatically once Google approves it; nothing shows before that.
4. EEA/UK/Swiss visitors: in AdSense go to **Privacy & messaging** and publish a consent message. The footer "Ad and cookie settings" link appears automatically once it loads.
5. Optional manual unit: set `ADSENSE_SLOT` to a display ad unit ID to place one labelled ad on guides and the news page.
In GitHub, set repository variables or edit the workflow to pass ADSENSE_ID, SITE_URL and CONTACT_EMAIL into the build step.

## News
`data/feeds.json` lists RSS/Atom feeds fetched at build time (twice a day via the workflow). Edit it to add or remove sources. Items are cached in `data/news.json`, older than 120 days are dropped, and a failed feed is skipped. Check the Actions log for "feed skipped" lines to see which URLs need fixing.
