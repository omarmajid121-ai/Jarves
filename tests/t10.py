import asyncio, json, re, datetime
from playwright.async_api import async_playwright
src=open("tests/t3.py").read()
INIT=re.search(r'INIT="""(.*?)"""',src,re.S).group(1)
INIT=re.sub(r"localStorage.setItem\('musaed.gtok'.*?\);\n","",INIT,flags=re.S).replace("localStorage.setItem('musaed.gid','123-abc.apps.googleusercontent.com');","")
now=datetime.datetime.now();soon=now+datetime.timedelta(hours=3,minutes=10)
BP={"kind":"boarding","title":"رحلة جدة","name":"ALBDOUR/OMAR","code":"K7XQ2M","date":"2026-11-15","time":"07:05","airline":"السعودية","flight":"SV1023","from_code":"ruh","from_city":"الرياض","to_code":"jed","to_city":"جدة","arrive_time":"08:50","boarding_time":"06:20","gate":"B12","seat":"14A","terminal":"5"}
HT={"kind":"hotel","title":"فندق الواحة","name":"Omar Albdour","code":"HX-448120","date":"2026-11-15","time":"15:00","end_date":"2026-11-18","place":"فندق الواحة دبي"}
TODAY=dict(BP,date=soon.strftime("%Y-%m-%d"),time=soon.strftime("%H:%M"),arrive_time="",flight="XY88",to_city="أبها",to_code="AHB",title="رحلة أبها")
Q=[];LOG=[]
async def gem(route):
    rq=route.request;u=rq.url
    if rq.method=="GET": LOG.append("list"); return await route.fulfill(json={"models":[{"name":"models/gemini-3.8-flash","supportedGenerationMethods":["generateContent"]},{"name":"models/gemini-3.8-flash-lite","supportedGenerationMethods":["generateContent"]},{"name":"models/gemini-3.8-live","supportedGenerationMethods":["bidiGenerateContent"]}]})
    body=json.loads(rq.post_data or "{}");parts=body["contents"][0]["parts"];m=re.search(r"models/([^:]+):",u).group(1)
    if len(parts)<2 or "inlineData" not in parts[1]: return await route.fulfill(json={"candidates":[{"content":{"parts":[{"text":"ملخص"}]}}]})
    LOG.append((m,[p.get("inlineData",{}).get("mimeType","text") for p in parts],len(parts[1]["inlineData"]["data"])//1000,"key" if rq.headers.get("x-goog-api-key") else "NOKEY","key-in-url" if "key=" in u else "url-clean"))
    r=Q.pop(0) if Q else BP
    if isinstance(r,int): return await route.fulfill(status=r,json={"error":{"code":r}})
    await route.fulfill(json={"candidates":[{"content":{"parts":[{"text":"```json\n"+json.dumps(r,ensure_ascii=False)+"\n```"}]}}]})
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox","--use-fake-device-for-media-stream","--use-fake-ui-for-media-stream","--autoplay-policy=no-user-gesture-required","--allow-file-access-from-files"])
        c=await b.new_context(viewport={"width":390,"height":844},permissions=["microphone"]); pg=await c.new_page(); errs=[]
        pg.on("pageerror",lambda e:errs.append(str(e))); await pg.add_init_script(INIT)
        await pg.route("**/*googleapis.com/**",lambda r:r.fulfill(json={}))
        await pg.route(re.compile(r"generativelanguage\.googleapis\.com/v1beta/models"),gem)
        
        await pg.goto("file://"+__import__("os").getcwd()+"/index.html"); await pg.wait_for_timeout(1200)
        setup=await pg.evaluate("JSON.parse(__sent[0]).setup"); print("decls",sum(len(t.get("functionDeclarations",[])) for t in setup["tools"]))
        async def call(name,args,wait=800,shot=None):
            await pg.evaluate("(a)=>__ws.onmessage({data:JSON.stringify({toolCall:{functionCalls:[{id:'x',name:a[0],args:a[1]}]}})})",[name,args]); await pg.wait_for_timeout(wait)
            r=json.loads(await pg.evaluate("__sent.filter(x=>x.indexOf('toolResponse')>-1).slice(-1)[0]"))["toolResponse"]["functionResponses"][0]["response"]
            print(name,"→",json.dumps({k:(v if not isinstance(v,(str,list,dict)) else (v[:50] if isinstance(v,str) else "…")) for k,v in r.items()},ensure_ascii=False))
            if shot: await pg.screenshot(path=f"tests/out/e_{shot}.png")
            return r
        card=lambda: pg.evaluate("[document.querySelector('#act').classList.contains('on'),document.querySelector('#actTitle').textContent,document.querySelector('#actTag').textContent,document.querySelector('#actGo').textContent,document.querySelector('#actSecond').textContent]")
        docs=lambda: pg.evaluate("JSON.parse(localStorage.getItem('musaed.docs')||'[]').map(d=>[d.kind,d.title,d.pend,d.n,d.pdf,!!d.ev,d.shown,d.unread||''])")
        async def close():
            await pg.evaluate("for(var i=0;i<6;i++)document.querySelector('#actClose').click()"); await pg.wait_for_timeout(200)
        await call("doc_add",{},700,"add")
        # 1 photo: first model 404 -> list -> fallback
        Q[:]=[404,BP]
        await pg.evaluate("document.querySelector('#docImg').value=''"); await pg.set_input_files("#docImg","tests/docs/bp.png"); await pg.wait_for_timeout(2500); await pg.screenshot(path="tests/out/e_pend.png")
        print(" pend:",await card(),await docs()); print(" calls:",LOG)
        print(" told:",[json.loads(x)["realtimeInput"]["text"][:70] for x in await pg.evaluate("__sent.filter(x=>x.indexOf('رفعت وثيقة')>-1)")])
        r=await call("doc_confirm",{"save":True},900,"saved"); print(" saved:",await card(),await docs())
        print(" cal:",[(e["title"],e["kind"],e.get("pre"),e["mins"],e["loc"]) for e in json.loads(await pg.evaluate("localStorage.getItem('musaed.cal')||'[]'"))])
        await call("doc_show",{"kind":"boarding","full":True},900,"view"); print(" viewer:",await pg.evaluate("[document.querySelector('#docView').className,document.querySelector('#dvImg').naturalWidth,document.querySelector('#dvTitle').textContent,document.querySelector('#act').classList.contains('on')]"))
        await pg.click("#dvImg"); await pg.wait_for_timeout(300); await pg.screenshot(path="tests/out/e_zoom.png")
        await pg.click("#dvClose"); await pg.wait_for_timeout(500); print(" after close:",await card()); await close()
        # 2 pdf hotel, saved by tap
        LOG.clear(); Q[:]=[HT]
        await pg.set_input_files("#docPdf","tests/docs/hotel.pdf"); await pg.wait_for_timeout(5000); await pg.screenshot(path="tests/out/e_hotel.png")
        print(" pdf pend:",await card(),await docs()); print(" calls:",LOG)
        await pg.click("#actGo"); await pg.wait_for_timeout(700); print(" pdf saved:",await card(),await docs())
        await pg.click("#actGo"); await pg.wait_for_timeout(700); print(" pdf viewer:",await pg.evaluate("[document.querySelector('#docView').className,document.querySelector('#dvPg').textContent,document.querySelector('#dvNext').hidden]"))
        await pg.click("#dvNext"); await pg.wait_for_timeout(400); await pg.screenshot(path="tests/out/e_pdfview.png"); print(" page:",await pg.evaluate("document.querySelector('#dvPg').textContent"))
        await pg.keyboard.press("Escape"); await pg.wait_for_timeout(400); await close()
        await call("doc_show",{},800,"list"); await close()
        await call("doc_show",{"query":"الواحة"}); print(" by query:",await card()); await close()
        # 3 refused
        Q[:]=[{"kind":"refused"}]; await pg.set_input_files("#docCam","tests/docs/bp.png"); await pg.wait_for_timeout(2000); await pg.screenshot(path="tests/out/e_refused.png"); print(" refused:",await card(),len(await docs())); await close()
        # 4 read failure, then corrected by voice
        Q[:]=[500]; await pg.evaluate("document.querySelector('#docImg').value=''"); await pg.set_input_files("#docImg","tests/docs/bp.png"); await pg.wait_for_timeout(2000); await pg.screenshot(path="tests/out/e_unread.png"); print(" unread:",await card(),(await docs())[-1])
        await call("doc_update",{"kind":"event","title":"مباراة الهلال","place":"المملكة أرينا","date":"2026-11-20","time":"20:00","seat":"C-114"},800,"event"); print(" updated:",await card(),(await docs())[-1])
        await call("doc_confirm",{"save":False}); print(" discarded:",len(await docs())); await close()
        # 5 flight today: shows by itself
        Q[:]=[TODAY]; await pg.evaluate("document.querySelector('#docImg').value=''"); await pg.set_input_files("#docImg","tests/docs/bp.png"); await pg.wait_for_timeout(2000); await call("doc_confirm",{"save":True}); await close()
        await pg.wait_for_timeout(21000); await pg.screenshot(path="tests/out/e_auto.png"); print(" auto:",await card(),(await docs())[-1])
        print(" spoken:",[json.loads(x)["realtimeInput"]["text"][:80] for x in await pg.evaluate("__sent.filter(x=>x.indexOf('(تنبيه)')>-1)")]); await close()
        # 6 data page + delete
        await pg.click("#pfBtn"); await pg.wait_for_timeout(600); print(" data rows:",await pg.evaluate("[].map.call(document.querySelectorAll('#dcList li'),l=>l.textContent)")); await pg.screenshot(path="tests/out/e_data.png"); await pg.evaluate("document.querySelector('#card').classList.remove('open')"); await pg.wait_for_timeout(500)
        did=await pg.evaluate("JSON.parse(localStorage.getItem('musaed.docs'))[0].id")
        await call("doc_delete",{"id":did},700,"del"); await pg.click("#actGo"); await pg.wait_for_timeout(500)
        print(" after delete:",await docs()); print(" cal:",[(e["title"],e["kind"]) for e in json.loads(await pg.evaluate("localStorage.getItem('musaed.cal')||'[]'"))])
        print(" idb keys:",await pg.evaluate("new Promise(r=>{var q=indexedDB.open('musaed',1);q.onsuccess=()=>{var k=q.result.transaction('files').objectStore('files').getAllKeys();k.onsuccess=()=>r(k.result.length)}})"))
        # reload: persists
        await pg.reload(); await pg.wait_for_timeout(1500); await call("doc_show",{"kind":"hotel"},900); print(" after reload:",await card(),await pg.evaluate("!!document.querySelector('#act .cb-media img')"))
        print("errors",errs); await b.close()
asyncio.run(main())
