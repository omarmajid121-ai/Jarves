import asyncio, json, re
from playwright.async_api import async_playwright
src=open("tests/t3.py").read()
INIT=re.search(r'INIT="""(.*?)"""',src,re.S).group(1)+"\nlocalStorage.setItem('musaed.cs','https://calls.test');localStorage.setItem('musaed.ck','correct-horse-battery');"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox","--use-fake-device-for-media-stream","--use-fake-ui-for-media-stream","--autoplay-policy=no-user-gesture-required"])
        c=await b.new_context(viewport={"width":390,"height":844},permissions=["microphone"]); pg=await c.new_page(); errs=[]
        pg.on("pageerror",lambda e:errs.append(str(e))); await pg.add_init_script(INIT)
        seq=[{"status":"starting","transcript":[]},{"status":"ringing","transcript":[]},{"status":"talking","transcript":[{"who":"her","text":"السلام عليكم، معك مساعد عمر الذكية"}]},
             {"status":"done","seconds":42,"result":{"outcome":"done","summary":"حجز لأربعة الساعة 9 باسم عمر"},"transcript":[{"who":"her","text":"السلام عليكم"},{"who":"them","text":"تم الحجز"}]}]
        posted=[]
        async def srv(route):
            r=route.request
            if r.method=="OPTIONS": return await route.fulfill(status=204,headers={"access-control-allow-origin":"*","access-control-allow-headers":"authorization, content-type"})
            h={"access-control-allow-origin":"*"}
            if r.url.endswith("/call") and r.method=="POST": posted.append([r.headers.get("authorization"),r.post_data]); return await route.fulfill(json={"id":"abc","status":"starting"},headers=h)
            if "/call/abc" in r.url: return await route.fulfill(json=seq.pop(0) if len(seq)>1 else seq[0],headers=h)
            await route.fulfill(json={"ok":True,"ready":True,"from":"+17372508034"},headers=h)
        await pg.route("https://calls.test/**",srv)
        await pg.route("**/*googleapis.com/**",lambda r:r.fulfill(json={}))
        await pg.goto("file://"+__import__("os").getcwd()+"/index.html"); await pg.wait_for_timeout(1200)
        setup=await pg.evaluate("JSON.parse(__sent[0]).setup"); names=[f["name"] for t in setup["tools"] for f in t.get("functionDeclarations",[])]
        print("decls",len(names),"assistant_call" in names,"prompt has assistant_call:", "assistant_call" in setup["systemInstruction"]["parts"][0]["text"])
        card=lambda: pg.evaluate("[document.querySelector('#actTitle').textContent,document.querySelector('#actTag').textContent,document.querySelector('#actBody').textContent,document.querySelector('#actGo').hidden?'':document.querySelector('#actGo').textContent]")
        await pg.evaluate("(a)=>__ws.onmessage({data:JSON.stringify({toolCall:{functionCalls:[{id:'x',name:a[0],args:a[1]}]}})})",["assistant_call",{"name":"مطعم نجد","number":"0534619119","brief":"احجزي طاولة لأربعة الساعة تسع الليلة باسم عمر"}]); await pg.wait_for_timeout(900)
        print("resp",json.loads(await pg.evaluate("__sent.filter(x=>x.indexOf('toolResponse')>-1).slice(-1)[0]"))["toolResponse"]["functionResponses"][0]["response"])
        print("confirm",await card()); await pg.screenshot(path="tests/out/ac1.png")
        await pg.click("#actGo"); await pg.wait_for_timeout(1500); print("progress",await card())
        await pg.wait_for_timeout(5600); print("talking",await card()); await pg.screenshot(path="tests/out/ac2.png")
        await pg.wait_for_timeout(3500); print("result",await card()); await pg.screenshot(path="tests/out/ac3.png")
        print("posted",posted[0][0][:12],json.loads(posted[0][1])["to"])
        print("to model",[json.loads(x)["realtimeInput"]["text"][:90] for x in await pg.evaluate("__sent.filter(x=>x.indexOf('نتيجة المكالمة')>-1)")])
        print("note",(await pg.evaluate("JSON.parse(localStorage.getItem('musaed.notes')).slice(-1)[0].x")))
        print("errors",errs); await b.close()
asyncio.run(main())
