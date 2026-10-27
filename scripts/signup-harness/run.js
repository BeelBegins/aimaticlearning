// Browser check of the one-sitting signup form with the server stubbed. See docs/signup-flow.md.
const http = require('http'), fs = require('fs'), path = require('path'), cp = require('child_process');
const { chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright');
const S = __dirname, ROOT = path.join(S, '..', '..'), PUB = path.join(ROOT, 'aimaticlearning', 'public');
const OUT = process.env.OUT_DIR || S; fs.mkdirSync(OUT + '/shots', { recursive: true });
const rendered = OUT + '/form.html';
cp.execFileSync(process.env.PYTHON || 'python3', [S + '/render.py', rendered]);
const JQ = process.env.JQUERY || path.join(ROOT, '..', 'frappe', 'node_modules', 'jquery', 'dist', 'jquery.min.js');
const page = () => `<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="stylesheet" href="/assets/aimaticlearning/css/examic_login.css"></head>
<body data-path="login"><section class="for-login"><div class="examic-login-notice hidden"></div><input id="login_email"><input id="login_password"></section>
<section class="for-signup">${fs.readFileSync(rendered, 'utf8').replace(/<script>[\s\S]*<\/script>/, '')}</section>
<script src="/jq.js"></script>
<script>
window.__calls = [];
window.frappe = { ready: f => $(f), call: o => { window.__calls.push({ method: o.method, args: o.args });
  const a = window.__answer(o.method, o.args); setTimeout(() => a.error ? o.error() : o.callback({ message: a }), 20); } };
window.validate_email = e => /^\\S+@\\S+\\.\\S+$/.test(e); window.cint = x => parseInt(x, 10) || 0;
window.__answer = () => ({});
</script>
<script>${fs.readFileSync(rendered, 'utf8').match(/<script>([\s\S]*)<\/script>/)[1]}</script></body></html>`;
const srv = http.createServer((q, r) => {
  const u = q.url.split('?')[0];
  if (u === '/favicon.ico') { r.statusCode = 204; return r.end(); }
  if (u === '/jq.js') { r.setHeader('content-type', 'application/javascript'); return r.end(fs.readFileSync(JQ)); }
  if (u.startsWith('/assets/aimaticlearning/')) { const f = path.join(PUB, u.replace('/assets/aimaticlearning/', '')); if (fs.existsSync(f)) { r.setHeader('content-type', 'text/css'); return r.end(fs.readFileSync(f)); } }
  if (u.startsWith('/card')) { r.setHeader('content-type', 'text/html'); return r.end('<h1>stripe</h1>'); }
  r.setHeader('content-type', 'text/html'); r.end(page());
}).listen(18766);
const res = []; const ok = (n, c, d = '') => res.push((c ? 'PASS ' : 'FAIL ') + n + (d ? ' | ' + d : ''));
(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME_PATH, args: ['--no-sandbox'] });
  const ctx = await b.newContext({ viewport: { width: 420, height: 900 } });
  const p = await ctx.newPage(); const errs = [];
  p.on('pageerror', e => errs.push(e.message)); p.on('console', m => m.type() === 'error' && errs.push(m.text()));
  const U = 'http://localhost:18766/';
  const shot = n => p.screenshot({ path: OUT + '/shots/' + n + '.png', fullPage: true });
  const calls = () => p.evaluate(() => window.__calls.map(c => c.method.split('.').pop()));
  const answer = body => p.evaluate(b => { window.__answer = (m, a) => (typeof b === 'function' ? b(m, a) : b); }, body);
  const fill = async () => {
    await p.fill('#signup_fullname', 'Jane Doe'); await p.fill('#signup_email', 'jane@example.com');
    await p.fill('#signup_password', 'correct horse'); await p.check('#signup-terms');
  };
  await p.goto(U); await p.waitForTimeout(300);
  await shot('01-empty');
  ok('Sign up disabled when empty', await p.locator('.btn-signup').isDisabled());
  ok('no step counters in copy', !/Step \d of/.test(await p.locator('.signup-form').innerText()));
  await fill();
  ok('Sign up enabled when filled', await p.locator('.btn-signup').isEnabled());
  await p.fill('#signup_password', 'short'); await p.click('.btn-signup');
  ok('short password blocked on the page, no server call', (await calls()).length === 0 && /at least 8/.test(await p.locator('#signup_password').locator('xpath=ancestor::div[contains(@class,"form-group")]').innerText()));
  await p.fill('#signup_password', 'correct horse');
  // sent
  await p.evaluate(() => { window.__answer = () => ({ status: 'sent', email: 'jane@example.com', wait: 3, expires_in: 900 }); });
  await p.click('.btn-signup'); await p.waitForTimeout(250);
  const sent = p.locator('#signup-sent');
  ok('notice visible', await sent.isVisible());
  const txt = await sent.innerText();
  ok('notice names the address', txt.includes('jane@example.com'));
  ok('notice says inbox and spam folder', /inbox/i.test(txt) && /spam/i.test(txt));
  ok('notice is below the Sign up button in the page', await p.evaluate(() => !!(document.querySelector('.btn-signup').compareDocumentPosition(document.querySelector('#signup-sent')) & Node.DOCUMENT_POSITION_FOLLOWING)));
  const place = await p.evaluate(() => { const a = document.querySelector('.btn-signup').getBoundingClientRect(), n = document.querySelector('#signup-sent').getBoundingClientRect(); return { buttonBottom: a.bottom, noticeTop: n.top, formTop: document.querySelector('.examic-signup-plans').getBoundingClientRect().top }; });
  ok('notice sits under the plan and details block', place.noticeTop > place.formTop);
  ok('details are locked while the code is pending', await p.locator('#signup_email').isDisabled() && await p.locator('#signup_password').isDisabled());
  ok('role=status for screen readers', await sent.getAttribute('role') === 'status');
  ok('resend is counting down', /in \d+s/.test(await p.locator('.examic-signup-resend').innerText()) && await p.locator('.examic-signup-resend').isDisabled());
  await shot('02-sent');
  await p.waitForTimeout(3300);
  ok('resend enabled after the wait', await p.locator('.examic-signup-resend').isEnabled());
  await p.click('.examic-signup-resend'); await p.waitForTimeout(150);
  ok('resend asks the server again', (await calls()).filter(c => c === 'request_signup_code').length === 2);
  // wrong code
  await answer({ status: 'wrong', left: 4, message: 'That code is not right. 4 tries left.' });
  await p.fill('#signup_code', '12'); await p.keyboard.press('Enter'); await p.waitForTimeout(100);
  ok('short code rejected without calling the server', !(await calls()).includes('verify_signup_code'));
  await p.fill('#signup_code', '123456'); await p.waitForTimeout(300);
  ok('wrong code shows the server message under the code box', /4 tries left/.test(await p.locator('.examic-signup-code').innerText()));
  ok('verify button usable again', await p.locator('.examic-signup-verify').isEnabled());
  await shot('03-wrong');
  // right code goes to the card page
  await p.route('http://localhost:18766/card**', r => r.fulfill({ contentType: 'text/html', body: '<h1>stripe</h1>' }));
  await answer({ status: 'ok', url: 'http://localhost:18766/card?s=1', billing: '/billing' });
  await p.fill('#signup_code', ''); await p.fill('#signup_code', '654321');
  await p.waitForURL('**/card**', { timeout: 3000 }).catch(() => {});
  ok('right code opens the card page', p.url().includes('/card'), p.url());
  // different email
  await p.goto(U); await fill();
  await p.evaluate(() => { window.__answer = () => ({ status: 'sent', email: 'jane@example.com', wait: 60 }); });
  await p.click('.btn-signup'); await p.waitForTimeout(200);
  await p.click('.examic-signup-change'); await p.waitForTimeout(100);
  ok('Use a different email unlocks the form and keeps the values', await p.locator('#signup_email').isEnabled() && await p.inputValue('#signup_email') === 'jane@example.com' && await p.locator('.btn-signup').isVisible() && !(await sent.isVisible()));
  // existing account
  await p.evaluate(() => { window.__answer = () => ({ status: 'exists', message: 'Already Registered' }); });
  await p.click('.btn-signup'); await p.waitForTimeout(200);
  ok('existing account sends the student to log in', (await p.evaluate(() => location.hash)) === '#login' && /already have an account/i.test(await p.locator('.examic-login-notice').innerText()));
  // error banner below the button
  await p.goto(U); await fill();
  await p.evaluate(() => { window.__answer = () => ({ status: 'mail_failed', message: 'We could not send the email.' }); });
  await p.click('.btn-signup'); await p.waitForTimeout(200);
  ok('send failure shows an error below the button and no sent notice', await p.locator('#signup-error').isVisible() && !(await p.locator('#signup-sent').isVisible()));
  await p.evaluate(() => { window.__answer = () => ({ error: 1 }); });
  await p.click('.btn-signup'); await p.waitForTimeout(200);
  ok('network failure shows a plain error', /could not reach/i.test(await p.locator('#signup-error').innerText()) && await p.locator('.btn-signup').isEnabled());
  ok('no horizontal scroll at 420px', await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  ok('no JS errors', errs.length === 0, errs.join(' ; '));
  console.log(res.join('\n')); console.log(res.filter(r => r.startsWith('FAIL')).length ? 'SOME FAILED' : 'ALL PASSED');
  await b.close(); srv.close();
})();
