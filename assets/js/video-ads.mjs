/**
 * Optional professional outstream video ad placement for JobPath India.
 * No network request, placeholder or video is created until ALL approval gates pass.
 * This is a provider-iframe adapter only. Script/VAST tags require an approved
 * provider-specific implementation; do not put VAST URLs into embedUrl.
 */
export function isVideoConfigReady(cfg, hostname='') {
  if (hostname !== 'jobpath-india.pages.dev' ||
      cfg?.enabled !== true || cfg?.status !== 'approved' ||
      !['vdo.ai','ex.co','primis','direct-sponsor'].includes(cfg.provider) ||
      cfg?.mode !== 'provider-iframe' || cfg.publisherApproved !== true ||
      cfg.categoryExclusionsConfirmed !== true ||
      cfg.mutedPlaybackVerified !== true || cfg.closeControlVerified !== true ||
      cfg.requiresExplicitOptIn !== true ||
      typeof cfg.embedUrl !== 'string' || typeof cfg.embedHost !== 'string' ||
      !cfg.embedHost || !cfg.embedUrl) return false;
  try {
    const u = new URL(cfg.embedUrl);
    return u.protocol === 'https:' && !u.username && !u.password &&
      u.hostname === cfg.embedHost && u.hostname !== hostname &&
      !u.hostname.endsWith('.pages.dev') && u.hostname !== 'localhost';
  } catch { return false; }
}
export function mountProfessionalVideo(cfg, consent, doc=globalThis.document, win=globalThis.window) {
  if (!isVideoConfigReady(cfg, win?.location?.hostname) ||
      consent !== 'allow' || win?.navigator?.globalPrivacyControl === true ||
      !doc?.querySelector || !doc?.createElement) return false;
  const main = doc.querySelector('#main .wrap');
  if (!main || main.querySelector?.('#jp-professional-video')) return false;
  const aside = doc.createElement('aside');
  aside.id = 'jp-professional-video';
  aside.setAttribute('aria-label','Video advertisement');
  aside.style.cssText = 'max-width:620px;margin:28px auto;padding:14px;border:1px solid #b7c6d7;border-radius:14px;background:transparent';
  const top = doc.createElement('div');
  top.style.cssText = 'display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:9px';
  const label = doc.createElement('strong');
  label.textContent = 'Video Advertisement';
  const close = doc.createElement('button');
  close.type = 'button';
  close.textContent = 'Close video ad';
  close.setAttribute('aria-label','Close video advertisement');
  close.style.cssText = 'border:1px solid #889ab0;border-radius:8px;background:transparent;color:inherit;padding:6px 10px;cursor:pointer';
  close.addEventListener('click', () => aside.remove());
  top.append(label,close);
  const frame = doc.createElement('iframe');
  frame.src = cfg.embedUrl;
  frame.title = 'Sponsored video advertisement';
  frame.loading = 'lazy';
  frame.referrerPolicy = 'strict-origin-when-cross-origin';
  frame.setAttribute('allow','autoplay');
  frame.setAttribute('sandbox','allow-scripts allow-same-origin');
  frame.style.cssText = 'display:block;border:0;width:100%;aspect-ratio:16/9;max-height:350px;background:transparent';
  aside.append(top,frame);
  const anchor = main.querySelector?.('#auto-notices') || main.querySelector?.('.section');
  if (anchor?.after) anchor.after(aside);
  else main.appendChild(aside);
  return true;
}
