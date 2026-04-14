// ── Page nav ──────────────────────────────────────────────────────────────
function switchPage(id, btn) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('page-' + id).classList.add('active');
  btn.classList.add('active');
}

// ── Seg helper ────────────────────────────────────────────────────────────
function segOn(btn) {
  btn.parentElement.querySelectorAll('button').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}

// ── Compress sub-tabs ─────────────────────────────────────────────────────
function switchComp(id, btn) {
  document.querySelectorAll('#page-compress .comp-sub').forEach(s => s.classList.remove('active'));
  document.getElementById('cs-' + id).classList.add('active');
  segOn(btn);
}

// ── Create sub-tabs ───────────────────────────────────────────────────────
function switchCreate(id, btn) {
  document.querySelectorAll('#page-create .comp-sub').forEach(s => s.classList.remove('active'));
  document.getElementById('cc-' + id).classList.add('active');
  segOn(btn);
}

// ── Drop zone (images) ────────────────────────────────────────────────────
function dzOver(e)  { e.preventDefault(); document.getElementById('dz').classList.add('over'); }
function dzLeave()  { document.getElementById('dz').classList.remove('over'); }
function dzDrop(e)  { e.preventDefault(); dzLeave(); nacist(e.dataTransfer.files[0]); }

// ── Drop zone (pfx extract) ───────────────────────────────────────────────
function pfxDzOver(e)  { e.preventDefault(); document.getElementById('dz-pfx').classList.add('over'); }
function pfxDzLeave()  { document.getElementById('dz-pfx').classList.remove('over'); }
function pfxDzDrop(e)  { e.preventDefault(); pfxDzLeave(); nacistPfx(e.dataTransfer.files[0]); }

// ── Drop zone (wrap) ──────────────────────────────────────────────────────
function wrapDzOver(e, id) { e.preventDefault(); document.getElementById(id).classList.add('over'); }
function wrapDzLeave(id) { document.getElementById(id).classList.remove('over'); }
function wrapDzDrop(e, kind) { e.preventDefault(); wrapDzLeave('dz-wrap-' + kind); nacistWrapSoubor(kind, e.dataTransfer.files[0]); }

// ── Shared image state ────────────────────────────────────────────────────
let img = null, imgNazev = 'obrazek';
let compFmt = 'jpg', reformatFmt = 'png';

function nacist(file) {
  if (!file || !file.type.startsWith('image/')) return;
  imgNazev = file.name.replace(/\.[^.]+$/, '');
  const reader = new FileReader();
  reader.onload = e => {
    const i = new Image();
    i.onload = () => {
      img = i;
      document.getElementById('comp-nastaveni').style.display = '';
      document.getElementById('dz').querySelector('p').innerHTML = '✅ <strong>' + file.name + '</strong>';
      const rf = document.getElementById('rf-nazev');
      if (rf) rf.textContent = file.name;
      renderOrig();
      refresh();
    };
    i.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

// ── COMPRESS ──────────────────────────────────────────────────────────────
function setFmt(f, btn) {
  compFmt = f;
  segOn(btn);
  document.getElementById('row-qual').style.display = f === 'jpg' ? '' : 'none';
  refresh();
}

function renderOrig() {
  const c = document.getElementById('cv-orig');
  c.width = img.width; c.height = img.height;
  c.getContext('2d').drawImage(img, 0, 0);
  document.getElementById('m-orig-dim').textContent = img.width + ' × ' + img.height + ' px';
  c.toBlob(b => { document.getElementById('m-orig-sz').textContent = fmtBytes(b.size); }, 'image/png');
}

function refresh() {
  if (!img) return;
  const pct  = +document.getElementById('sl-res').value;
  const qual = +document.getElementById('sl-qual').value;
  document.getElementById('vl-res').textContent  = pct  + '%';
  document.getElementById('vl-qual').textContent = qual + '%';

  const nW = Math.max(1, Math.round(img.width  * pct / 100));
  const nH = Math.max(1, Math.round(img.height * pct / 100));
  const c  = document.getElementById('cv-out');
  c.width = nW; c.height = nH;
  c.getContext('2d').drawImage(img, 0, 0, nW, nH);
  document.getElementById('m-out-dim').textContent = nW + ' × ' + nH + ' px';

  const mime = compFmt === 'png' ? 'image/png' : 'image/jpeg';
  const q    = compFmt === 'jpg' ? qual / 100 : undefined;
  c.toBlob(b => { document.getElementById('m-out-sz').textContent = fmtBytes(b.size); }, mime, q);
}

function stahnoutComp() {
  if (!img) return;
  const pct  = +document.getElementById('sl-res').value;
  const qual = +document.getElementById('sl-qual').value;
  const nW   = Math.max(1, Math.round(img.width  * pct / 100));
  const nH   = Math.max(1, Math.round(img.height * pct / 100));
  const c    = document.createElement('canvas');
  c.width = nW; c.height = nH;
  c.getContext('2d').drawImage(img, 0, 0, nW, nH);
  const mime = compFmt === 'png' ? 'image/png' : 'image/jpeg';
  const ext  = compFmt === 'png' ? 'png' : 'jpg';
  const q    = compFmt === 'jpg' ? qual / 100 : undefined;
  c.toBlob(b => dl(b, imgNazev + '_comp.' + ext), mime, q);
}

// ── REFORMAT ──────────────────────────────────────────────────────────────
function setReformat(f, btn) { reformatFmt = f; segOn(btn); }

function stahnoutReformat() {
  if (!img) return;
  const c = document.createElement('canvas');
  c.width = img.width; c.height = img.height;
  c.getContext('2d').drawImage(img, 0, 0);
  const mime = reformatFmt === 'png' ? 'image/png' : 'image/jpeg';
  const ext  = reformatFmt === 'png' ? 'png' : 'jpg';
  const q    = reformatFmt === 'jpg' ? 0.92 : undefined;
  c.toBlob(b => dl(b, imgNazev + '.' + ext), mime, q);
}

// ── CONVERT: Base64 ───────────────────────────────────────────────────────
let b64Fmt = 'pdf';

function prepnout(f, btn) {
  b64Fmt = f;
  segOn(btn);
  document.getElementById('b64-lbl').textContent = f.toUpperCase();
  document.getElementById('err-b64').textContent = '';
}

function prevest() {
  const err = document.getElementById('err-b64');
  err.textContent = '';
  let b64 = document.getElementById('b64-vstup').value.trim().replace(/^data:[^;]+;base64,/, '');
  try {
    const bin = atob(b64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    const mimes = { pdf:'application/pdf', png:'image/png', jpg:'image/jpeg', jpeg:'image/jpeg' };
    dl(new Blob([bytes], { type: mimes[b64Fmt] }), 'zZToolExport.' + b64Fmt);
  } catch { err.textContent = 'Chyba: Neplatný base64 řetězec.'; }
}

// ── CREATE: PFX (self-signed, browser) ────────────────────────────────────
async function vytvorPfx() {
  const err  = document.getElementById('err-pfx-make');
  const btn  = document.getElementById('btn-make-pfx');
  err.textContent = '';

  const cn   = document.getElementById('pfx-cn').value.trim();
  const o    = document.getElementById('pfx-o').value.trim();
  const ou   = document.getElementById('pfx-ou').value.trim();
  const l    = document.getElementById('pfx-l').value.trim();
  const st   = document.getElementById('pfx-st').value.trim();
  const c    = document.getElementById('pfx-c').value.trim().toUpperCase();
  const bits = +document.getElementById('pfx-bits').value;
  const days = +document.getElementById('pfx-days').value;
  const pass = document.getElementById('pfx-pass').value;
  const pass2= document.getElementById('pfx-pass2').value;

  if (!cn)           { err.textContent = 'Common Name (CN) je povinný.'; return; }
  if (!pass)         { err.textContent = 'Heslo je povinné.'; return; }
  if (pass !== pass2){ err.textContent = 'Hesla se neshodují.'; return; }
  if (days < 1)      { err.textContent = 'Platnost musí být alespoň 1 den.'; return; }

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Generuji…';
  await new Promise(r => setTimeout(r, 30));

  try {
    const pki  = forge.pki;
    const keys = pki.rsa.generateKeyPair({ bits, e: 0x10001 });
    const cert = pki.createCertificate();

    cert.publicKey  = keys.publicKey;
    cert.serialNumber = forge.util.bytesToHex(forge.random.getBytesSync(16));

    const now = new Date();
    cert.validity.notBefore = now;
    cert.validity.notAfter  = new Date(now.getTime() + days * 86400000);

    const attrs = [{ name:'commonName', value: cn }];
    if (o)  attrs.push({ name:'organizationName',       value: o });
    if (ou) attrs.push({ name:'organizationalUnitName', value: ou });
    if (l)  attrs.push({ name:'localityName',            value: l });
    if (st) attrs.push({ name:'stateOrProvinceName',     value: st });
    if (c)  attrs.push({ name:'countryName',             value: c });

    cert.setSubject(attrs);
    cert.setIssuer(attrs);

    cert.setExtensions([
      { name:'basicConstraints', cA: true },
      { name:'keyUsage', keyCertSign: true, digitalSignature: true, nonRepudiation: true,
        keyEncipherment: true, dataEncipherment: true },
      { name:'extKeyUsage', serverAuth: true, clientAuth: true },
      { name:'subjectKeyIdentifier' }
    ]);

    cert.sign(keys.privateKey, forge.md.sha256.create());

    const p12  = forge.pkcs12.toPkcs12Asn1(keys.privateKey, [cert], pass,
                   { generateLocalKeyId: true, friendlyName: cn });
    const der  = forge.asn1.toDer(p12).getBytes();
    const bytes = new Uint8Array(der.length);
    for (let i = 0; i < der.length; i++) bytes[i] = der.charCodeAt(i);

    dl(new Blob([bytes], { type: 'application/x-pkcs12' }), (cn || 'certifikat') + '.pfx');
  } catch (e) {
    err.textContent = 'Chyba při generování: ' + (e && e.message ? e.message : String(e));
  }

  btn.disabled = false;
  btn.innerHTML = '✦ Vygenerovat a stáhnout .pfx';
}

// ── EXTRACT: PFX (browser) ────────────────────────────────────────────────
let pfxBytes = null;

function nacistPfx(file) {
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    pfxBytes = e.target.result;
    document.getElementById('dz-pfx').querySelector('p').innerHTML =
      '✅ <strong>' + file.name + '</strong>';
    ['out-cert','out-key','out-chain'].forEach(id =>
      document.getElementById(id).classList.remove('visible'));
    document.getElementById('err-pfx-ext').textContent = '';
  };
  reader.readAsBinaryString(file);
}

function rozbalitPfx() {
  const err  = document.getElementById('err-pfx-ext');
  const btn  = document.getElementById('btn-ext-pfx');
  err.textContent = '';

  if (!pfxBytes) { err.textContent = 'Nejprve nahraj .pfx soubor.'; return; }

  const pass = document.getElementById('pfx-ext-pass').value;

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Rozbaluji…';

  setTimeout(() => {
    try {
      const p12Asn1 = forge.asn1.fromDer(pfxBytes);
      const p12     = forge.pkcs12.pkcs12FromAsn1(p12Asn1, pass);

      const certBags = p12.getBags({ bagType: forge.pki.oids.certBag });
      const certs    = (certBags[forge.pki.oids.certBag] || []).map(b => b.cert).filter(Boolean);

      const leaf  = certs[0];
      const chain = certs.slice(1);
      if (!leaf) throw new Error('V souboru nebyl nalezen žádný certifikát.');

      const keyBags = p12.getBags({ bagType: forge.pki.oids.pkcs8ShroudedKeyBag });
      const keyBag  = (keyBags[forge.pki.oids.pkcs8ShroudedKeyBag] || [])[0];
      const privKey = keyBag ? keyBag.key : null;

      ukazVystup('out-cert', 'out-cert-ta', forge.pki.certificateToPem(leaf));
      if (privKey) ukazVystup('out-key', 'out-key-ta', forge.pki.privateKeyToPem(privKey));
      if (chain.length > 0) {
        const chainPem = chain.map(cert => forge.pki.certificateToPem(cert)).join('\n');
        ukazVystup('out-chain', 'out-chain-ta', chainPem);
      }
    } catch(e) {
      const msg = (e && e.message) ? e.message : String(e);
      const lmsg = msg.toLowerCase();
      if (lmsg.includes('invalid') || lmsg.includes('decrypt') || lmsg.includes('mac') || lmsg.includes('password')) {
        err.textContent = 'Chyba: Špatné heslo nebo poškozený soubor.';
      } else {
        err.textContent = 'Chyba při rozbalování: ' + msg;
      }
    }

    btn.disabled = false;
    btn.innerHTML = '⊡ Rozbalit PFX';
  }, 30);
}

function ukazVystup(boxId, taId, text) {
  document.getElementById(taId).value = text;
  document.getElementById(boxId).classList.add('visible');
}

// ── WRAP: cert+key(+chain) → PFX (localhost API) ──────────────────────────
let wrapFiles = { cert: null, key: null, chain: null };

function nacistWrapSoubor(kind, file) {
  if (!file) return;
  wrapFiles[kind] = file;
  const dzId = (kind === 'cert') ? 'dz-wrap-cert' : (kind === 'key') ? 'dz-wrap-key' : 'dz-wrap-chain';
  const dz = document.getElementById(dzId);
  if (dz) dz.querySelector('p').innerHTML = '✅ <strong>' + file.name + '</strong>';
  document.getElementById('err-pfx-wrap').textContent = '';
}

async function updateWrapStatus() {
  const dot = document.getElementById('wrap-dot');
  const txt = document.getElementById('wrap-status-text');
  try {
    const r = await fetch('/api/health', { cache: 'no-store' });
    if (!r.ok) throw new Error('bad');
    dot.classList.add('ok');
    txt.textContent = 'Lokální služba běží (localhost).';
  } catch {
    dot.classList.remove('ok');
    txt.textContent = 'Lokální služba neběží. Spusť Flask/Streamlit podle nápovědy níže.';
  }
}

async function zabalitDoPfx() {
  const err = document.getElementById('err-pfx-wrap');
  const btn = document.getElementById('btn-wrap-pfx');
  err.textContent = '';

  if (!wrapFiles.cert) { err.textContent = 'Chybí certifikát.'; return; }
  if (!wrapFiles.key)  { err.textContent = 'Chybí privátní klíč.'; return; }

  const p1 = document.getElementById('wrap-pfx-pass').value;
  const p2 = document.getElementById('wrap-pfx-pass2').value;
  const kp = document.getElementById('wrap-key-pass').value;
  const fn = document.getElementById('wrap-friendly').value;

  if (!p1) { err.textContent = 'Heslo PFX je povinné.'; return; }
  if (p1 !== p2) { err.textContent = 'Hesla PFX se neshodují.'; return; }

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Balím…';

  try {
    const fd = new FormData();
    fd.append('cert', wrapFiles.cert, wrapFiles.cert.name);
    fd.append('key', wrapFiles.key, wrapFiles.key.name);
    if (wrapFiles.chain) fd.append('chain', wrapFiles.chain, wrapFiles.chain.name);

    fd.append('pfxPassword', p1);
    fd.append('pfxPassword2', p2);
    if (kp) fd.append('keyPassword', kp);
    if (fn) fd.append('friendlyName', fn);

    const r = await fetch('/api/wrap-pfx', { method: 'POST', body: fd });
    if (!r.ok) {
      const msg = await r.text();
      throw new Error(msg || 'Neplatné vstupy.');
    }

    const blob = await r.blob();
    // Try to read filename from Content-Disposition
    let filename = 'certifikat.pfx';
    const cd = r.headers.get('Content-Disposition') || '';
    const m = cd.match(/filename=\"([^\"]+)\"/);
    if (m && m[1]) filename = m[1];
    dl(blob, filename);
  } catch (e) {
    err.textContent = (e && e.message) ? e.message : String(e);
  }

  btn.disabled = false;
  btn.innerHTML = '⧉ Zabalit a stáhnout .pfx';
  updateWrapStatus();
}

// ── Helpers ───────────────────────────────────────────────────────────────
function dl(blob, name) {
  const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: name });
  a.click(); URL.revokeObjectURL(a.href);
}

function fmtBytes(b) {
  return b < 1024 ? b + ' B' : b < 1048576 ? (b/1024).toFixed(1) + ' KB' : (b/1048576).toFixed(2) + ' MB';
}

function kopirovat(taId, btn) {
  const ta = document.getElementById(taId);
  navigator.clipboard.writeText(ta.value).then(() => {
    const orig = btn.innerHTML;
    btn.innerHTML = '✓ Zkopírováno';
    setTimeout(() => { btn.innerHTML = orig; }, 1800);
  });
}

function stahnoutText(taId, filename) {
  const text = document.getElementById(taId).value;
  dl(new Blob([text], { type: 'text/plain' }), filename);
}

// on load
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('wrap-status')) updateWrapStatus();
});

