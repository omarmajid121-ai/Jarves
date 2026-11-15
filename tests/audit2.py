import asyncio, sys, time
sys.argv=["x","none"]
exec(open("tests/audit.py").read().replace("asyncio.run(main())",""))
FULL=INIT
COUNT="window.__wsN=0;"
def wsvar(init,body):
    a=init.index("window.WebSocket=function(u){");b=init.index("};",init.index("setTimeout(function(){w.onopen&&w.onopen()},20)"))+2
    return init[:a]+body+init[b:]
WS_COUNT="window.__wsN=0;window.__all=[];window.WebSocket=function(u){var w=this;window.__ws=w;__wsN++;__all.push(w);w.readyState=1;w.send=function(x){__sent.push(x);var m=JSON.parse(x);if(m.setup)setTimeout(function(){w.onmessage({data:JSON.stringify({setupComplete:{}})})},50)};w.close=function(){w.readyState=3};setTimeout(function(){w.onopen&&w.onopen()},20)};"
WS_NOREADY="window.__wsN=0;window.WebSocket=function(u){var w=this;window.__ws=w;__wsN++;w.readyState=1;w.send=function(x){__sent.push(x)};w.close=function(){};setTimeout(function(){w.onopen&&w.onopen()},20)};"
WS_BADKEY="window.__wsN=0;window.WebSocket=function(u){var w=this;window.__ws=w;__wsN++;w.readyState=1;w.send=function(x){__sent.push(x);setTimeout(function(){w.onclose&&w.onclose({code:1007,reason:'API key not valid. Please pass a valid API key.'})},40)};w.close=function(){};setTimeout(function(){w.onopen&&w.onopen()},20)};"
async def hang(route):
    try: await asyncio.sleep(40); await route.abort()
    except Exception: pass
texts=lambda pg: pg.evaluate("__sent.map(function(x){try{var m=JSON.parse(x);return m.realtimeInput&&typeof m.realtimeInput.text==='string'?m.realtimeInput.text:null}catch(e){return null}}).filter(Boolean)")
async def timed(pg,name,args,limit=25):
    n=await pg.evaluate("__sent.filter(x=>x.indexOf('toolResponse')>-1).length");t=time.time()
    await pg.evaluate("(a)=>__ws.onmessage({data:JSON.stringify({toolCall:{functionCalls:[{id:'x',name:a[0],args:a[1]}]}})})",[name,args])
    while time.time()-t<limit:
        await pg.wait_for_timeout(250)
        if await pg.evaluate("__sent.filter(x=>x.indexOf('toolResponse')>-1).length")>n:
            r=json.loads(await pg.evaluate("__sent.filter(x=>x.indexOf('toolResponse')>-1).slice(-1)[0]"))["toolResponse"]["functionResponses"][0]["response"];return round(time.time()-t,1),r
    return None,None
async def visible(pg,sel="#actTitle"):
    return await pg.evaluate("(s)=>{var e=document.querySelector(s),r=e.getBoundingClientRect(),t=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);return !!t&&!!t.closest('#act')}",sel)
async def A(p):
    print("== A services that never answer")
    for label,pats,name,args in [("weather",["**/api.open-meteo.com/**"],"today_data",{"show":"weather"}),("prayer times",["**/api.aladhan.com/**"],"today_data",{"show":"prayer"}),("photo",["**/*.wikipedia.org/**"],"show_photo",{"query":"الربع الخالي"}),("map search",["**/nominatim.openstreetmap.org/**"],"show_route",{"destination":"المطار"}),("map route",["**/router.project-osrm.org/**"],"show_route",{"destination":"المطار"})]:
        b,pg,call,lay,card,close=await boot(p,390,844,NOG)
        for pat in pats: await pg.route(pat,hang)
        t,r=await timed(pg,name,args);print(f" {label}: answer after",t,"s",json.dumps(r,ensure_ascii=False)[:110] if r else "")
        if t is None: F("HIGH",label,"service does not answer: she gets nothing back for 25 s and stays silent")
        elif t>12: F("MED",label,f"service does not answer: she waits {t} s before she can speak")
        await b.close()
    b,pg,call,lay,card,close=await boot(p,390,844,FULL);await pg.route("**/*googleapis.com/**",hang)
    for name,args in [("calendar_list",{"days":1}),("email_list",{}),("tasks_list",{})]:
        t,r=await timed(pg,name,args);print(f" google {name}: answer after",t,"s",json.dumps(r,ensure_ascii=False)[:90] if r else "")
        if t is None: F("HIGH","Google "+name,"Google does not answer: she gets nothing back for 25 s and stays silent")
        elif t>12: F("MED","Google "+name,f"she waits {t} s")
    await b.close()
async def B(p):
    print("== B connection problems")
    b,pg,call,lay,card,close=await boot(p,390,844,wsvar(NOG,WS_NOREADY));await pg.wait_for_timeout(22000)
    st=await pg.evaluate("[document.querySelector('#state').textContent,document.querySelector('#caption').textContent,document.querySelector('#endBtn').hidden,__wsN]");print(" server accepts but never answers, after 23 s:",st)
    if "الاتصال" in st[0]: F("MED","connecting","if Google never answers, the screen stays on «جارٍ الاتصال…» with no message")
    await b.close()
    b,pg,call,lay,card,close=await boot(p,390,844,wsvar(NOG,WS_BADKEY));await pg.wait_for_timeout(800)
    print(" wrong key:",await pg.evaluate("[document.querySelector('#caption').textContent,document.querySelector('#card').classList.contains('open'),__wsN]"));await b.close()
    MIC="navigator.mediaDevices.getUserMedia=function(){return Promise.reject(new Error('denied'))};"
    b,pg,call,lay,card,close=await boot(p,390,844,wsvar(NOG,WS_COUNT)+MIC);await pg.wait_for_timeout(600)
    st=await pg.evaluate("[document.querySelector('#state').textContent,document.querySelector('#caption').textContent,__wsN,__all.filter(w=>w.readyState===1).length]");tx=await texts(pg);print(" microphone refused:",st,"| she was asked to greet:",len(tx))
    await pg.mouse.click(195,420);await pg.wait_for_timeout(700);st2=await pg.evaluate("[__wsN,__all.filter(w=>w.readyState===1).length]");print("   after he taps to retry: connections made, still open:",st2)
    if st[3]>0: F("MED","microphone refused","the voice connection stays open in the background, so she may greet him while the screen says it is stopped")
    if st2[1]>1: F("HIGH","microphone refused","tapping again opens a second voice connection on top of the first")
    await b.close()
async def C(p):
    print("== C session ends / leaving the app")
    b,pg,call,lay,card,close=await boot(p,390,844,wsvar(NOG,WS_COUNT))
    await call("show_flights",FL);await pg.wait_for_timeout(21000)
    await pg.evaluate("__ws.onmessage({data:JSON.stringify({goAway:{timeLeft:'5s'}})})");await pg.wait_for_timeout(300)
    await pg.evaluate("__ws.onclose({code:1000,reason:''})");await pg.wait_for_timeout(1200)
    tx=await texts(pg);c=await card();su=await pg.evaluate("__sent.filter(x=>x.indexOf('systemInstruction')>-1).map(x=>Object.keys(JSON.parse(x).setup))");print(" Google closes the session after 21 s: connections",await pg.evaluate("__wsN"),"| card still on:",c[0],"| she is told:",tx[-1][:70]);print("   setup keys:",su[-1])
    if "function softConnect(" not in open("index.html").read(): F("HIGH","long conversations","Google ends every voice connection after about 10 minutes; she then starts a new session, greets him again and keeps only the last few lines of the talk")
    await pg.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:function(){return true}});document.dispatchEvent(new Event('visibilitychange'))");await pg.wait_for_timeout(400)
    live1=await pg.evaluate("document.querySelector('#state').textContent")
    await pg.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:function(){return false}});document.dispatchEvent(new Event('visibilitychange'))");await pg.wait_for_timeout(1200)
    tx=await texts(pg);c=await card();print(" he leaves to book and comes back: while away:",live1,"| card still on:",c[0],c[1][:20],"| she is told:",tx[-1][:70])
    if "رجعت" in tx[-1]: F("MED","leaving the app","after he opens a booking page, WhatsApp or the dialer and returns, she starts a fresh session with a welcome and does not know what he just did")
    await b.close()
async def D(p):
    print("== D cards hidden behind other screens")
    b,pg,call,lay,card,close=await boot(p,390,844,NOG)
    await call("show_brief",{},1200);await call("reminder_add",{"text":"اتصل بالمحاسب","at":h(-1)},200);await pg.wait_for_timeout(27000)
    c=await card();v=await visible(pg) if c[0] else False;print(" reminder while the Today page is open: card on:",c[0],c[2],"| can he see it:",v)
    if c[0] and not v: F("HIGH","reminder","a reminder that fires while the Today page is open is hidden behind it")
    await pg.evaluate("document.querySelector('#briefClose').click()");await close()
    await pg.click("#setBtn");await pg.wait_for_timeout(500);await call("reminder_add",{"text":"موعد الدواء","at":h(-1)},200);await pg.wait_for_timeout(27000)
    c=await card();v=await visible(pg) if c[0] else False;print(" reminder while Settings is open: card on:",c[0],"| can he see it:",v)
    if c[0] and not v: F("MED","reminder","a reminder that fires while Settings or My data is open is hidden behind it")
    await pg.evaluate("document.querySelector('#card').classList.remove('open')");await close();await b.close()
async def E(p):
    print("== E taps she is not told about, and voice-only confirmation")
    b,pg,call,lay,card,close=await boot(p,390,844,NOG)
    async def tap(label,sel,expect_told=True,sev="MED",what=""):
        n=len(await texts(pg));await pg.click(sel);await pg.wait_for_timeout(600);tx=await texts(pg);told=len(tx)>n
        print(f" {label}: she is told:",told,"|",(tx[-1][:60] if told else ""),"| card now:",(await card())[:2])
        if expect_told and not told: F(sev,label,what)
    r=await call("calendar_add",{"allow_prayer":True,"title":"اجتماع الفريق","start":h(600),"kind":"meeting"});eid=r["event"]["id"];await close()
    r=await call("calendar_delete",{"event_id":eid});r2=await call("calendar_delete",{"event_id":eid});print(" delete by voice, asked twice:",json.dumps(r2,ensure_ascii=False)[:120])
    if r2.get("awaiting_user_confirmation") and "confirm" not in json.dumps(r2).replace("confirmation","").replace("confirm card",""): F("MED","delete by voice","a meeting or document can be deleted only by tapping; saying «نعم احذف» does nothing")
    await tap("tap Delete on the confirm card","#actGo",True,"MED","after he taps Delete she is not told, so she may ask again or think it is still there")
    await close();await call("calendar_add",{"allow_prayer":True,"title":"موعد أ","start":h(700),"kind":"appointment"});r=await call("calendar_add",{"allow_prayer":True,"title":"موعد ب","start":h(710),"kind":"appointment"});print(" clash card buttons:",(await card())[3],"|",await pg.evaluate("document.querySelector('#actSecond').hidden?'':document.querySelector('#actSecond').textContent"))
    await tap("tap the main button on the clash card","#actGo",True,"MED","after he decides on the clash card she is not told what he chose")
    await close();await pg.route(re.compile(r"generativelanguage\.googleapis\.com/v1beta/models/.*generateContent"),lambda r:r.fulfill(json={"candidates":[{"content":{"parts":[{"text":json.dumps({"kind":"boarding","flight":"SV1023","from_code":"RUH","to_code":"JED","to_city":"جدة","date":"2026-11-20","time":"07:05"},ensure_ascii=False)}]}}]}))
    await pg.evaluate("document.querySelector('#docImg').value=''");await pg.set_input_files("#docImg","tests/docs/bp.png");await pg.wait_for_timeout(2600)
    await tap("tap Save on the uploaded document","#actGo",True,"MED","she asked «أحفظها؟»; after he taps Save she is not told, and a spoken «نعم» afterwards gets an error")
    r=await call("doc_confirm",{"save":True});print("   then he also says yes:",json.dumps(r,ensure_ascii=False)[:90]);await close()
    await call("reminder_add",{"text":"اتصل بالمحاسب","at":h(-1)},200);await pg.wait_for_timeout(27000)
    await tap("tap Done on a reminder","#actGo",False);await close()
    await call("show_trip",TR);print(" trip card buttons:",(await card())[3],(await card())[4][:50]);await close()
    await call("device_action",{"name":"رنج روفر"});c=await card();print(" car card:",c[3],c[4][:60]);await close()
    # typed text
    await pg.evaluate("var q=document.querySelector('#q');if(q){q.value='وش أخبار اليوم';q.form?q.form.requestSubmit():0}");await pg.wait_for_timeout(400);tx=await texts(pg);print(" typed message reaches her:",tx[-1][:30] if tx else None)
    # end then reminder
    await pg.evaluate("document.querySelector('#endBtn').click()");await pg.wait_for_timeout(400);n=len(await texts(pg));await call("reminder_add",{"text":"بعد الإنهاء","at":h(-1)},200) if False else None
    if pg.errs: F("HIGH","script errors",str(pg.errs[:3]))
    await b.close()
async def main2():
    async with async_playwright() as p:
        for f in [A,B,C,D,E]:
            try: await f(p)
            except Exception as e: print("  TEST ERROR in",f.__name__,str(e)[:300])
    print("\nFINDINGS",len(FIND))
    for f in sorted(set(FIND)): print(" ",f)
asyncio.run(main2())
