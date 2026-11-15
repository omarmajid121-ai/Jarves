import asyncio, datetime, subprocess, time, base64
src=open("tests/audit2.py").read().replace("asyncio.run(main2())","")
src=src.replace('exec(open','exec(open') 
exec(src)
FIND.clear()
srv=subprocess.Popen(["python3","-m","http.server","8765","--bind","127.0.0.1"],cwd=__import__("os").getcwd(),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
import inspect
PCM=base64.b64encode(bytes(9600)).decode()
SRFAKE="window.SpeechRecognition=window.webkitSpeechRecognition=function(){var s=this;s.start=function(){window.__sr=s;s.on=true};s.stop=function(){s.on=false}};"
now=datetime.datetime.now()
async def boot2(p,init,url):
    b=await p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox","--use-fake-device-for-media-stream","--use-fake-ui-for-media-stream","--autoplay-policy=no-user-gesture-required"])
    c=await b.new_context(viewport={"width":390,"height":844},permissions=["microphone","geolocation"],geolocation={"latitude":24.7136,"longitude":46.6753});pg=await c.new_page();pg.errs=[]
    pg.on("pageerror",lambda e:pg.errs.append(str(e)[:160]));await pg.add_init_script(init)
    H={"access-control-allow-origin":"*"};pt=(now+datetime.timedelta(minutes=5)).strftime("%H:%M")
    await pg.route("**/*googleapis.com/**",lambda r:r.fulfill(json={}))
    await pg.route("**/api.open-meteo.com/**",lambda r:r.fulfill(json={"current":{"temperature_2m":27.3,"weather_code":1},"daily":{"temperature_2m_max":[31.2],"temperature_2m_min":[17.8]}}))
    await pg.route("**/api.aladhan.com/**",lambda r:r.fulfill(json={"code":200,"data":{"timings":{"Fajr":"04:48","Dhuhr":"11:38","Asr":"14:45","Maghrib":pt,"Isha":"23:59"}}}))
    await pg.route("**/nominatim.openstreetmap.org/**",lambda r:r.fulfill(json=[{"lat":"24.80","lon":"46.70","display_name":"حي الملقا، الرياض"}],headers=H))
    await pg.route("**/router.project-osrm.org/**",lambda r:r.fulfill(json={"code":"Ok","routes":[{"distance":18200,"duration":1800,"geometry":{"coordinates":[[46.68,24.71],[46.70,24.80]]},"legs":[{"steps":[]}]}]},headers=H))
    await pg.route("**/tile.openstreetmap.org/**",lambda r:r.fulfill(body=PNG,content_type="image/png"))
    await pg.goto(url);await pg.wait_for_timeout(1500)
    async def call(name,args,wait=700):
        n=await pg.evaluate("__sent.filter(x=>x.indexOf('toolResponse')>-1).length")
        await pg.evaluate("(a)=>__ws.onmessage({data:JSON.stringify({toolCall:{functionCalls:[{id:'x',name:a[0],args:a[1]}]}})})",[name,args])
        for _ in range(60):
            await pg.wait_for_timeout(150)
            if await pg.evaluate("__sent.filter(x=>x.indexOf('toolResponse')>-1).length")>n: break
        else: F("HIGH",name,"no answer"); return {}
        await pg.wait_for_timeout(wait)
        return json.loads(await pg.evaluate("__sent.filter(x=>x.indexOf('toolResponse')>-1).slice(-1)[0]"))["toolResponse"]["functionResponses"][0]["response"]
    async def card(): return await pg.evaluate("[document.querySelector('#act').classList.contains('on'),document.querySelector('#actTitle').textContent,document.querySelector('#actTag').textContent,document.querySelector('#actGo').hidden?'':document.querySelector('#actGo').textContent,document.querySelector('#actGo').getAttribute('href')||'']")
    async def close(): await pg.evaluate("document.querySelector('#sheetClose').click();for(var i=0;i<6;i++)document.querySelector('#actClose').click()");await pg.wait_for_timeout(200)
    return b,pg,call,card,close
async def go():
    async with async_playwright() as p:
        INIT2=wsvar(NOG,WS_COUNT)+SRFAKE+"window.open=function(u){(window.__opened=window.__opened||[]).push(u);return null};"
        b,pg,call,card,close=await boot2(p,INIT2,"http://127.0.0.1:8765/index.html")
        msg=lambda o: pg.evaluate("o=>__ws.onmessage({data:JSON.stringify(o)})",o)
        last=lambda: pg.evaluate("__sent.map(x=>JSON.parse(x)).filter(x=>x.realtimeInput&&x.realtimeInput.text).map(x=>x.realtimeInput.text).slice(-1)[0]||''")
        # app install pieces
        mf=await pg.evaluate("fetch('manifest.json').then(r=>r.json()).then(j=>[j.name,j.display,j.shortcuts[0].url])");sw=await pg.evaluate("navigator.serviceWorker.getRegistration().then(r=>!!r)")
        print(" manifest:",mf,"| service worker:",sw)
        if not sw: F("MED","install","service worker not registered")
        # places & people
        r=await call("my_places",{"action":"set","name":"البيت","here":True},900);print(" save home here:",r)
        r=await call("my_places",{"action":"set","name":"الدوام","address":"برج المملكة"},900);print(" save work:",r.get("saved"),(await card())[1:3]);await close()
        r=await call("show_route",{"destination":"الشغل"},1200);c=await card();print(" route to «الشغل»:",c[1],"| link:",c[4][:80])
        if "الدوام" not in c[1] or "24.800000" not in c[4]: F("HIGH","places","route to a saved place did not use it")
        await close()
        r=await call("my_people",{"action":"set","relation":"أمي","name":"فاطمة","number":"0501234567"});r=await call("contacts_find",{"name":"أمي"});print(" «أمي» →",r);await close()
        if not r.get("matches"): F("HIGH","people","«أمي» not resolved")
        # screen awareness
        await call("show_places",{"title":"صيدليات","places":[{"name":"النهدي","area":"العليا"},{"name":"الدواء","area":"الورود"}]})
        r=await call("screen_now",{});print(" screen_now:",json.dumps(r,ensure_ascii=False)[:150])
        r=await call("screen_tap",{"target":"option","n":2});print(" tap before he speaks:",r.get("error","")[:50])
        await msg({"serverContent":{"inputTranscription":{"text":"الثاني"}}})
        r=await call("screen_tap",{"target":"option","n":2});op=await pg.evaluate("window.__opened||[]");print(" after «الثاني»:",r,"| opened:",op[-1][-40:] if op else None)
        if not r.get("done"): F("HIGH","screen","could not pick an option by voice")
        await msg({"serverContent":{"turnComplete":True}});await close()
        # quality numbers
        await msg({"serverContent":{"inputTranscription":{"text":"وش الطقس"}}});await pg.wait_for_timeout(900)
        await msg({"serverContent":{"modelTurn":{"parts":[{"inlineData":{"mimeType":"audio/pcm;rate=24000","data":PCM}}]}}});await msg({"serverContent":{"turnComplete":True}})
        await msg({"serverContent":{"inputTranscription":{"text":"لا مو كذا قصدي جدة"}}});await msg({"serverContent":{"turnComplete":True}})
        await call("calendar_delete",{"event_id":"zzz"});q=await pg.evaluate("__mz2().qm");print(" quality:",q)
        if q["turns"]<3 or q["corrections"]<1 or q["commands_failed"]<1 or not q["median_ms"]: F("MED","quality","numbers not counted")
        await pg.evaluate("__t.openCard('set')");await pg.wait_for_timeout(300);dg=await pg.evaluate("document.querySelector('#diag').textContent");print(" status screen:",dg[dg.find('الجودة'):][:120].replace("\n"," | "));await pg.evaluate("__t.closeCard()")
        # understanding test (mocked Google)
        async def gfun(route):
            rq=route.request
            if rq.method=="GET": return await route.fulfill(json={"models":[{"name":"models/gemini-3.5-flash-lite","supportedGenerationMethods":["generateContent"]},{"name":"models/gemini-3.8-flash","supportedGenerationMethods":["generateContent"]}]})
            bd=json.loads(rq.post_data);txt=bd["contents"][0]["parts"][0].get("text","")
            if "functionDeclarations" in json.dumps(bd.get("tools",[])):
                nm="today_data" if ("جو" in txt or "حرار" in txt) else "web_search"
                return await route.fulfill(json={"candidates":[{"content":{"parts":[{"functionCall":{"name":nm,"args":{}}}]}}]})
            if "summarise a meeting" in json.dumps(bd):
                return await route.fulfill(json={"candidates":[{"content":{"parts":[{"text":json.dumps({"summary":"اتفقنا على إطلاق المرحلة الثانية.","decisions":["الإطلاق في يناير"],"tasks":[{"task":"إرسال العرض للعميل","owner":"أنا","due":(now+datetime.timedelta(days=2)).strftime("%Y-%m-%d")},{"task":"تجهيز الميزانية","owner":"خالد","due":""}]},ensure_ascii=False)}]}}]})
            await route.fulfill(json={"candidates":[{"content":{"parts":[{"text":"ملخص"}]}}]})
        await pg.route(re.compile(r"generativelanguage\.googleapis\.com/v1beta/models"),gfun)
        await pg.evaluate("__t.openCard('set')");await pg.wait_for_timeout(300);await pg.evaluate("document.querySelector('#qtBtn').click()")
        for _ in range(60):
            await pg.wait_for_timeout(1000)
            c=await card()
            if c[0] and "اختبار الفهم" in c[1]: break
        print(" understanding test:",c[1:3]);await pg.screenshot(path="tests/out/q_test.png")
        if "اختبار الفهم" not in c[1]: F("MED","test bank","runner did not finish")
        await close()
        # prayer and Ramadan moments
        await pg.evaluate("localStorage.setItem('musaed.ramadanTest','1')");await call("show_brief",{},1500);await pg.evaluate("document.querySelector('#briefClose').click()")
        r=await call("prayer_mode",{});print(" prayer mode:",r.get("on"),"| ramadan:",r.get("ramadan"))
        await pg.evaluate("localStorage.setItem('musaed.mom','[]')");await pg.evaluate("__t.momTick()");await pg.wait_for_timeout(600);c=await card();print(" moment card:",c[1:3])
        if not c[0]: F("MED","moments","no prayer or iftar notice")
        await close()
        # leave now
        st=(now+datetime.timedelta(minutes=40)).strftime("%Y-%m-%dT%H:%M")
        await call("calendar_add",{"allow_prayer":True,"title":"اجتماع العميل","start":st,"kind":"meeting","location":"الدوام"});await close()
        await pg.evaluate("localStorage.setItem('musaed.mom','[]')");await pg.evaluate("__t.momTick()");await pg.wait_for_timeout(1500)
        for _ in range(4):
            c=await card()
            if c[0] and "اطلع" in c[1]: break
            await pg.evaluate("document.querySelector('#actClose').click()");await pg.wait_for_timeout(200)
        print(" leave-now:",c[1:4],"| she was told:",(await last())[:60])
        if "اطلع" not in c[1]: F("HIGH","moments","no leave-now alert")
        await close()
        # place reminder (leave)
        r=await call("place_reminder",{"action":"add","text":"اشتري خبز","place":"هنا","when":"leave"},900);print(" place reminder:",r.get("saved"),r.get("place"));await close()
        await pg.context.set_geolocation({"latitude":24.7300,"longitude":46.6900});await pg.wait_for_timeout(2500);c=await card();print(" after leaving:",c[1:3])
        if "خبز" not in c[1]: F("HIGH","place reminder","did not fire on leaving")
        await close()
        # driving mode
        r=await call("driving_mode",{"on":True});await call("show_card",{"title":"اختبار","rows":[{"label":"أ","value":"ب"}]});vis=await pg.evaluate("[document.body.classList.contains('driving'),getComputedStyle(document.querySelector('#act .cb-kv')).display]");print(" driving:",vis);await close()
        await call("driving_mode",{"on":False})
        # meeting mode
        r=await call("meeting_mode",{"action":"start","title":"اجتماع المرحلة الثانية"});await pg.wait_for_timeout(4500)
        st=await pg.evaluate("[__mz2().MT,!!window.__sr&&__sr.on,document.querySelector('#actTitle').textContent]");print(" meeting started:",st)
        for t in ["نبدأ بمراجعة المرحلة الأولى","اتفقنا نطلق المرحلة الثانية في يناير","عمر يرسل العرض للعميل بعد يومين","وخالد يجهز الميزانية"]:
            await pg.evaluate("t=>__sr.onresult({resultIndex:0,results:[{0:{transcript:t},isFinal:true,length:1}]})",t)
        await pg.wait_for_timeout(300);print(" live text on card:",(await pg.evaluate("document.querySelector('#actBlocks').innerText"))[:60].replace("\n"," | "))
        await pg.evaluate("document.querySelector('#actGo').click()");await pg.wait_for_timeout(4000)
        c=await card();bl=await pg.evaluate("document.querySelector('#actBlocks').innerText");print(" summary card:",c[1:4],"|",bl[:120].replace("\n"," | "))
        if "ملخص" not in c[1]: F("HIGH","meeting","no summary")
        await pg.evaluate("document.querySelector('#actGo').click()");await pg.wait_for_timeout(500)
        nt=await pg.evaluate("JSON.parse(localStorage.getItem('musaed.notes')||'[]').slice(-2).map(x=>x.x.slice(0,50))");cal=await pg.evaluate("JSON.parse(localStorage.getItem('musaed.cal')||'[]').filter(x=>x.title.indexOf('العرض')>-1).length")
        print(" saved notes:",nt,"| my tasks as reminders:",cal)
        await pg.screenshot(path="tests/out/m_sum.png")
        print(" errors",pg.errs);await b.close()
        # quick start
        b,pg,call,card,close=await boot2(p,wsvar(NOG,WS_COUNT),"http://127.0.0.1:8765/index.html?listen=1")
        await pg.wait_for_timeout(1200);n=await pg.evaluate("window.__wsN||0");print(" quick start ?listen=1 connects:",n>0,"| url now:",await pg.evaluate("location.search"))
        if not n: F("HIGH","quick start","did not start listening")
        await b.close()
    srv.terminate()
    print("FINDINGS",len(FIND))
    for f in FIND: print(" ",f)
asyncio.run(go())
