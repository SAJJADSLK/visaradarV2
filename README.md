# VisaRadar

Static visa-requirement and country-guide site, generated from one dataset.

## Structure
- `build.py`: generator. Reads `seed.sql` and the country table, writes `public/`.
- `seed.sql`: visa rules (passport, destination, requirement, stay, notes, reviewed date).
- `public/`: the generated site. This is the only folder that gets deployed.
- `wrangler.jsonc`: Cloudflare config serving `public/`.
- `legacy/`: the original interactive tools (calculator, compare, border waits, alerts, Worker/D1 API). Not deployed. Port these into the new design later; fix the `innerHTML` XSS in `alerts.html` and the open write endpoints in `api/worker.js` first.

## Build and deploy
    python3 build.py              # regenerates public/ (no dependencies)
    npx wrangler deploy           # or upload public/ to Cloudflare Pages / any static host

## Add data
- New country: add a line to the `C` table in `build.py`.
- New rule: add a row to `seed.sql`, or add a `fix(...)` call in `build.py` for a dated correction.
- Rebuild. Pages, internal links, sitemap and structured data update automatically.

## Before going live
- Replace `contact@visaradar.com` in `build.py` with your real address.
- Confirm each rule against the official government source; 39 pages still carry the Jan 2025 date and show a "possibly outdated" warning.
- Update the privacy page before adding analytics, ads or email alerts.
- Submit `https://visaradar.com/sitemap.xml` in Google Search Console.

## Deploy on Vercel
1. Push this folder to GitHub (commit `public/` too).
2. In Vercel: Add New > Project > import the repo. Framework Preset: Other. `vercel.json` already sets the output directory to `public` and disables the build step.
3. Deploy, then add your domain under Settings > Domains.
After editing data: run `python3 build.py` locally, commit the updated `public/`, and push.
