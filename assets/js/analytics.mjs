// Optional Google Analytics 4: never request Google's tag before a visitor opts in.
const MEASUREMENT_ID = 'G-HFKPWNKDBY';
const CHOICE_KEY = 'jp_analytics_consent_v1';
let started = false;
function currentChoice() {
  try { return localStorage.getItem(CHOICE_KEY); } catch { return null; }
}
function storeChoice(choice) {
  try { localStorage.setItem(CHOICE_KEY, choice); } catch { /* storage unavailable */ }
}
function startAnalytics() {
  if (started) return;
  started = true;
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', MEASUREMENT_ID, { anonymize_ip: true });
  const tag = document.createElement('script');
  tag.async = true;
  tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(MEASUREMENT_ID);
  tag.dataset.jobpathAnalytics = 'true';
  document.head.append(tag);
}
function removeExistingAnalyticsCookies() {
  for (const part of document.cookie.split(';')) {
    const name = part.trim().split('=')[0];
    if (/^_ga(?:_|$)/.test(name)) {
      document.cookie = name + '=; Max-Age=0; Path=/; SameSite=Lax';
    }
  }
}
function closeChoices() { document.getElementById('jobpath-analytics-choices')?.remove(); }
function showChoices() {
  closeChoices();
  const banner = document.createElement('aside');
  banner.id = 'jobpath-analytics-choices';
  banner.className = 'analytics-consent';
  banner.setAttribute('aria-label', 'Optional website analytics preferences');
  banner.innerHTML = '<div class="analytics-consent-text"><strong>Optional website analytics</strong><p>Allow Google Analytics to measure visits, page views and traffic sources? Google may use cookies and device data. The job portal works without analytics. <a href="/privacy-policy/">Privacy policy</a>.</p></div><div class="analytics-consent-actions"><button type="button" class="btn btn-primary" data-analytics-allow>Allow analytics</button><button type="button" class="btn btn-secondary" data-analytics-decline>Decline</button></div>';
  banner.querySelector('[data-analytics-allow]').addEventListener('click', () => {
    storeChoice('allow');
    closeChoices();
    startAnalytics();
  });
  banner.querySelector('[data-analytics-decline]').addEventListener('click', () => {
    const wasAllowed = currentChoice() === 'allow' || started;
    storeChoice('decline');
    removeExistingAnalyticsCookies();
    closeChoices();
    if (wasAllowed) window.location.reload();
  });
  document.body.append(banner);
}
document.addEventListener('click', event => {
  if (event.target.closest?.('[data-analytics-choices]')) {
    event.preventDefault();
    showChoices();
  }
});
if (currentChoice() === 'allow') {
  startAnalytics();
} else if (currentChoice() === null) {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', showChoices, { once: true });
  } else {
    showChoices();
  }
}
