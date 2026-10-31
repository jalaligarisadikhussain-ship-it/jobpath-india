/* JobPath India: apply-only gateway. No third-party ad code is injected here. */
export const WAIT_MS = 5000;
export function secureDestination(value) {
  try {
    const u = new URL(value);
    return u.protocol === 'https:' && !u.username && !u.password ? u.href : null;
  } catch { return null; }
}
export function secondsLeft(start, now) {
  return Math.max(0, Math.ceil((WAIT_MS - Math.max(0, now - start)) / 1000));
}
export function plainClick(e) {
  return e.button === 0 && !e.defaultPrevented && !e.altKey &&
    !e.ctrlKey && !e.metaKey && !e.shiftKey;
}
const markup = [
'<div class="jp-gw" id="jp-apply-gateway" hidden>',
' <div class="jp-gw-scrim" aria-hidden="true"></div>',
' <section class="jp-gw-panel" role="dialog" aria-modal="true" aria-labelledby="jp-gw-title">',
'  <header class="jp-gw-top"><div class="jp-gw-logo">JP</div><div class="jp-gw-brand">JOBPATH INDIA<small>Independent recruitment information</small></div>',
'   <button type="button" class="jp-gw-close" data-gw-close aria-label="Cancel and return">✕</button></header>',
'  <div class="jp-gw-body"><p class="jp-gw-kicker">CONTINUE TO OFFICIAL RECRUITMENT</p>',
'  <h2 id="jp-gw-title" tabindex="-1">Your job link is ready</h2>',
'  <p class="jp-gw-intro">This short sponsored pause helps support free job information. Advertising is never an official application link, and ad clicks are not required.</p>',
'  <section class="jp-gw-ad" aria-label="Advertisement space">',
'   <div class="jp-gw-ad-label"><strong>ADVERTISEMENT</strong><span>Not affiliated with the recruiting authority</span></div>',
'   <div class="jp-gw-slot" data-gw-slot><span>Reserved for an approved advertising placement</span></div>',
'  </section>',
'  <div class="jp-gw-bottom"><div class="jp-gw-count"><div class="jp-gw-ring" data-gw-ring><span data-gw-number>5</span></div>',
'   <div><strong data-gw-label>Continue in 5 seconds</strong><p>Destination: <span data-gw-host></span></p></div></div>',
'   <button type="button" class="jp-gw-next" data-gw-next disabled>Skip Ad / Continue to Job ↗</button>',
'   <p class="jp-gw-note" data-gw-note role="status" aria-live="polite">You can cancel at any time.</p>',
'  </div></div></section></div>'
].join('');

export function installApplyGateway({enabled = false, resolveLink, shouldGate, mountApprovedAd} = {}) {
  if (!enabled || typeof document === 'undefined' || typeof resolveLink !== 'function') return () => {};
  const wrapper = document.createElement('div');
  wrapper.innerHTML = markup;
  const dialog = wrapper.firstElementChild;
  document.body.append(dialog);
  const $ = s => dialog.querySelector(s);
  const next = $('[data-gw-next]'), closeButton = $('[data-gw-close]');
  const number = $('[data-gw-number]'), label = $('[data-gw-label]');
  const ring = $('[data-gw-ring]'), note = $('[data-gw-note]');
  const slot = $('[data-gw-slot]'), title = $('#jp-gw-title');
  let active = false, start = 0, target = '', timer = 0, source = null;
  let oldOverflow = '', previousInert = false;

  function tick() {
    if (!active) return;
    const elapsed = performance.now() - start, left = secondsLeft(start, performance.now());
    number.textContent = String(left);
    label.textContent = left ? 'Continue in ' + left + ' second' + (left === 1 ? '' : 's') : 'Ready to continue';
    ring.style.setProperty('--elapsed', Math.min(100, elapsed / WAIT_MS * 100) + '%');
    if (left === 0) {
      next.disabled = false;
      note.textContent = 'Continue is now available. No ad click is needed.';
      return;
    }
    timer = window.setTimeout(tick, Math.min(100, Math.max(10, WAIT_MS - elapsed)));
  }
  function dismiss() {
    if (!active) return;
    active = false;
    window.clearTimeout(timer);
    dialog.hidden = true;
    document.body.style.overflow = oldOverflow;
    const app = document.getElementById('app');
    if (app) app.inert = previousInert;
    target = '';
    if (source && source.isConnected) source.focus();
    source = null;
  }
  function show(url, anchor) {
    target = url;
    source = anchor;
    oldOverflow = document.body.style.overflow;
    const app = document.getElementById('app');
    previousInert = Boolean(app && app.inert);
    if (app) app.inert = true;
    document.body.style.overflow = 'hidden';
    $('[data-gw-host]').textContent = new URL(url).hostname;
    slot.replaceChildren();
    const placeholder = document.createElement('span');
    placeholder.textContent = 'Reserved for an approved advertising placement';
    slot.append(placeholder);
    if (typeof mountApprovedAd === 'function') {
      try { mountApprovedAd(slot); } catch (error) { console.warn('Gateway ad unavailable', error); }
    }
    next.disabled = true;
    note.textContent = 'You can cancel at any time.';
    dialog.hidden = false;
    active = true;
    start = performance.now();
    title.focus({preventScroll:true});
    tick();
  }
  function onClick(event) {
    if (active || !plainClick(event)) return;
    const anchor = event.target instanceof Element ? event.target.closest('a[data-jobpath-apply]') : null;
    if (!anchor || (shouldGate && !shouldGate())) return;
    const approved = secureDestination(resolveLink(anchor));
    if (!approved || approved !== secureDestination(anchor.href)) return;
    event.preventDefault();
    show(approved, anchor);
  }
  function onKey(event) {
    if (!active) return;
    if (event.key === 'Escape') { event.preventDefault(); dismiss(); }
    else if (event.key === 'Tab') {
      const controls = next.disabled ? [closeButton] : [closeButton, next];
      const current = controls.indexOf(document.activeElement);
      const index = event.shiftKey ? (current <= 0 ? controls.length-1 : current-1) :
        (current < 0 || current === controls.length-1 ? 0 : current+1);
      event.preventDefault(); controls[index].focus();
    }
  }
  function continueToJob() {
    if (!active || next.disabled || secondsLeft(start, performance.now()) !== 0) return;
    const url = target;
    dismiss();
    window.location.assign(url);
  }
  function onVisibility() { if (active) { window.clearTimeout(timer); tick(); } }
  document.addEventListener('click', onClick, true);
  document.addEventListener('keydown', onKey, true);
  document.addEventListener('visibilitychange', onVisibility);
  closeButton.addEventListener('click', dismiss);
  next.addEventListener('click', continueToJob);
  return () => {
    dismiss();
    document.removeEventListener('click', onClick, true);
    document.removeEventListener('keydown', onKey, true);
    document.removeEventListener('visibilitychange', onVisibility);
    dialog.remove();
  };
}
