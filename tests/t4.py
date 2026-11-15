import asyncio, json, re
from playwright.async_api import async_playwright
src=open("tests/t3.py").read()
INIT=re.search(r'INIT="""(.*?)"""',src,re.S).group(1)
INIT=re.sub(r"localStorage.setItem\('musaed.gtok'.*?\);\n","",INIT,flags=re.S).replace("localStorage.setItem('musaed.gid','123-abc.apps.googleusercontent.com');","")
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox","--use-fake-device-for-media-stream","--use-fake-ui-for-media-stream","--autoplay-policy=no-user-gesture-required"])
        c=await b.new_context(viewport={"width":390,"height":844},permissions=["microphone","geolocation"],geolocation={"latitude":24.71,"longitude":46.68}); pg=await c.new_page(); errs=[]
        pg.on("pageerror",lambda e:errs.append(str(e))); await pg.add_init_script(INIT)
        await pg.goto("file://"+__import__("os").getcwd()+"/index.html"); await pg.wait_for_timeout(1200)
        async def call(name,args,wait=500):
            await pg.evaluate("(a)=>__ws.onmessage({data:JSON.stringify({toolCall:{functionCalls:[{id:'x',name:a[0],args:a[1]}]}})})",[name,args]); await pg.wait_for_timeout(wait)
            r=await pg.evaluate("__sent.filter(x=>x.indexOf('toolResponse')>-1).slice(-1)[0]"); print(name,"→",json.loads(r)["toolResponse"]["functionResponses"][0]["response"])
            print("   card:",(await pg.evaluate("[document.querySelector('#actTitle')?.textContent,document.querySelector('#actBody')?.textContent,document.body.className||document.body.dataset.mode]")))
        await call("contacts_find",{"name":"محمد"})
        await call("show_action",{"type":"call","name":"محمد","number":"0552147730","reason":"تأجيل الاجتماع إلى بكرة 11 الصبح"},900)
        await pg.screenshot(path="tests/out/call.png")
        await call("contacts_find",{"name":"محمّد"})
        await call("show_action",{"type":"call","name":"محمد","reason":"متابعة"},900)
        print("saved",await pg.evaluate("localStorage.getItem('musaed.ct')")); print("errors",errs); await b.close()
asyncio.run(main())
