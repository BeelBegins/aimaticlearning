const http=require('http'),fs=require('fs'),path=require('path');
const {chromium}=require(process.env.PLAYWRIGHT_PATH || 'playwright');
const PUB=path.join(__dirname,'..','..','aimaticlearning','public');
const S=__dirname; fs.mkdirSync(S+'/shots',{recursive:true});
const srv=http.createServer((q,r)=>{
  const u=q.url.split('?')[0];
  if(u.startsWith('/lms/quiz/')){r.setHeader('content-type','text/html');return r.end(fs.readFileSync(S+'/harness.html'));}
  if(u.startsWith('/assets/aimaticlearning/')){const f=path.join(PUB,u.replace('/assets/aimaticlearning/',''));
    if(fs.existsSync(f)){r.setHeader('content-type',f.endsWith('.css')?'text/css':'application/javascript');return r.end(fs.readFileSync(f));}}
  r.statusCode=404;r.end();
}).listen(18765);
const res=[];const ok=(n,c,d='')=>{res.push((c?'PASS ':'FAIL ')+n+(d?' | '+d:''));};
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROME_PATH,args:['--no-sandbox']});
 const ctx=await b.newContext({viewport:{width:1100,height:760}});
 const p=await ctx.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>m.type()==='error'&&errs.push(m.text()));
 const U='http://localhost:18765/lms/quiz/mock-test';
 const shot=n=>p.screenshot({path:S+'/shots/'+n+'.png'});
 const cur=()=>p.evaluate(()=>{const e=[...document.querySelectorAll('.text-sm.text-ink-gray-5')].find(n=>/^Question\s+\d+/.test(n.textContent));return e?+e.textContent.match(/\d+/)[0]:0;});
 await p.goto(U); await p.waitForTimeout(500);
 await shot('01-start');
 // 1. Start asks style
 await p.click('#startbtn'); await p.waitForTimeout(300);
 ok('style modal on Start', await p.locator('.aimatic-style-choice').count()===1);
 await shot('02-modal');
 await p.click('[data-style=pearson]'); await p.waitForTimeout(700);
 ok('question 1 after pick', await cur()===1, 'cur='+await cur());
 ok('pearson bar visible', await p.locator('.aimatic-pearson-bar').first().isVisible());
 ok('no Skip button', await p.locator('text=/^Skip$/').count()===0);
 ok('option letters hidden', await p.locator('.aimatic-mcq-option-letter').first().isHidden());
 ok('old mark-for-review hidden', await p.locator('label:has-text("Mark for review")').first().isHidden());
 await p.waitForTimeout(300); await shot('03-q1');
 // select option 2 + flag + next
 await p.click('label:has-text("Irrationality")'); await p.click('.aimatic-pearson-review'); await p.waitForTimeout(300);
 ok('flag turns yellow', await p.$eval('.aimatic-pearson-review',e=>getComputedStyle(e).color)==='rgb(255, 255, 0)');
 await shot('04-flagged');
 await p.click('[data-pearson=next]'); await p.waitForTimeout(500);
 ok('Next moves to 2', await cur()===2, 'cur='+await cur());
 ok('Previous visible on Q2', await p.locator('[data-pearson=prev]').isVisible());
 // go to last
 for(let i=0;i<48;i++){await p.click('[data-pearson=next]'); await p.waitForTimeout(60);}
 ok('reached Q50', await cur()===50, 'cur='+await cur());
 await shot('05-q50');
 await p.click('[data-pearson=next]'); await p.waitForTimeout(500);
 ok('last Next opens review', await p.locator('.aimatic-pearson-review-screen').isVisible());
 ok('review rows = 50', await p.locator('.aimatic-pearson-row').count()===50, ''+await p.locator('.aimatic-pearson-row').count());
 ok('Q1 Answered', (await p.locator('.aimatic-pearson-row').nth(0).innerText()).includes('Answered'));
 ok('Q3 Incomplete', (await p.locator('.aimatic-pearson-row').nth(2).innerText()).includes('Incomplete'));
 await shot('06-review');
 await p.click('[data-filter=flagged]'); await p.waitForTimeout(200);
 ok('flagged filter shows Q1 only', await p.locator('.aimatic-pearson-row').count()===1);
 await p.click('[data-filter=all]');
 // jump far: row Question 3
 await p.locator('.aimatic-pearson-row').nth(2).click(); await p.waitForTimeout(1500);
 ok('row click jumps from 50 to 3', await cur()===3, 'cur='+await cur());
 ok('review closed after jump', !(await p.locator('.aimatic-pearson-review-screen').isVisible()));
 // End Test dialog
 for(let i=0;i<47;i++){await p.click('[data-pearson=next]'); await p.waitForTimeout(50);}
 await p.click('[data-pearson=next]'); await p.waitForTimeout(400);
 await p.click('[data-pearson=end]'); await p.waitForTimeout(600);
 const top=await p.evaluate(()=>{const d=document.querySelector('#dlgwrap [role=dialog]');if(!d)return 'nodialog';const r=d.getBoundingClientRect();const e=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);return d.contains(e)?'dialog-on-top':'covered:'+e.className;});
 ok('End Test confirm dialog above review', top==='dialog-on-top', top);
 await shot('07-end-dialog');
 await p.click('#dlgcancel'); await p.waitForTimeout(200);
 ok('cancel keeps review open', await p.locator('.aimatic-pearson-review-screen').isVisible());
 ok('no submit happened', !(await p.evaluate(()=>window.__SUBMITTED)));
 ok('Exit link present', await p.locator('.aimatic-pearson-exit').first().isVisible());
 // phone
 await p.setViewportSize({width:390,height:780}); await p.waitForTimeout(300); await shot('08-review-phone');
 await p.locator('.aimatic-pearson-row').nth(4).click(); await p.waitForTimeout(1500); await shot('09-q5-phone');
 // style asked again on a new Start (same tab/session storage)
 await p.setViewportSize({width:1100,height:760});
 await p.reload(); await p.waitForTimeout(500);
 await p.evaluate(()=>{/* harness reload returns to start screen */});
 await p.click('#startbtn'); await p.waitForTimeout(300);
 ok('modal asked again on 2nd Start', await p.locator('.aimatic-style-choice').count()===1);
 await p.click('[data-style=normal]'); await p.waitForTimeout(600);
 ok('normal: no pearson bar', !(await p.locator('.aimatic-pearson-bar').first().isVisible().catch(()=>false)));
 ok('normal: letters visible', await p.locator('.aimatic-mcq-option-letter').first().isVisible());
 await shot('10-normal');
 ok('no JS errors', errs.length===0, errs.slice(0,3).join(' || '));
 console.log(res.join('\n')); await b.close(); srv.close();
})().catch(e=>{console.log(res.join('\n'));console.log('CRASH',e.message);process.exit(1);});
