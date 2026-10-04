// api/worker.js — Main Cloudflare Worker
// Handles all /api/* routes for VisaRadar24
// Deploy with: wrangler deploy

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;

    // CORS headers for all responses
    const cors = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: cors });
    }

    function json(data, status = 200, extra = {}) {
      return new Response(JSON.stringify(data), {
        status,
        headers: { 'Content-Type': 'application/json', ...cors, ...extra },
      });
    }

    try {
      // Route handler
      if (path === '/api/border-waits' || path === '/api/border-waits/') {
        return await handleBorderWaits(request, env, ctx, json);
      }
      if (path === '/api/stats') {
        return await handleStats(request, env, ctx, json);
      }
      if (path === '/api/alerts') {
        return await handleAlerts(request, env, ctx, json);
      }
      if (path === '/api/visa-rules') {
        return await handleVisaRules(request, env, ctx, json);
      }
      if (path === '/api/subscribe' && request.method === 'POST') {
        return await handleSubscribe(request, env, ctx, json);
      }
      if (path === '/api/contact' && request.method === 'POST') {
        return await handleContact(request, env, ctx, json);
      }
      // Not an API route — serve static asset
      if (env.ASSETS) {
        return env.ASSETS.fetch(request);
      }
      return json({ error: "Not found" }, 404);
    } catch (err) {
      console.error(err);
      return json({ error: 'Internal server error' }, 500);
    }
  },
};

// ─── BORDER WAITS ───────────────────────────────────────────────────────────
// Source: US CBP public API (free, no auth required)
// Cache: 10 minutes in KV

async function handleBorderWaits(request, env, ctx, json) {
  const CACHE_KEY = 'border_waits_v1';
  const CACHE_TTL = 600; // 10 minutes

  // Check KV cache first
  if (env.KV) {
    const cached = await env.KV.get(CACHE_KEY);
    if (cached) {
      return json(JSON.parse(cached), 200, { 'X-Cache': 'HIT' });
    }
  }

  // Fetch from CBP
  try {
    const CBP_URL = 'https://bwt.cbp.gov/api/bwtdata';
    const res = await fetch(CBP_URL, {
      headers: { 'Accept': 'application/json', 'User-Agent': 'VisaRadar24/1.0' },
      cf: { cacheTtl: 300, cacheEverything: true },
    });

    if (!res.ok) throw new Error(`CBP API returned ${res.status}`);
    const raw = await res.json();

    // Normalize CBP data into our format
    const ports = normalizeCBPData(raw);
    const result = { ports, fetchedAt: new Date().toISOString(), source: 'cbp' };

    // Store in KV
    if (env.KV) {
      ctx.waitUntil(env.KV.put(CACHE_KEY, JSON.stringify(result), { expirationTtl: CACHE_TTL }));
    }

    return json(result, 200, { 'X-Cache': 'MISS' });
  } catch (err) {
    // Return fallback static data if CBP is down
    return json(getFallbackBorderData(), 200, { 'X-Cache': 'FALLBACK' });
  }
}

function normalizeCBPData(raw) {
  if (!raw || !Array.isArray(raw)) return getFallbackBorderData().ports;
  return raw.slice(0, 20).map(port => ({
    port: port.port_name || 'Unknown',
    location: `${port.state || ''} — ${port.border || ''}`.trim(),
    border: (port.border || '').toLowerCase().includes('canada') ? 'canada' : 'mexico',
    lanes: [
      port.passenger_vehicle_lanes?.standard_lanes
        ? { name: 'Passenger vehicles', wait: parseInt(port.passenger_vehicle_lanes.standard_lanes.delay_minutes) || 0 }
        : null,
      port.passenger_vehicle_lanes?.NEXUS_SENTRI_lanes
        ? { name: 'NEXUS / SENTRI', wait: parseInt(port.passenger_vehicle_lanes.NEXUS_SENTRI_lanes.delay_minutes) || 0 }
        : null,
      port.pedestrian_lanes?.standard_lanes
        ? { name: 'Pedestrian', wait: parseInt(port.pedestrian_lanes.standard_lanes.delay_minutes) || 0 }
        : null,
    ].filter(Boolean),
  })).filter(p => p.lanes.length > 0);
}

function getFallbackBorderData() {
  return {
    ports: [
      { port: 'San Ysidro', location: 'San Diego, CA — Mexico', border: 'mexico', lanes: [{ name: 'Passenger vehicles', wait: 45 }, { name: 'Ready Lane', wait: 20 }, { name: 'Pedestrian', wait: 10 }] },
      { port: 'Otay Mesa', location: 'San Diego, CA — Mexico', border: 'mexico', lanes: [{ name: 'Passenger vehicles', wait: 30 }, { name: 'Commercial', wait: 55 }] },
      { port: 'El Paso–Ysleta', location: 'El Paso, TX — Mexico', border: 'mexico', lanes: [{ name: 'Passenger vehicles', wait: 25 }, { name: 'Ready Lane', wait: 10 }] },
      { port: 'Laredo–World Trade Bridge', location: 'Laredo, TX — Mexico', border: 'mexico', lanes: [{ name: 'Commercial', wait: 40 }, { name: 'FAST', wait: 15 }] },
      { port: 'Buffalo–Peace Bridge', location: 'Buffalo, NY — Canada', border: 'canada', lanes: [{ name: 'Passenger vehicles', wait: 15 }, { name: 'NEXUS', wait: 5 }] },
      { port: 'Detroit–Ambassador Bridge', location: 'Detroit, MI — Canada', border: 'canada', lanes: [{ name: 'Passenger vehicles', wait: 20 }] },
      { port: 'Blaine–Pacific Highway', location: 'Blaine, WA — Canada', border: 'canada', lanes: [{ name: 'Passenger vehicles', wait: 10 }, { name: 'NEXUS', wait: 5 }] },
    ],
    fetchedAt: new Date().toISOString(),
    source: 'fallback',
  };
}

// ─── STATS ───────────────────────────────────────────────────────────────────
async function handleStats(request, env, ctx, json) {
  const CACHE_KEY = 'stats_v1';
  if (env.KV) {
    const cached = await env.KV.get(CACHE_KEY);
    if (cached) return json(JSON.parse(cached));
  }

  // Derive stats — in production, query D1 for real counts
  const stats = {
    visaFree: 183,
    changes: 3,
    avgWait: 22,
    advisories: 14,
    lastUpdated: new Date().toISOString(),
  };

  if (env.KV) {
    ctx.waitUntil(env.KV.put(CACHE_KEY, JSON.stringify(stats), { expirationTtl: 3600 }));
  }
  return json(stats);
}

// ─── ALERTS / POLICY FEED ────────────────────────────────────────────────────
// Fetches embassy RSS feeds via rss2json
async function handleAlerts(request, env, ctx, json) {
  const CACHE_KEY = 'alerts_v1';
  const CACHE_TTL = 3600; // 1 hour

  if (env.KV) {
    const cached = await env.KV.get(CACHE_KEY);
    if (cached) return json(JSON.parse(cached), 200, { 'X-Cache': 'HIT' });
  }

  try {
    // rss2json is a free RSS-to-JSON proxy — fetch US State Dept travel alerts
    const RSS_URL = encodeURIComponent('https://travel.state.gov/content/travel/en/News/travelnews.rss');
    const res = await fetch(`https://api.rss2json.com/v1/api.json?rss_url=${RSS_URL}&count=12`);

    if (!res.ok) throw new Error('RSS fetch failed');
    const data = await res.json();

    const alerts = (data.items || []).map(item => ({
      date: new Date(item.pubDate).toLocaleDateString('en-US', { month: 'short', year: 'numeric' }),
      country: '🇺🇸 US State Dept',
      title: item.title,
      desc: item.description?.replace(/<[^>]+>/g, '').slice(0, 180) + '…',
      type: 'warn',
      link: item.link,
    }));

    if (env.KV) {
      ctx.waitUntil(env.KV.put(CACHE_KEY, JSON.stringify(alerts), { expirationTtl: CACHE_TTL }));
    }
    return json(alerts, 200, { 'X-Cache': 'MISS' });
  } catch (err) {
    return json(getStaticAlerts());
  }
}

function getStaticAlerts() {
  return [
    { date: 'Mar 2025', country: '🇦🇺 Australia', title: 'eTA fee increase to AUD $23', desc: 'The Australian Electronic Travel Authority fee increased effective March 2025.', type: 'warn' },
    { date: 'Feb 2025', country: '🇬🇧 United Kingdom', title: 'ETA now required for EU citizens', desc: 'UK Electronic Travel Authorisation extended to all EU nationals for air, sea and rail travel.', type: 'new' },
    { date: 'Jan 2025', country: '🇮🇳 India', title: 'e-Visa processing time reduced', desc: 'India reduced e-Visa processing time from 5 to 3 business days for most nationalities.', type: 'new' },
    { date: 'Jan 2025', country: '🇹🇭 Thailand', title: 'Destination Thailand Visa (DTV) launched', desc: 'New long-stay visa valid for 5 years with 180-day stays per entry.', type: 'new' },
    { date: 'Dec 2024', country: '🇩🇪 Germany', title: 'Schengen border checks extended', desc: 'Germany extended internal Schengen border controls until mid-2025.', type: 'warn' },
  ];
}

// ─── VISA RULES ──────────────────────────────────────────────────────────────
// Reads from D1 SQLite database
async function handleVisaRules(request, env, ctx, json) {
  const url = new URL(request.url);
  const from = url.searchParams.get('from');
  const to = url.searchParams.get('to');

  if (!from && !to) {
    return json({ error: 'Provide from and/or to query params' }, 400);
  }

  if (env.DB) {
    try {
      let stmt, results;
      if (from && to) {
        stmt = env.DB.prepare('SELECT * FROM visa_rules WHERE from_country = ? AND to_country = ?');
        results = await stmt.bind(from.toUpperCase(), to.toUpperCase()).all();
      } else if (from) {
        stmt = env.DB.prepare('SELECT * FROM visa_rules WHERE from_country = ?');
        results = await stmt.bind(from.toUpperCase()).all();
      } else {
        stmt = env.DB.prepare('SELECT * FROM visa_rules WHERE to_country = ?');
        results = await stmt.bind(to.toUpperCase()).all();
      }
      return json(results.results || []);
    } catch (err) {
      console.error('D1 query failed:', err);
    }
  }

  // Fallback: serve static JSON file
  return json({ error: 'Database unavailable — use /data/visa-rules.json' }, 503);
}

// ─── SUBSCRIBE ───────────────────────────────────────────────────────────────
async function handleSubscribe(request, env, ctx, json) {
  const body = await request.json().catch(() => null);
  if (!body || !body.email) return json({ error: 'Email required' }, 400);

  const email = body.email.trim().toLowerCase();
  const countries = (body.countries || []).join(',');

  // Store in D1
  if (env.DB) {
    try {
      await env.DB.prepare(
        'INSERT OR REPLACE INTO subscribers (email, countries, created_at) VALUES (?, ?, ?)'
      ).bind(email, countries, new Date().toISOString()).run();
    } catch (err) {
      console.error('Subscribe D1 error:', err);
    }
  }

  // Also store in KV as a quick lookup
  if (env.KV) {
    ctx.waitUntil(env.KV.put(`sub:${email}`, countries, { expirationTtl: 365 * 24 * 3600 }));
  }

  return json({ success: true, message: 'Subscribed successfully' });
}

// ─── CONTACT ─────────────────────────────────────────────────────────────────
async function handleContact(request, env, ctx, json) {
  const body = await request.json().catch(() => null);
  if (!body || !body.email || !body.message) return json({ error: 'Missing fields' }, 400);

  // Store in D1
  if (env.DB) {
    try {
      await env.DB.prepare(
        'INSERT INTO contact_messages (name, email, subject, message, created_at) VALUES (?, ?, ?, ?, ?)'
      ).bind(
        body.name || '',
        body.email,
        body.subject || 'other',
        body.message,
        new Date().toISOString()
      ).run();
    } catch (err) {
      console.error('Contact D1 error:', err);
    }
  }

  return json({ success: true });
}
