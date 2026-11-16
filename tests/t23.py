import asyncio, json, subprocess, time
from playwright.async_api import async_playwright
FIND=[]
def F(sev,area,msg): FIND.append((sev,area,msg)); print("  !!",sev,area,"-",msg)
srv=subprocess.Popen(["python3","-m","http.server","8768","--bind","127.0.0.1"],cwd=__import__("os").getcwd(),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
URL="http://127.0.0.1:8768/index.html"
async def signup(pg,name,email,pw):
    if await pg.evaluate("document.querySelector('#authSeg').hidden===false"): await pg.click("#authTabUp")
    await pg.fill("#auName",name);await pg.fill("#auEmail",email);await pg.fill("#auPass",pw);await pg.fill("#auPass2",pw);await pg.click("#authGo")
    for _ in range(40):
        await pg.wait_for_timeout(200)
        code=await pg.evaluate("(()=>{var d=[...document.querySelectorAll('[role=dialog] div')].find(x=>/^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$/.test(x.textContent));return d?d.textContent:''})()")
        if code: break
    shown=bool(code)
    if code:
        await pg.evaluate("document.querySelector('[role=dialog] input[type=checkbox]').click()");await pg.evaluate("[...document.querySelectorAll('[role=dialog] button')].find(b=>b.textContent==='تم').click()")
    await pg.wait_for_timeout(1800);return code
async def signout(pg):
    await pg.evaluate("document.querySelector('#acOut').click()");await pg.wait_for_timeout(2600)
async def go():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox","--use-fake-device-for-media-stream","--use-fake-ui-for-media-stream"])
        c=await b.new_context(viewport={"width":390,"height":844});pg=await c.new_page();errs=[];pg.on("pageerror",lambda e:errs.append(str(e)[:160]))
        for u in ["**/*googleapis.com/**","**/api.open-meteo.com/**","**/api.aladhan.com/**"]: await c.route(u,lambda r:r.fulfill(json={}))
        await pg.goto(URL);await pg.evaluate("localStorage.clear()");await pg.reload();await pg.wait_for_timeout(800)
        code=await signup(pg,"عمر","omar@test.com","pass-omar-1");st=await pg.evaluate("[document.body.classList.contains('locked'),!!JSON.parse(localStorage.getItem('musaed.users'))[0].rc]")
        print(" sign-up shows recovery code once:",code,"| signed in:",not st[0],"| code stored (as hash):",st[1],"| code stored as text:",code in await pg.evaluate("localStorage.getItem('musaed.users')"))
        if not code or st[0]: F("HIGH","recovery","no recovery code at sign-up")
        await pg.evaluate("localStorage.setItem('musaed.mem',JSON.stringify([{id:'m1',t:'يحب القهوة',d:Date.now()}]))")
        # late write after sign-out must not reach the next account
        await signout(pg)
        await pg.evaluate("localStorage.setItem('musaed.log',JSON.stringify([{r:'a',t:'سر عمر'}]))")
        await pg.evaluate("new Promise(r=>{var q=indexedDB.open('musaed',1);q.onsuccess=()=>{var tx=q.result.transaction('files','readwrite');tx.objectStore('files').put(['سر عمر'],'hist/x');tx.oncomplete=()=>{q.result.close();r()}}})")
        await signup(pg,"سارة","sara@test.com","pass-sara-1")
        leak=await pg.evaluate("localStorage.getItem('musaed.log')");idb=await pg.evaluate("new Promise(r=>{var q=indexedDB.open('musaed',1);q.onsuccess=()=>{var g=q.result.transaction('files').objectStore('files').count();g.onsuccess=()=>{q.result.close();r(g.result)}}})")
        print(" leftovers reach the next account: log",leak,"| history items",idb)
        if (leak and "سر" in leak) or idb: F("HIGH","separation","leftovers reached the next account")
        await signout(pg)
        # forgot password with the recovery code
        await pg.fill("#auEmail","omar@test.com");await pg.click("#authForgot");await pg.wait_for_timeout(300)
        await pg.fill("#aa0","WRONG-CODE-XX");await pg.fill("#aa1","new-pass-omar");await pg.fill("#aa2","new-pass-omar");await pg.click("#authAskF button[type=submit]");await pg.wait_for_timeout(1500)
        print(" wrong recovery code:",await pg.evaluate("document.querySelector('#authAskF [role=alert]').textContent"))
        await pg.fill("#aa0",code.lower().replace("-"," "));await pg.click("#authAskF button[type=submit]")
        code2=""
        for _ in range(30):
            await pg.wait_for_timeout(200)
            code2=await pg.evaluate("(()=>{var d=[...document.querySelectorAll('[role=dialog] div')].find(x=>/^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$/.test(x.textContent));return d?d.textContent:''})()")
            if code2: break
        print(" right code -> new password, new recovery code:",code2 and code2!=code)
        if code2:
            await pg.evaluate("document.querySelector('[role=dialog] input[type=checkbox]').click()");await pg.evaluate("[...document.querySelectorAll('[role=dialog] button')].find(b=>b.textContent==='تم').click()");await pg.wait_for_timeout(300)
        print("   message:",await pg.text_content("#authErr"))
        await pg.fill("#auEmail","omar@test.com");await pg.fill("#auPass","new-pass-omar");await pg.click("#authGo");await pg.wait_for_timeout(2600)
        mem=await pg.evaluate("localStorage.getItem('musaed.mem')");print(" signed in with the new password, data kept:",bool(mem and "القهوة" in mem))
        if not (mem and "القهوة" in mem): F("HIGH","recovery","reset lost the data or failed")
        # second tab locks when this one signs out
        pg2=await c.new_page();await pg2.goto(URL);await pg2.wait_for_timeout(1200)
        print(" second tab signed in:",not await pg2.evaluate("document.body.classList.contains('locked')"))
        await signout(pg);await pg2.wait_for_timeout(2500)
        lk=await pg2.evaluate("document.body.classList.contains('locked')");raw=await pg2.evaluate("localStorage.getItem('musaed.mem')");print(" after sign-out in tab 1, tab 2 locked:",lk,"| data left in the open:",bool(raw))
        if not lk or raw: F("HIGH","tabs","the other tab stays open after sign-out")
        await pg2.close()
        # lock on open
        await pg.fill("#auEmail","omar@test.com");await pg.fill("#auPass","new-pass-omar");await pg.click("#authGo");await pg.wait_for_timeout(2600)
        await pg.evaluate("__t.openCard('set')");await pg.wait_for_timeout(400);await pg.evaluate("document.querySelector('#acLock').click()");await pg.wait_for_timeout(300)
        await pg.fill("#aa0","new-pass-omar");await pg.fill("#aa1","12a4");await pg.fill("#aa2","12a4");await pg.click("#authAskF button[type=submit]");await pg.wait_for_timeout(500)
        print(" bad PIN:",await pg.evaluate("document.querySelector('#authAskF [role=alert]').textContent"))
        await pg.fill("#aa1","2468");await pg.fill("#aa2","2468");await pg.click("#authAskF button[type=submit]");await pg.wait_for_timeout(1500)
        print(" lock setting:",await pg.text_content("#acLock"))
        await pg.reload();await pg.wait_for_timeout(1500)
        print(" app opens locked:",await pg.evaluate("!!document.querySelector('#pinLock')&&document.body.classList.contains('locked')"))
        await pg.fill("#pinIn","1111");await pg.click("#pinF button[type=submit]");await pg.wait_for_timeout(1200);print(" wrong PIN:",await pg.text_content("#pinErr"))
        await pg.fill("#pinIn","2468");await pg.click("#pinF button[type=submit]");await pg.wait_for_timeout(1200);ok=await pg.evaluate("!document.querySelector('#pinLock')&&!document.body.classList.contains('locked')");print(" right PIN opens:",ok)
        if not ok: F("HIGH","lock","PIN did not open the app")
        await pg.reload();await pg.wait_for_timeout(1500);await pg.click("#pinPw");await pg.fill("#pinIn","new-pass-omar");await pg.click("#pinF button[type=submit]");await pg.wait_for_timeout(1500)
        print(" password opens too:",await pg.evaluate("!document.querySelector('#pinLock')"))
        await pg.screenshot(path="tests/out/au2.png")
        # account made before recovery codes existed
        await pg.evaluate("(()=>{var l=JSON.parse(localStorage.getItem('musaed.users'));l.push({id:'old1',email:'old@test.com',name:'قديم',salt:'AAAA',hash:'x',it:1});localStorage.setItem('musaed.users',JSON.stringify(l))})()")
        await signout(pg);await pg.fill("#auEmail","old@test.com");await pg.click("#authForgot");await pg.wait_for_timeout(300);print(" old account without a code:",await pg.text_content("#authErr"))
        print(" errors",errs);await b.close()
    srv.terminate()
    print("FINDINGS",len(FIND))
    for f in FIND: print(" ",f)
asyncio.run(go())
