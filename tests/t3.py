import asyncio, json, re
from playwright.async_api import async_playwright
from PIL import Image
INIT="""localStorage.setItem('musaed.key','AIzaTEST');localStorage.setItem('musaed.name','عمر');localStorage.setItem('musaed.gid','123-abc.apps.googleusercontent.com');
localStorage.setItem('musaed.gtok',JSON.stringify({v:'TOK',exp:Date.now()+3500000}));
localStorage.setItem('musaed.loc',JSON.stringify({lat:24.71,lon:46.68,t:Date.now(),city:'الرياض',region:'',country:'السعودية'}));window.__sent=[];
window.WebSocket=function(u){var w=this;window.__ws=w;w.readyState=1;w.send=function(x){__sent.push(x);var m=JSON.parse(x);if(m.setup)setTimeout(function(){w.onmessage({data:JSON.stringify({setupComplete:{}})})},50)};w.close=function(){};setTimeout(function(){w.onopen&&w.onopen()},20)};"""
LOG=[]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox","--use-fake-device-for-media-stream","--use-fake-ui-for-media-stream","--autoplay-policy=no-user-gesture-required"])
        c=await b.new_context(viewport={"width":390,"height":844},permissions=["microphone","geolocation"],geolocation={"latitude":24.71,"longitude":46.68}); pg=await c.new_page(); errs=[]
        pg.on("pageerror",lambda e:errs.append(str(e))); await pg.add_init_script(INIT)
        async def g(route):
            r=route.request; u=r.url; LOG.append(r.method+" "+re.sub(r"\?.*","",u)[-60:])
            if "calendar" in u:
                if r.method=="DELETE": return await route.fulfill(status=204,body="")
                ev={"id":"ev1","summary":(json.loads(r.post_data)["summary"] if r.post_data and "summary" in r.post_data else "مراجعة العقود مع خالد"),"start":{"dateTime":"2030-01-01T10:30:00+03:00"},"end":{"dateTime":"2030-01-01T11:30:00+03:00"},"location":"المكتب"}
                return await route.fulfill(json=({"items":[ev]} if r.method=="GET" and u.split("?")[0].endswith("/events") else ev))
            if "gmail" in u:
                if "drafts" in u: return await route.fulfill(json={"id":"d1"})
                if "/messages/" in u: return await route.fulfill(json={"id":"m1","threadId":"t1","snippet":"هل نعتمد العرض الثاني؟","payload":{"headers":[{"name":"From","value":"Sara Ahmed <sara@example.com>"},{"name":"Subject","value":"العرض الثاني"},{"name":"Date","value":"Sat, 14 Nov 2026 08:12:00 +0300"},{"name":"Message-ID","value":"<x@y>"}]}})
                return await route.fulfill(json={"messages":[{"id":"m1"},{"id":"m2"}]})
            if "tasks" in u: return await route.fulfill(json=({"items":[{"id":"k1","title":"تجديد الاستمارة"}]} if r.method=="GET" else {"id":"k2","title":"اتصل بالبنك","due":"2026-11-16T00:00:00.000Z"}))
            if "people" in u: return await route.fulfill(json={"results":[{"person":{"names":[{"displayName":"محمد العتيبي"}],"phoneNumbers":[{"value":"055 214 7730","canonicalForm":"+966500000001"}]}}]})
            await route.fulfill(json={})
        await pg.route("**/*googleapis.com/**",g)
        async def wxr(route): await route.fulfill(json={"current":{"temperature_2m":27.3,"weather_code":1},"daily":{"temperature_2m_max":[31.2],"temperature_2m_min":[17.8]}})
        async def prr(route): await route.fulfill(json={"code":200,"data":{"timings":{"Fajr":"04:48","Dhuhr":"11:38","Asr":"14:45","Maghrib":"17:07","Isha":"18:37"}}})
        await pg.route("**/api.open-meteo.com/**",wxr); await pg.route("**/api.aladhan.com/**",prr)
        await pg.goto("file://"+__import__("os").getcwd()+"/index.html"); await pg.wait_for_timeout(1200)
        names=await pg.evaluate("JSON.parse(__sent[0]).setup.tools.map(t=>(t.functionDeclarations||[]).length)")
        print("tools",names)
        async def call(name,args,wait=500):
            await pg.evaluate("(a)=>__ws.onmessage({data:JSON.stringify({toolCall:{functionCalls:[{id:'x',name:a[0],args:a[1]}]}})})",[name,args]); await pg.wait_for_timeout(wait)
            r=await pg.evaluate("__sent.filter(x=>x.indexOf('toolResponse')>-1).slice(-1)[0]"); print(name,"→",json.loads(r)["toolResponse"]["functionResponses"][0]["response"])
        await call("calendar_list",{"days":2}); await call("calendar_add",{"title":"غداء مع فيصل","start":"2026-11-15T13:00","minutes":90})
        await call("reminder_add",{"text":"اتصل على محمد","at":"2026-11-15T17:20"}); await call("calendar_update",{"event_id":"ev1","start":"2026-11-15T14:00"}); await call("calendar_delete",{"event_id":"ev1"},900)
        await pg.screenshot(path="tests/out/c1.png"); await pg.click("#actGo"); await pg.wait_for_timeout(400)
        await call("email_list",{"max":2}); await call("email_draft",{"reply_to_id":"m1","body":"نعم، نعتمد العرض الثاني. شكرًا سارة."},2500); await pg.screenshot(path="tests/out/c2.png"); await pg.click("#actClose")
        await call("tasks_list",{}); await call("task_add",{"title":"اتصل بالبنك","due":"2026-11-16"}); await call("contacts_find",{"name":"محمد"})
        await call("note_add",{"text":"رقم لوحة السيارة ٧٧٣٠"}); await call("expense_add",{"amount":200,"category":"بنزين"}); await call("expenses_summary",{})
        await call("device_action",{"name":"أنوار الصالة"})
        await pg.evaluate("localStorage.setItem('musaed.dev',JSON.stringify([{n:'أنوار الصالة',t:'sc',v:'Living Lights',c:true},{n:'مكيف المجلس',t:'hook',v:'https://example.com/hook',c:false}]))")
        await call("device_action",{"name":"انوار الصاله"}); await call("device_action",{"name":"أنوار الصالة"},900); await pg.screenshot(path="tests/out/c3.png")
        print("go href",await pg.get_attribute("#actGo","href")); await pg.click("#actClose")
        await call("show_action",{"type":"whatsapp","name":"خالد","number":"+966500000002","text":"بوصل متأخر ربع ساعة","go":"https://evil"},400); print("wa href",await pg.get_attribute("#actGo","href")); await pg.click("#actClose")
        await call("show_brief",{},1800); await pg.screenshot(path="tests/out/c4.png"); await pg.click("#briefClose")
        await pg.click("#setBtn"); await pg.wait_for_timeout(700); await pg.evaluate("document.querySelector('#paneSet').scrollTop=430"); await pg.wait_for_timeout(200); await pg.screenshot(path="tests/out/c5.png")
        print("errors",errs); print("calls",LOG[:40]); await b.close()
    im=Image.new("RGB",(390*5+80,844),(50,50,50))
    for i in range(5): im.paste(Image.open(f"tests/out/c{i+1}.png"),(i*410,0))
    im.save("tests/out/c_row.png")
asyncio.run(main())
