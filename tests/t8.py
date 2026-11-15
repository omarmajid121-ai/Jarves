import asyncio, json, re, base64
from playwright.async_api import async_playwright
src=open("tests/t3.py").read()
INIT=re.search(r'INIT="""(.*?)"""',src,re.S).group(1)+"\nlocalStorage.setItem('musaed.cs','https://calls.test');localStorage.setItem('musaed.ck','correct-horse-battery');"
PNG=base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
SVGIMG='<svg xmlns="http://www.w3.org/2000/svg" width="900" height="600"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3B2A6B"/><stop offset="1" stop-color="#FFB36B"/></linearGradient></defs><rect width="900" height="600" fill="url(#g)"/><circle cx="640" cy="300" r="80" fill="#FFE2A8"/><path d="M0 420 C200 320 500 480 900 380 V600 H0z" fill="#B8612E"/></svg>'
import math
coords=[[46.68+i*0.004+math.sin(i/3)*0.003,24.71+i*0.006] for i in range(40)]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox","--use-fake-device-for-media-stream","--use-fake-ui-for-media-stream","--autoplay-policy=no-user-gesture-required"])
        c=await b.new_context(viewport={"width":390,"height":844},permissions=["microphone","geolocation"],geolocation={"latitude":24.71,"longitude":46.68}); pg=await c.new_page(); errs=[]
        pg.on("pageerror",lambda e:errs.append(str(e))); await pg.add_init_script(INIT)
        H={"access-control-allow-origin":"*"}
        await pg.route("**/*googleapis.com/**",lambda r:r.fulfill(json={}))
        await pg.route("**/api.open-meteo.com/**",lambda r:r.fulfill(json={"current":{"temperature_2m":27.3,"weather_code":1},"daily":{"temperature_2m_max":[31.2],"temperature_2m_min":[17.8]}}))
        await pg.route("**/api.aladhan.com/**",lambda r:r.fulfill(json={"code":200,"data":{"timings":{"Fajr":"04:48","Dhuhr":"11:38","Asr":"14:45","Maghrib":"17:07","Isha":"18:37"}}}))
        await pg.route("**/*.wikipedia.org/**",lambda r:r.fulfill(json={"query":{"pages":{"1":{"index":1,"title":"الربع الخالي","fullurl":"https://ar.wikipedia.org/wiki/X","thumbnail":{"source":"https://upload.wikimedia.org/a.svg"}},"2":{"index":2,"title":"كثيب","fullurl":"https://ar.wikipedia.org/wiki/Y","thumbnail":{"source":"https://upload.wikimedia.org/b.svg"}}}}},headers=H))
        await pg.route("**/upload.wikimedia.org/**",lambda r:r.fulfill(body=SVGIMG,content_type="image/svg+xml"))
        await pg.route("**/nominatim.openstreetmap.org/**",lambda r:r.fulfill(json=[{"lat":"24.95","lon":"46.70","display_name":"مطار الملك خالد"}],headers=H))
        await pg.route("**/router.project-osrm.org/**",lambda r:r.fulfill(json={"code":"Ok","routes":[{"distance":18200,"duration":1440,"geometry":{"coordinates":coords},"legs":[{"steps":[{"name":"طريق الملك فهد","distance":12000,"maneuver":{"type":"depart"}},{"name":"طريق المطار","distance":5000,"maneuver":{"type":"turn","modifier":"right"}},{"name":"","distance":1000,"maneuver":{"type":"arrive"}}]}]}]},headers=H))
        await pg.route("**/tile.openstreetmap.org/**",lambda r:r.fulfill(body=PNG,content_type="image/png"))
        await pg.goto("file://"+__import__("os").getcwd()+"/index.html"); await pg.wait_for_timeout(1200)
        setup=await pg.evaluate("JSON.parse(__sent[0]).setup"); print("decls",sum(len(t.get("functionDeclarations",[])) for t in setup["tools"]),"accent line" , "set_accent" in setup["systemInstruction"]["parts"][0]["text"])
        async def call(name,args,wait=900,shot=None):
            await pg.evaluate("(a)=>__ws.onmessage({data:JSON.stringify({toolCall:{functionCalls:[{id:'x',name:a[0],args:a[1]}]}})})",[name,args]); await pg.wait_for_timeout(wait)
            r=json.loads(await pg.evaluate("__sent.filter(x=>x.indexOf('toolResponse')>-1).slice(-1)[0]"))["toolResponse"]["functionResponses"][0]["response"]
            print(name,"→",{k:(v if not isinstance(v,str) else v[:50]) for k,v in r.items()})
            if shot: await pg.screenshot(path=f"tests/out/c_{shot}.png")
        close=lambda: pg.evaluate("closeAllForTest()")
        await pg.evaluate("window.closeAllForTest=function(){document.querySelector('#xBtn')&&0;document.querySelector('#sheetClose').click();for(var i=0;i<6;i++)document.querySelector('#actClose').click()}")
        await call("show_action",{"type":"call","name":"محمد العتيبي","number":"+966500000001","reason":"تأجيل الاجتماع لبكرة 11"},900,"call")
        await call("show_action",{"type":"whatsapp","name":"سارة","number":"0551112222","text":"هلا سارة، نعتمد العرض الثاني. أرسلي لي العقد اليوم."},900,"stack")
        print("stack",await pg.evaluate("[document.querySelector('#actCount').textContent,document.querySelector('#act').className]"))
        await pg.click("#actClose"); await pg.wait_for_timeout(500); print("after close top:",await pg.evaluate("document.querySelector('#actTitle').textContent")); await close()
        await call("today_data",{"show":"weather"},1200,"wx"); await close()
        await call("today_data",{"show":"prayer"},900,"pray"); await close()
        await call("show_card",{"title":"أي وقت يناسبك؟","subtitle":"المطعم يقترح","icon":"clock","choices":["8:30 م","9:30 م","10:00 م","يوم ثاني"]},900,"choice")
        await pg.click(".cb-chips button:nth-child(2)"); await pg.wait_for_timeout(400); print("choice sent:",[json.loads(x)["realtimeInput"]["text"] for x in await pg.evaluate("__sent.filter(x=>x.indexOf('9:30')>-1)")])
        await call("show_card",{"title":"أرامكو","subtitle":"50 سهم في محفظتك","icon":"chart","big":{"value":"28.45","unit":"ر.س","note":"▲ 1.2%\nاليوم"},"rows":[{"label":"القيمة","value":"1,422 ر.س"}]},900,"big"); await close()
        await call("show_news",{"items":[{"title":"افتتاح مسار جديد في مترو الرياض","source":"واس"},{"title":"السوق يغلق مرتفعًا للجلسة الثالثة","source":"الاقتصادية"},{"title":"أمطار متوقعة على المنطقة الشرقية","source":"الأرصاد"},{"title":"خبر رابع","source":"مصدر"},{"title":"خبر خامس","source":"مصدر"}]},900,"news")
        await pg.click("#actSecond"); await pg.wait_for_timeout(700); await pg.screenshot(path="tests/out/c_newssheet.png"); await close()
        await call("show_photo",{"query":"الربع الخالي","query_en":"Rub al Khali","caption":"أكبر صحراء رملية متصلة في العالم."},1500,"photo")
        await pg.click(".cb-media"); await pg.wait_for_timeout(700); await pg.screenshot(path="tests/out/c_photosheet.png"); await close()
        await call("show_route",{"destination":"مطار الملك خالد"},2000,"route")
        await pg.click(".cb-media"); await pg.wait_for_timeout(800); await pg.screenshot(path="tests/out/c_routesheet.png"); await close()
        await call("show_flight",{"from_code":"ruh","from_city":"الرياض","to_code":"JED","to_city":"جدة","depart_time":"7:05 ص","arrive_time":"8:50 ص","date":"الأحد 15 نوفمبر","flight":"SV 1023","duration":"ساعة و45 د","stops":"مباشرة","boarding":"6:20 ص","gate":"24","seat":"14A","status":"في موعدها"},900,"flight"); await close()
        await call("calendar_delete",{"id":"ev1"},900,"delete"); await close()
        await call("set_accent",{"accent":"مصرية","module":"assistant"},500); await call("set_accent",{"accent":"شامية","module":"calls"},500)
        print("stored",await pg.evaluate("[localStorage.getItem('musaed.dia'),localStorage.getItem('musaed.diac')]"))
        await call("set_accent",{"accent":"default","module":"all"},500); print("reset",await pg.evaluate("[localStorage.getItem('musaed.dia'),localStorage.getItem('musaed.diac')]"))
        print("errors",errs); await b.close()
asyncio.run(main())
