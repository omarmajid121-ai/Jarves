import asyncio, json, re, datetime
from playwright.async_api import async_playwright
src=open("tests/t3.py").read()
INIT=re.search(r'INIT="""(.*?)"""',src,re.S).group(1)
INIT=re.sub(r"localStorage.setItem\('musaed.gtok'.*?\);\n","",INIT,flags=re.S).replace("localStorage.setItem('musaed.gid','123-abc.apps.googleusercontent.com');","")
now=datetime.datetime.now();D=now.strftime("%Y-%m-%d");tm=(now+datetime.timedelta(days=1)).strftime("%Y-%m-%d")
h=lambda add: (now+datetime.timedelta(minutes=add)).strftime("%Y-%m-%dT%H:%M")
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox","--use-fake-device-for-media-stream","--use-fake-ui-for-media-stream","--autoplay-policy=no-user-gesture-required"])
        c=await b.new_context(viewport={"width":390,"height":844},permissions=["microphone"]); pg=await c.new_page(); errs=[]
        pg.on("pageerror",lambda e:errs.append(str(e))); await pg.add_init_script(INIT)
        await pg.route("**/*googleapis.com/**",lambda r:r.fulfill(json={}))
        await pg.goto("file://"+__import__("os").getcwd()+"/index.html"); await pg.wait_for_timeout(1200)
        setup=await pg.evaluate("JSON.parse(__sent[0]).setup"); print("decls",sum(len(t.get("functionDeclarations",[])) for t in setup["tools"]))
        res={}
        async def call(name,args,wait=800,shot=None):
            await pg.evaluate("(a)=>__ws.onmessage({data:JSON.stringify({toolCall:{functionCalls:[{id:'x',name:a[0],args:a[1]}]}})})",[name,args]); await pg.wait_for_timeout(wait)
            r=json.loads(await pg.evaluate("__sent.filter(x=>x.indexOf('toolResponse')>-1).slice(-1)[0]"))["toolResponse"]["functionResponses"][0]["response"]
            print(name,"→",json.dumps({k:(v if not isinstance(v,(str,list,dict)) else (v[:44] if isinstance(v,str) else "…")) for k,v in r.items()},ensure_ascii=False))
            if shot: await pg.screenshot(path=f"tests/out/d_{shot}.png")
            return r
        async def close():
            await pg.evaluate("document.querySelector('#sheetClose').click();for(var i=0;i<6;i++)document.querySelector('#actClose').click()"); await pg.wait_for_timeout(200)
        r=await call("calendar_add",{"title":"اجتماع الإدارة","start":h(120),"minutes":60,"kind":"meeting","location":"قاعة 3"})
        mid=r["event"]["id"]
        await call("calendar_add",{"title":"موعد الأسنان","start":h(140),"kind":"appointment"},800,"clash")
        await call("calendar_add",{"title":"موعد الأسنان","start":h(140),"kind":"appointment","allow_clash":True}); await close()
        await call("calendar_add",{"title":"عشاء العائلة","start":tm+"T19:30","kind":"appointment","location":"مطعم نجد"})
        await call("reminder_add",{"text":"اتصل بالمحاسب","at":h(-1)})
        await call("show_agenda",{},900,"agenda")
        await pg.click("#actSecond"); await pg.wait_for_timeout(700); await pg.screenshot(path="tests/out/d_week.png"); await close()
        r=await call("calendar_list",{"days":3}); print("  list:",[(e["title"],e["kind"]) for e in r["events"]])
        await call("calendar_update",{"event_id":mid,"start":h(200)})
        await call("calendar_delete",{"event_id":mid},700,"del")
        print("  pre-click:",await pg.evaluate("[document.body.className,getComputedStyle(document.querySelector('.tool')).pointerEvents,getComputedStyle(document.querySelector('.tool')).opacity]"))
        try: await pg.click("#actGo",timeout=3000)
        except Exception as e: print("  CLICK FAIL; state:",await pg.evaluate("[document.body.className,document.querySelector('#act').className,getComputedStyle(document.querySelector('.tool')).pointerEvents,document.querySelector('#actGo').textContent]"))
        await pg.wait_for_timeout(400)
        print("  after delete:",[e["title"] for e in json.loads(await pg.evaluate("localStorage.getItem('musaed.cal')"))])
        print("waiting for the reminder to fire…"); await pg.wait_for_timeout(500); await pg.screenshot(path="tests/out/d_remind.png")
        print("  reminder card:",await pg.evaluate("[document.querySelector('#actTitle').textContent,document.querySelector('#actTag').textContent,document.querySelector('#actGo').textContent]"))
        print("  spoken:",[json.loads(x)["realtimeInput"]["text"][:40] for x in await pg.evaluate("__sent.filter(x=>x.indexOf('تذكير حان')>-1)")])
        await close()
        F={"trip":"oneway","from_code":"RUH","from_city":"الرياض","to_code":"JED","to_city":"جدة","date":"الأحد 15 نوفمبر","date_iso":"2026-11-15","passengers":"مسافر واحد","options":[
          {"depart_time":"9:15 ص","arrive_time":"11:00 ص","airline":"طيران ناس","duration":"ساعة و45 د","stops":"مباشرة","price":"285","tag":"cheapest"},
          {"depart_time":"7:05 ص","arrive_time":"8:50 ص","airline":"السعودية","duration":"ساعة و45 د","stops":"مباشرة","price":"340","tag":"fits_calendar"},
          {"depart_time":"6:00 ص","arrive_time":"7:40 ص","airline":"طيران أديل","duration":"ساعة و40 د","stops":"مباشرة","price":"310","tag":"earliest"},
          {"depart_time":"6:10 م","arrive_time":"9:40 م","airline":"طيران ناس","duration":"3 س و30 د","stops":"توقف واحد","price":"395","stop_details":[{"code":"dmm","city":"الدمام","arrive_time":"7:10 م","depart_time":"8:20 م","layover":"ساعة و10 د","note":"نفس الصالة"}]}]}
        await call("show_flights",F,900,"flights")
        await pg.click("#actSecond"); await pg.wait_for_timeout(600); await pg.screenshot(path="tests/out/d_flsheet.png")
        await pg.click("#sheet .cb-opts button:nth-child(4)"); await pg.wait_for_timeout(700); await pg.screenshot(path="tests/out/d_transit.png"); await close()
        F2=dict(F); F2["chosen"]=2; await call("show_flights",F2,800,"chosen"); print("  link:",await pg.evaluate("document.querySelector('#actGo').href")); await close()
        await call("show_flights",{"trip":"round","from_code":"RUH","from_city":"الرياض","to_code":"DXB","to_city":"دبي","date":"15 نوفمبر","return_date":"18 نوفمبر","options":[
          {"depart_time":"7:05 ص","arrive_time":"9:55 ص","airline":"السعودية","stops":"مباشرة","price":"890","tag":"fits_calendar","return_depart_time":"8:30 م","return_arrive_time":"9:20 م","return_stops":"مباشرة"},
          {"depart_time":"10:40 ص","arrive_time":"1:30 م","airline":"طيران ناس","stops":"مباشرة","price":"740","tag":"cheapest","return_depart_time":"11:15 م","return_arrive_time":"12:05 ص","return_stops":"مباشرة"}]},900,"round"); await close()
        await call("show_flights",{"trip":"multi","to_city":"لندن","date":"15 – 21 نوفمبر","total":"3,410","legs":[{"from_city":"الرياض","to_city":"دبي","date":"الأحد 15","depart_time":"7:05 ص","stops":"مباشرة","price":"340"},{"from_city":"دبي","to_city":"لندن","date":"الثلاثاء 17","depart_time":"12:05 م","price":"1,420"},{"from_city":"لندن","to_city":"الرياض","date":"السبت 21","depart_time":"9:10 م","price":"1,650"}]},900,"multi"); await close()
        Hh={"city":"دبي","check_in":"الأحد 15","check_out":"الأربعاء 18","nights":"3","options":[{"name":"فندق الواحة","rating":"4.6","distance":"6 دقائق من اجتماعك","price_per_night":"520","total":"1,560","cancellation":"مجاني حتى السبت 14","tag":"nearest"},{"name":"نُزل المرسى","rating":"4.3","distance":"14 دقيقة","perks":"إفطار","price_per_night":"390","tag":"cheapest"},{"name":"برج الأفق","rating":"4.8","distance":"20 دقيقة","perks":"مسبح","price_per_night":"760","tag":"top_rated"}]}
        await call("show_hotels",Hh,900,"hotels"); await pg.click("#act .cb-opts button:nth-child(1)"); await pg.wait_for_timeout(700); await pg.screenshot(path="tests/out/d_hotel.png"); await close()
        await call("show_trip",{"title":"رحلة دبي كاملة","dates":"15 – 18 نوفمبر","total":"2,450","calendar_note":"اجتماع المستثمرين الإثنين 4 م وأنت في دبي. أحوّله عن بُعد؟","parts":[{"kind":"flight","title":"ذهاب · الرياض ← دبي","detail":"الأحد 7:05 ص · السعودية","price":"340"},{"kind":"hotel","title":"فندق الواحة","detail":"3 ليالٍ","price":"1,560"},{"kind":"flight","title":"عودة · دبي ← الرياض","detail":"الأربعاء 8:30 م","price":"550"}]},900,"trip")
        print("errors",errs); await b.close()
asyncio.run(main())
