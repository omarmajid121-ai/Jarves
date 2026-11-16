import asyncio, json, subprocess, time
from playwright.async_api import async_playwright
FIND=[]
def F(sev,area,msg): FIND.append((sev,area,msg)); print("  !!",sev,area,"-",msg)
srv=subprocess.Popen(["python3","-m","http.server","8767","--bind","127.0.0.1"],cwd=__import__("os").getcwd(),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
URL="http://127.0.0.1:8767/index.html"
async def go():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox","--use-fake-device-for-media-stream","--use-fake-ui-for-media-stream"])
        c=await b.new_context(viewport={"width":390,"height":844});pg=await c.new_page();errs=[];pg.on("pageerror",lambda e:errs.append(str(e)[:160]))
        await c.route("**/*googleapis.com/**",lambda r:r.fulfill(json={}));await c.route("**/api.open-meteo.com/**",lambda r:r.fulfill(json={}));await c.route("**/api.aladhan.com/**",lambda r:r.fulfill(json={}))
        # legacy data from before accounts
        await pg.goto(URL);await pg.evaluate("localStorage.clear()")
        await pg.evaluate("""localStorage.setItem('musaed.mem',JSON.stringify([{id:'m1',t:'يحب القهوة بدون سكر',d:Date.now()}]));localStorage.setItem('musaed.exp',JSON.stringify([{a:50,c:'مطاعم',x:'',d:Date.now()}]));localStorage.setItem('musaed.key','KEY-A')""")
        await pg.evaluate("new Promise(r=>{var q=indexedDB.open('musaed',1);q.onupgradeneeded=()=>q.result.createObjectStore('files');q.onsuccess=()=>{var tx=q.result.transaction('files','readwrite');tx.objectStore('files').put('DOC-A','doc/1');tx.oncomplete=()=>{q.result.close();r()}}})")
        await pg.reload();await pg.wait_for_timeout(900)
        st=await pg.evaluate("[document.body.classList.contains('locked'),document.querySelector('#authSub').textContent,!document.querySelector('#authMove').hidden,document.querySelector('#authSeg').hidden]")
        nws=await pg.evaluate("performance.getEntriesByType('resource').filter(e=>e.name.indexOf('BidiGenerateContent')>-1).length")
        await pg.wait_for_timeout(1500);live=await pg.evaluate("document.body.dataset.mode")
        print(" voice on the sign-up page: mode",live)
        if live not in ("idle",None,""): F("HIGH","login","the assistant starts talking behind the sign-up page")
        print(" first open:",st);await pg.screenshot(path="tests/out/au_first.png")
        if not st[0]: F("HIGH","login","app opens without an account")
        # validation
        await pg.fill("#auName","عمر");await pg.fill("#auEmail","omar@test");await pg.fill("#auPass","123");await pg.click("#authGo");print(" bad email:",await pg.text_content("#authErr"))
        await pg.fill("#auEmail","Omar@Test.com");await pg.click("#authGo");print(" short password:",await pg.text_content("#authErr"))
        await pg.fill("#auPass","pass-omar-1");await pg.fill("#auPass2","pass-omar-2");await pg.click("#authGo");print(" mismatch:",await pg.text_content("#authErr"))
        await pg.fill("#auPass2","pass-omar-1");await pg.click("#authGo");await pg.wait_for_timeout(2500)
        st=await pg.evaluate("[document.body.classList.contains('locked'),localStorage.getItem('musaed.mem'),localStorage.getItem('musaed.key'),localStorage.getItem('musaed.name')]");print(" omar signed up, old data kept:",st[0]==False,"| memory",bool(st[1]),"| key",st[2],"| name",st[3])
        if st[0] or not st[1]: F("HIGH","login","sign up or move of existing data failed")
        users=json.loads(await pg.evaluate("localStorage.getItem('musaed.users')"));print(" stored account:",{k:(v if k in('email','name') else '…') for k,v in users[0].items()},"| password stored as text:", "pass-omar-1" in json.dumps(users))
        # settings
        await pg.evaluate("document.querySelector('#tabSet').click()");await pg.wait_for_timeout(200);await pg.evaluate("__t.openCard('set')");await pg.wait_for_timeout(800)
        print(" settings account:",await pg.text_content("#acName"),await pg.text_content("#acEmail"),"| permissions:",await pg.evaluate("[...document.querySelectorAll('#permG .cell')].map(b=>b.innerText.replace(/\\n/g,': '))"))
        await pg.screenshot(path="tests/out/au_settings.png")
        # sign out -> data locked away
        await pg.evaluate("document.querySelector('#acOut').click()");await pg.wait_for_timeout(2500)
        st=await pg.evaluate("[document.body.classList.contains('locked'),localStorage.getItem('musaed.mem'),Object.keys(localStorage).filter(k=>k.indexOf('musaed@')===0).length]")
        idb=await pg.evaluate("new Promise(r=>{var q=indexedDB.open('musaed',1);q.onsuccess=()=>{var g=q.result.transaction('files').objectStore('files').count();g.onsuccess=()=>{q.result.close();r(g.result)}}})")
        print(" after sign out: locked",st[0],"| omar's memory visible",bool(st[1]),"| kept apart",st[2],"items | documents left in the open",idb)
        if not st[0] or st[1] or idb: F("HIGH","separation","data still visible after sign out")
        # second user sees nothing of omar
        await pg.click("#authTabUp");await pg.fill("#auName","سارة");await pg.fill("#auEmail","sara@test.com");await pg.fill("#auPass","pass-sara-1");await pg.fill("#auPass2","pass-sara-1");await pg.click("#authGo");await pg.wait_for_timeout(2500)
        st=await pg.evaluate("[document.body.classList.contains('locked'),localStorage.getItem('musaed.mem'),localStorage.getItem('musaed.exp'),localStorage.getItem('musaed.key'),localStorage.getItem('musaed.name')]");print(" sara signed in: sees omar's memory",bool(st[1]),"| expenses",bool(st[2]),"| key",st[3],"| name",st[4])
        if st[1] or st[2] or st[3]: F("HIGH","separation","second user sees the first user's data")
        await pg.evaluate("localStorage.setItem('musaed.mem',JSON.stringify([{id:'s1',t:'تحب الشاي',d:Date.now()}]))")
        await pg.evaluate("document.querySelector('#acOut').click()");await pg.wait_for_timeout(2500)
        # wrong password, then omar again
        await pg.fill("#auEmail","omar@test.com");await pg.fill("#auPass","wrong-pass");await pg.click("#authGo");await pg.wait_for_timeout(1500);print(" wrong password:",await pg.text_content("#authErr"))
        await pg.fill("#auPass","pass-omar-1");await pg.click("#authGo");await pg.wait_for_timeout(2800)
        st=await pg.evaluate("[document.body.classList.contains('locked'),localStorage.getItem('musaed.mem'),localStorage.getItem('musaed.key')]")
        idb=await pg.evaluate("new Promise(r=>{var q=indexedDB.open('musaed',1);q.onsuccess=()=>{var g=q.result.transaction('files').objectStore('files').get('doc/1');g.onsuccess=()=>{q.result.close();r(g.result)}}})")
        print(" omar back: memory",(st[1] or "")[:40],"| key",st[2],"| his document",idb)
        if "القهوة" not in (st[1] or "") or idb!="DOC-A" or "الشاي" in (st[1] or ""): F("HIGH","separation","omar's data not restored correctly")
        # lockout after many wrong tries
        await pg.evaluate("document.querySelector('#acOut').click()");await pg.wait_for_timeout(2500)
        for i in range(6):
            await pg.fill("#auEmail","sara@test.com");await pg.fill("#auPass","nope-"+str(i));await pg.click("#authGo");await pg.wait_for_timeout(1300)
        print(" after 6 wrong tries:",await pg.text_content("#authErr"))
        # forgot password -> delete account
        await pg.fill("#auEmail","sara@test.com");await pg.click("#authForgot");await pg.wait_for_timeout(300);await pg.fill("#aa0","sara@test.com");await pg.click("#authAskF button[type=submit]");await pg.wait_for_timeout(800)
        print(" forgot -> deleted:",await pg.text_content("#authErr"),"| accounts left:",[u["email"] for u in json.loads(await pg.evaluate("localStorage.getItem('musaed.users')"))],"| sara's data left:",await pg.evaluate("Object.keys(localStorage).filter(k=>k.indexOf('musaed@')===0&&localStorage.getItem(k).indexOf('الشاي')>-1).length"))
        await pg.screenshot(path="tests/out/au_login.png")
        print(" errors",errs);await b.close()
    srv.terminate()
    print("FINDINGS",len(FIND))
    for f in FIND: print(" ",f)
asyncio.run(go())
