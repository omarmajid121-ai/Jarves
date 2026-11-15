import asyncio, json, re
from playwright.async_api import async_playwright
src=open("tests/t3.py").read()
INIT=re.search(r'INIT="""(.*?)"""',src,re.S).group(1)+"\nlocalStorage.setItem('musaed.cs','https://calls.test');localStorage.setItem('musaed.ck','correct-horse-battery');"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox","--use-fake-device-for-media-stream","--use-fake-ui-for-media-stream","--autoplay-policy=no-user-gesture-required"])
        c=await b.new_context(viewport={"width":390,"height":844},permissions=["microphone"]); pg=await c.new_page(); errs=[]; posted=[]
        pg.on("pageerror",lambda e:errs.append(str(e))); await pg.add_init_script(INIT)
        async def srv(route):
            r=route.request;h={"access-control-allow-origin":"*","access-control-allow-headers":"authorization, content-type"}
            if r.method=="OPTIONS": return await route.fulfill(status=204,headers=h)
            if r.url.endswith("/call"): posted.append(json.loads(r.post_data)); return await route.fulfill(json={"id":"abc"},headers=h)
            await route.fulfill(json={"status":"ringing","transcript":[]},headers=h)
        await pg.route("https://calls.test/**",srv); await pg.route("**/*googleapis.com/**",lambda r:r.fulfill(json={}))
        await pg.goto("file://"+__import__("os").getcwd()+"/index.html"); await pg.wait_for_timeout(1200)
        await pg.evaluate("(a)=>__ws.onmessage({data:JSON.stringify({toolCall:{functionCalls:[{id:'x',name:a[0],args:a[1]}]}})})",["show_action",{"type":"call","name":"عمر","number":"0534619119","reason":"اجتماع بكرة تأجل للساعة 11، واسأله إذا يناسبه"}]); await pg.wait_for_timeout(900)
        print(await pg.evaluate("[document.querySelector('#actAlt').hidden,document.querySelector('#actAlt').textContent,document.querySelector('#actGo').textContent,document.querySelector('#actGo').getAttribute('href')]"))
        await pg.screenshot(path="tests/out/alt.png")
        await pg.click("#actAlt"); await pg.wait_for_timeout(1200); print("posted",posted); print(await pg.evaluate("document.querySelector('#actTitle').textContent+' | '+document.querySelector('#actAlt').hidden"))
        print("errors",errs); await b.close()
asyncio.run(main())
