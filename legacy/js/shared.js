// shared.js — VISA RADAR

function getNav(activePage) {
  return `
  <nav class="nav">
    <a href="/index.html" class="nav-logo">
      <div class="radar-icon"><div class="dot"></div></div>
      <span class="name">VISA</span><span class="sep"> </span><span style="color:var(--gold)">RADAR</span>
    </a>
    <div class="nav-links">
      <a href="/index.html" class="${activePage==='home'?'active':''}">Map</a>
      <a href="/calculator.html" class="${activePage==='calc'?'active':''}">Calculator</a>
      <a href="/compare.html" class="${activePage==='compare'?'active':''}">Compare</a>
      <a href="/border-wait.html" class="${activePage==='border'?'active':''}">Border Waits</a>
      <a href="/alerts.html" class="${activePage==='alerts'?'active':''}">Alerts</a>
      <a href="/alerts.html" class="nav-cta btn btn-sm">Get Alerts</a>
    </div>
  </nav>`;
}

function getFooter() {
  return `
  <footer class="footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-col">
          <div style="font-family:var(--font-display);font-size:1rem;font-weight:900;letter-spacing:0.15em;color:var(--text);margin-bottom:14px">
            VISA <span style="color:var(--gold)">RADAR</span>
          </div>
          <p>Live global visa &amp; border intelligence. Real data from 195 governments, updated continuously.</p>
          <p class="mt-3" style="font-size:0.75rem;color:var(--text3)">Data sourced from official government portals, embassy RSS feeds, and US CBP. Always verify with the official embassy before travel.</p>
        </div>
        <div class="footer-col">
          <h4>Tools</h4>
          <a href="/calculator.html">Visa Calculator</a>
          <a href="/compare.html">Passport Compare</a>
          <a href="/border-wait.html">Border Wait Times</a>
          <a href="/alerts.html">Policy Alerts</a>
        </div>
        <div class="footer-col">
          <h4>Countries</h4>
          <a href="/country.html?c=US">United States</a>
          <a href="/country.html?c=GB">United Kingdom</a>
          <a href="/country.html?c=AE">UAE</a>
          <a href="/country.html?c=DE">Germany</a>
          <a href="/country.html?c=JP">Japan</a>
        </div>
        <div class="footer-col">
          <h4>Company</h4>
          <a href="/about.html">About</a>
          <a href="/contact.html">Contact</a>
          <a href="/privacy.html">Privacy Policy</a>
        </div>
      </div>
      <div class="footer-bottom">
        <p>© 2025 VISA RADAR · All rights reserved</p>
        <p>Data is informational only · Always verify with official embassy sources</p>
      </div>
    </div>
  </footer>`;
}

function renderShared(activePage) {
  const navEl = document.getElementById('nav-placeholder');
  const footerEl = document.getElementById('footer-placeholder');
  if (navEl) navEl.outerHTML = getNav(activePage);
  if (footerEl) footerEl.outerHTML = getFooter();
}

function loadCookiebot() {
  const s = document.createElement('script');
  s.id = 'Cookiebot';
  s.src = 'https://consent.cookiebot.com/uc.js';
  s.setAttribute('data-cbid', 'REPLACE_WITH_COOKIEBOT_ID');
  s.setAttribute('data-blockingmode', 'auto');
  s.type = 'text/javascript';
  document.head.prepend(s);
}

function loadAdSense() {
  const s = document.createElement('script');
  s.async = true;
  s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-REPLACE_WITH_PUB_ID';
  s.crossOrigin = 'anonymous';
  document.head.appendChild(s);
}

document.addEventListener('DOMContentLoaded', () => {
  // loadCookiebot(); // Uncomment when Cookiebot ID is set
  // loadAdSense();   // Uncomment when AdSense approved
});
