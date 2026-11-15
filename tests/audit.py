import asyncio, json, re, datetime, base64, sys
from playwright.async_api import async_playwright
src=open("tests/t3.py").read()
INIT=re.search(r'INIT="""(.*?)"""',src,re.S).group(1)
WSONLY=INIT[INIT.index("window.__sent=[]"):]
NOG=re.sub(r"localStorage.setItem\('musaed.gtok'.*?\);\n","",INIT,flags=re.S).replace("localStorage.setItem('musaed.gid','123-abc.apps.googleusercontent.com');","")
PNG=base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
now=datetime.datetime.now();h=lambda add:(now+datetime.timedelta(minutes=add)).strftime("%Y-%m-%dT%H:%M");tm=(now+datetime.timedelta(days=1)).strftime("%Y-%m-%d")
LAY="""()=>{var out=[],vh=innerHeight,vw=innerWidth,sh=document.querySelector('#sheet'),a=(sh&&sh.classList.contains('on'))?sh:document.querySelector('#act');
 if(!a.classList.contains('on'))return ['NO CARD ON SCREEN'];var r=a.getBoundingClientRect();
 if(r.top<-1)out.push('card starts above the screen by '+Math.round(-r.top)+'px');if(r.bottom>vh+1)out.push('card ends below the screen by '+Math.round(r.bottom-vh)+'px');
 var sc=a.scrollHeight>a.clientHeight+2;
 a.querySelectorAll('*').forEach(function(e){var cs=getComputedStyle(e);if(cs.display==='none'||e.hidden||e.closest('[hidden]'))return;var b=e.getBoundingClientRect();if(!b.width||!b.height)return;
  if(!e.closest('.cb-map')&&(b.left<r.left-1||b.right>r.right+1))out.push('spills sideways: .'+e.className+' "'+(e.textContent||'').trim().slice(0,22)+'"');
  if(e.children.length===0&&e.scrollWidth>e.clientWidth+2&&cs.overflow!=='visible'&&cs.textOverflow!=='ellipsis')out.push('text cut: .'+e.className+' "'+(e.textContent||'').trim().slice(0,22)+'"');
  var ab=document.querySelector('#actBlocks');if(!sc&&!(e.closest('.cb-map')&&!e.classList.contains('cb-map'))&&!(ab&&ab.contains(e)&&ab.scrollHeight>ab.clientHeight+2)&&(b.bottom>r.bottom+1))out.push('cut at the bottom: .'+e.className+' "'+(e.textContent||'').trim().slice(0,22)+'"')});
 a.querySelectorAll('button,a').forEach(function(e){if(e.hidden||e.closest('[hidden]')||getComputedStyle(e).display==='none')return;var b=e.getBoundingClientRect();if(b.height&&b.height<40)out.push('small tap target '+Math.round(b.height)+'px: "'+(e.textContent||e.getAttribute('aria-label')||e.className).trim().slice(0,16)+'"')});
 return out.filter(function(x,i){return out.indexOf(x)===i}).slice(0,6)}"""
FIND=[]
def F(sev,where,what): FIND.append((sev,where,what)); print("  !!",sev,where,"-",what)
async def boot(p,vw,vh,init,routes=True,offline=False):
    b=await p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox","--use-fake-device-for-media-stream","--use-fake-ui-for-media-stream","--autoplay-policy=no-user-gesture-required","--allow-file-access-from-files"])
    c=await b.new_context(viewport={"width":vw,"height":vh},permissions=["microphone"]);pg=await c.new_page();pg.errs=[]
    pg.on("pageerror",lambda e:pg.errs.append(str(e)[:160]));await pg.add_init_script(init)
    H={"access-control-allow-origin":"*"}
    await pg.route("**/*googleapis.com/**",lambda r:r.fulfill(json={}))
    if offline:
        for pat in ["**/api.open-meteo.com/**","**/api.aladhan.com/**","**/*.wikipedia.org/**","**/nominatim.openstreetmap.org/**","**/router.project-osrm.org/**"]: await pg.route(pat,lambda r:r.abort())
    elif routes:
        await pg.route("**/api.open-meteo.com/**",lambda r:r.fulfill(json={"current":{"temperature_2m":27.3,"weather_code":1},"daily":{"temperature_2m_max":[31.2],"temperature_2m_min":[17.8]}}))
        await pg.route("**/api.aladhan.com/**",lambda r:r.fulfill(json={"code":200,"data":{"timings":{"Fajr":"04:48","Dhuhr":"11:38","Asr":"14:45","Maghrib":"17:07","Isha":"18:37"}}}))
        await pg.route("**/*.wikipedia.org/**",lambda r:r.fulfill(json={"query":{"pages":{"1":{"index":1,"title":"الربع الخالي","fullurl":"https://ar.wikipedia.org/wiki/X","thumbnail":{"source":"https://upload.wikimedia.org/a.png"}}}}},headers=H))
        await pg.route("**/upload.wikimedia.org/**",lambda r:r.fulfill(body=PNG,content_type="image/png"))
        await pg.route("**/nominatim.openstreetmap.org/**",lambda r:r.fulfill(json=[{"lat":"24.95","lon":"46.70","display_name":"مطار الملك خالد"}],headers=H))
        await pg.route("**/router.project-osrm.org/**",lambda r:r.fulfill(json={"code":"Ok","routes":[{"distance":18200,"duration":1440,"geometry":{"coordinates":[[46.68,24.71],[46.69,24.80],[46.70,24.95]]},"legs":[{"steps":[{"name":"طريق الملك فهد","distance":12000,"maneuver":{"type":"depart"}},{"name":"طريق المطار","distance":6200,"maneuver":{"type":"turn","modifier":"right"}}]}]}]},headers=H))
        await pg.route("**/tile.openstreetmap.org/**",lambda r:r.fulfill(body=PNG,content_type="image/png"))
    await pg.goto("file://"+__import__("os").getcwd()+"/index.html");await pg.wait_for_timeout(1300)
    async def call(name,args,wait=700):
        n=await pg.evaluate("__sent.filter(x=>x.indexOf('toolResponse')>-1).length")
        await pg.evaluate("(a)=>__ws.onmessage({data:JSON.stringify({toolCall:{functionCalls:[{id:'x',name:a[0],args:a[1]}]}})})",[name,args])
        for _ in range(40):
            await pg.wait_for_timeout(150)
            if await pg.evaluate("__sent.filter(x=>x.indexOf('toolResponse')>-1).length")>n: break
        else: F("HIGH",name,"no answer to the assistant within 6 s: "+json.dumps(args,ensure_ascii=False)[:60]); return {}
        await pg.wait_for_timeout(wait)
        return json.loads(await pg.evaluate("__sent.filter(x=>x.indexOf('toolResponse')>-1).slice(-1)[0]"))["toolResponse"]["functionResponses"][0]["response"]
    async def lay(where):
        for x in await pg.evaluate(LAY): F("MED" if "tap target" in x else "HIGH",f"{where} @{vw}x{vh}",x)
    async def card(): return await pg.evaluate("[document.querySelector('#act').classList.contains('on'),document.querySelector('#actTitle').textContent,document.querySelector('#actTag').textContent,document.querySelector('#actGo').hidden?'':document.querySelector('#actGo').textContent,document.querySelector('#actGo').getAttribute('href')||'',document.querySelector('#actBody').textContent]")
    async def close():
        await pg.evaluate("document.querySelector('#sheetClose').click();for(var i=0;i<6;i++)document.querySelector('#actClose').click()");await pg.wait_for_timeout(200)
    return b,pg,call,lay,card,close
LONG="اجتماع مراجعة خطة التوسع الإقليمي مع فريق الاستثمار والشركاء الاستراتيجيين في المنطقة"
FL={"trip":"oneway","from_code":"RUH","from_city":"الرياض","to_code":"JED","to_city":"جدة","date":"الأحد 15 نوفمبر","date_iso":"2026-11-15","passengers":"مسافر واحد","options":[{"depart_time":"9:15 ص","arrive_time":"11:00 ص","airline":"طيران ناس","duration":"ساعة و45 د","stops":"مباشرة","price":"285","tag":"cheapest"},{"depart_time":"7:05 ص","arrive_time":"8:50 ص","airline":"الخطوط الجوية العربية السعودية","duration":"ساعة و45 د","stops":"مباشرة","price":"12,340","tag":"fits_calendar"},{"depart_time":"6:00 ص","arrive_time":"7:40 ص","airline":"طيران أديل","duration":"ساعة و40 د","stops":"مباشرة","price":"310","tag":"earliest"},{"depart_time":"6:10 م","arrive_time":"9:40 م","airline":"طيران ناس","duration":"3 س و30 د","stops":"توقف واحد","price":"395","stop_details":[{"code":"dmm","city":"الدمام","arrive_time":"7:10 م","depart_time":"8:20 م","wait":"ساعة و10 د"}]},{"depart_time":"11:00 م","arrive_time":"12:45 ص","airline":"السعودية","stops":"مباشرة","price":"420"},{"depart_time":"1:00 م","arrive_time":"2:45 م","airline":"طيران ناس","stops":"مباشرة","price":"300"}]}
RT={"trip":"round","from_code":"RUH","from_city":"الرياض","to_code":"LHR","to_city":"لندن","date":"15 نوفمبر","return_date":"28 نوفمبر","options":[{"depart_time":"10:05 ص","arrive_time":"12:55 م","airline":"الخطوط الجوية العربية السعودية","stops":"توقف واحد في جدة","price":"3,890","tag":"fits_calendar","return_depart_time":"10:30 م","return_arrive_time":"11:20 ص","return_stops":"توقف واحد"},{"depart_time":"10:40 ص","arrive_time":"1:30 م","airline":"طيران ناس","stops":"مباشرة","price":"2,740","tag":"cheapest","return_depart_time":"11:15 م","return_arrive_time":"12:05 ص","return_stops":"مباشرة"},{"depart_time":"2:40 ص","arrive_time":"7:30 ص","airline":"البريطانية","stops":"مباشرة","price":"4,100","return_depart_time":"1:15 م","return_arrive_time":"10:05 م","return_stops":"مباشرة"}]}
HT={"city":"دبي","check_in":"الأحد 15","check_out":"الأربعاء 18","nights":"3","options":[{"name":"فندق ومنتجع الواحة الملكي للأجنحة الفندقية","rating":"4.6","distance":"6 دقائق من اجتماعك","price_per_night":"1,520","total":"4,560","tag":"closest"},{"name":"نُزل المرسى","rating":"4.3","distance":"14 دقيقة","price_per_night":"390","total":"1,170","tag":"cheapest"},{"name":"برج الأفق","rating":"4.8","distance":"20 دقيقة","price_per_night":"760","total":"2,280","tag":"top_rated"},{"name":"فندق النخيل","rating":"4.1","distance":"25 دقيقة","price_per_night":"300","total":"900"}]}
TR={"title":"رحلة دبي كاملة","dates":"15 – 18 نوفمبر","total":"2,450","calendar_note":"اجتماع المستثمرين الإثنين 4 م وأنت في دبي. أحوّله عن بُعد؟","parts":[{"kind":"flight","title":"ذهاب · الرياض ← دبي","detail":"الأحد 7:05 ص · السعودية","price":"340"},{"kind":"hotel","title":"فندق الواحة","detail":"3 ليالٍ","price":"1,560"},{"kind":"car","title":"سيارة من المطار","detail":"3 أيام","price":"400"},{"kind":"flight","title":"عودة · دبي ← الرياض","detail":"الأربعاء 8:30 م","price":"550"}]}
async def sweep(p,vw,vh):
    print(f"== layout sweep {vw}x{vh}")
    b,pg,call,lay,card,close=await boot(p,vw,vh,NOG)
    await call("show_action",{"type":"call","name":"محمد العتيبي أبو عبدالله","number":"+966500000000","reason":"تأجيل اجتماع الأحد إلى يوم الإثنين الساعة 11 صباحًا في مكتب الرياض"});await lay("call card");await close()
    await call("show_action",{"type":"whatsapp","name":"سارة","number":"0555555555","text":"السلام عليكم، بتأخر ربع ساعة عن الموعد بسبب الزحمة، أعتذر منك وأشوفك هناك إن شاء الله. "*2});await lay("whatsapp card");await close()
    await call("calendar_add",{"allow_prayer":True,"title":LONG,"start":h(120),"minutes":60,"kind":"meeting","location":"قاعة الاجتماعات الكبرى، الدور 14، برج المملكة"})
    await call("calendar_add",{"allow_prayer":True,"title":"موعد الأسنان","start":h(140),"kind":"appointment"});await lay("clash card");await close()
    for i in range(5): await call("calendar_add",{"allow_prayer":True,"title":f"موعد رقم {i+1} مع عميل مهم","start":h(300+i*70),"kind":"appointment","allow_clash":True},150)
    await close();await call("show_agenda",{});await lay("agenda card");await pg.click("#actSecond");await pg.wait_for_timeout(500);await lay("week sheet");await close()
    await call("reminder_add",{"text":LONG,"at":h(-1)},300);await pg.wait_for_timeout(21000);await lay("reminder card");await close()
    await call("show_flights",FL);await lay("flight options");await pg.click("#actSecond");await pg.wait_for_timeout(500);await lay("all flights sheet")
    await pg.click("#sheet .cb-opts button:nth-child(4)");await pg.wait_for_timeout(600);await lay("transit ticket");await close()
    F2=dict(FL);F2["chosen"]=2;await call("show_flights",F2);await lay("chosen flight");await close()
    await call("show_flights",RT);await lay("round trip");await close()
    await call("show_flights",{"trip":"multi","to_city":"لندن","date":"15 – 28 نوفمبر","total":"13,410","legs":[{"from_city":"الرياض","to_city":"دبي","date":"الأحد 15","depart_time":"7:05 ص","stops":"مباشرة","price":"340"},{"from_city":"دبي","to_city":"لندن","date":"الثلاثاء 17","depart_time":"12:05 م","stops":"مباشرة","price":"1,420"},{"from_city":"لندن","to_city":"باريس","date":"الجمعة 20","depart_time":"9:00 ص","stops":"مباشرة","price":"600"},{"from_city":"باريس","to_city":"إسطنبول","date":"الإثنين 23","depart_time":"2:00 م","stops":"مباشرة","price":"900"},{"from_city":"إسطنبول","to_city":"الرياض","date":"السبت 28","depart_time":"9:10 م","stops":"مباشرة","price":"1,650"}]});await lay("multi-city");await close()
    await call("show_hotels",HT);await lay("hotel options");await pg.click("#act .cb-opts button:nth-child(1)");await pg.wait_for_timeout(600);await lay("hotel choice");await close()
    await call("show_trip",TR);await lay("whole trip");await close()
    await call("today_data",{"show":"weather"},1200);await lay("weather card");await close()
    await call("today_data",{"show":"prayer"},1200);await lay("prayer card");await close()
    await call("show_photo",{"query":"الربع الخالي","caption":"أكبر صحراء رملية متصلة في العالم"},1500);await lay("photo card");await close()
    await call("show_route",{"destination":"مطار الملك خالد الدولي"},2000);await lay("route card");await close()
    await call("show_card",{"title":"أي وقت يناسبك؟","subtitle":"المطعم يقترح","icon":"clock","choices":["8:30 م","9:30 م","10:00 م","يوم ثاني","الأسبوع الجاي"]});await lay("choice card");await close()
    await call("show_news",{"items":[{"title":"عنوان إخباري طويل جدًا عن تطورات اقتصادية مهمة في المنطقة خلال الربع الأخير من السنة","source":"الاقتصادية"}]*6});await lay("news card");await pg.click("#actSecond");await pg.wait_for_timeout(400);await lay("news sheet");await close()
    await call("device_action",{"name":"رنج روفر"});await lay("car card");await close()
    await call("doc_add",{});await lay("add document");await close()
    await pg.set_input_files("#docImg","tests/docs/bp.png");await pg.wait_for_timeout(2500);await lay("document card");await close()
    if pg.errs: F("HIGH",f"script errors @{vw}x{vh}",str(pg.errs[:3]))
    await b.close()
async def scenarios(p):
    print("== scenarios")
    # S1 first run, no key
    b,pg,call,lay,card,close=await boot(p,390,844,WSONLY,routes=False)
    st=await pg.evaluate("[document.querySelector('#card').classList.contains('open'),document.activeElement&&document.activeElement.id,__sent.length]");print(" S1 first run:",st)
    if not st[0]: F("HIGH","first run","settings do not open when there is no key")
    if st[2]: F("HIGH","first run","a session started without a key")
    if pg.errs: F("HIGH","first run",str(pg.errs[:2]))
    await b.close()
    # S2 everything else
    b,pg,call,lay,card,close=await boot(p,390,844,NOG)
    setup=json.loads(await pg.evaluate("__sent[0]"))["setup"];sysl=len(json.dumps(setup.get("systemInstruction",{}),ensure_ascii=False));tl=len(json.dumps(setup.get("tools",[]),ensure_ascii=False))
    print(" S2 session setup: tools",sum(len(t.get("functionDeclarations",[])) for t in setup["tools"]),"prompt chars",sysl,"tool text chars",tl,"model",setup.get("model"))
    # S3 call
    r=await call("show_action",{"type":"call","name":"محمد"});c=await card();print(" S3 call no number:",c[2],"|",r.get("note","")[:50])
    r=await call("show_action",{"type":"call","name":"محمد","number":"0500000000","reason":"تأجيل الاجتماع"});c=await card();print(" S3 call:",c[3],c[4])
    if not c[4].startswith("tel:"): F("HIGH","call card","does not open the dialer")
    await close();r=await call("contacts_find",{"name":"محمد"});print(" S3 number remembered:",json.dumps(r,ensure_ascii=False)[:120])
    r=await call("show_action",{"type":"whatsapp","name":"سارة","number":"0555555555","text":"بتأخر ربع ساعة & أشوفك؟ 100% #1"});c=await card();print(" S4 whatsapp link:",c[4])
    if "wa.me/0555" in c[4]: F("HIGH","whatsapp card","a local number (05…) is passed to WhatsApp without the country code, so WhatsApp will not find the person")
    await close()
    r=await call("show_action",{"type":"sms","name":"سارة","number":"0555555555","text":"بتأخر & أشوفك"});c=await card();print(" S4 sms link:",c[4]);await close()
    # S5 calendar edge cases
    r=await call("calendar_add",{"allow_prayer":True,"title":"اجتماع","start":"بكرة الساعة 5"});print(" S5 bad date:",json.dumps(r,ensure_ascii=False)[:110])
    if r.get("ok"): F("HIGH","calendar","accepts a date it cannot read")
    r=await call("calendar_add",{"allow_prayer":True,"title":"اجتماع قديم","start":h(-3000),"kind":"meeting"});print(" S5 past date:",json.dumps(r,ensure_ascii=False)[:130])
    if r.get("ok"): F("MED","calendar","records a meeting in the past with no warning to her or to him")
    r=await call("calendar_add",{"allow_prayer":True,"title":"اجتماع أمس","start":h(-1500),"kind":"meeting","allow_past":True});print(" S5 past on purpose:",r.get("ok"))
    await close();r=await call("calendar_add",{"allow_prayer":True,"title":"","start":h(100)});print(" S5 no title:",json.dumps(r,ensure_ascii=False)[:90])
    r=await call("calendar_add",{"allow_prayer":True,"title":"سهرة","start":now.strftime("%Y-%m-%d")+"T23:30","minutes":120,"kind":"appointment","allow_clash":True});await close()
    r=await call("calendar_list",{"days":1});print(" S5 midnight event listed today:",any(e["title"]=="سهرة" for e in r.get("events",[])))
    r=await call("calendar_update",{"event_id":"Lnope","start":h(50)});print(" S5 update missing:",json.dumps(r,ensure_ascii=False)[:80])
    r=await call("reminder_add",{"text":"x","at":"2026-13-40T99:99"});print(" S5 bad reminder:",json.dumps(r,ensure_ascii=False)[:90])
    if r.get("ok"): F("HIGH","reminder","accepts an impossible date")
    r=await call("reminder_add",{"text":"قديم جدًا","at":h(-2000)});print(" S5 old reminder:",json.dumps(r,ensure_ascii=False)[:120]);await close()
    if r.get("ok"): F("MED","reminder","saves a reminder whose time has passed")
    # S6 reminder flow: snooze
    r=await call("reminder_add",{"text":"اتصل بالمحاسب","at":h(-1)},300);await pg.wait_for_timeout(21000);c=await card();print(" S6 reminder card:",c[:4])
    if "تذكير" not in c[2]: F("HIGH","reminder","did not appear at its time")
    else:
        await pg.click("#actSecond");await pg.wait_for_timeout(400);x=[e for e in json.loads(await pg.evaluate("localStorage.getItem('musaed.cal')")) if e["title"]=="اتصل بالمحاسب"][0];print(" S6 snoozed by min:",round((x["s"]-now.timestamp()*1000)/60000),"fired",x.get("fired"))
    await close()
    # S7 travel edge cases
    r=await call("show_flights",{"trip":"oneway","from_code":"RUH","to_code":"JED","options":[]});print(" S7 no options:",json.dumps(r,ensure_ascii=False)[:120]);c=await card();print("   card:",c[:3]);await close()
    F3=dict(FL);F3["chosen"]=9;r=await call("show_flights",F3);print(" S7 chosen out of range:",json.dumps(r,ensure_ascii=False)[:110]);await close()
    if r.get("shown"): F("LOW","flights","a choice number outside the list is accepted")
    r=await call("show_flights",{"trip":"oneway","options":FL["options"]});print(" S7 no cities:",json.dumps(r,ensure_ascii=False)[:90]);await close()
    if r.get("shown"): F("LOW","flights","a card with no cities is shown")
    r=await call("show_hotels",{"options":[]});print(" S7 hotels none:",json.dumps(r,ensure_ascii=False)[:100]);await close()
    r=await call("show_flights",FL);link=(await card())[4];await pg.click("#act .cb-opts button:nth-child(2)");await pg.wait_for_timeout(600);c=await card();print(" S7 tap option 2:",c[1],"|",c[3],"|",c[4][:70])
    told=await pg.evaluate("__sent.filter(x=>x.indexOf('realtimeInput')>-1&&x.indexOf('text')>-1).slice(-1)[0]||''");tt=json.loads(told)["realtimeInput"]["text"] if told else "";print("   she is told:",tt[:90])
    if "رقم 2" not in tt: F("HIGH","flights","tapping an option does not tell her")
    await close();await call("show_hotels",HT);await pg.click("#act .cb-opts button:nth-child(3)");await pg.wait_for_timeout(600);tt=json.loads(await pg.evaluate("__sent.filter(x=>x.indexOf('realtimeInput')>-1&&x.indexOf('text')>-1).slice(-1)[0]"))["realtimeInput"]["text"];print("   hotel tap tells her:",tt[:80])
    if "رقم 3" not in tt: F("HIGH","hotels","tapping an option does not tell her")
    await close()
    # S8 stack and auto-dismiss
    for t in ["أحمد","بدر","جمال","داود","هاني"]: await call("show_action",{"type":"call","name":t,"number":"0500000000"},150)
    cnt=await pg.evaluate("document.querySelector('#actCount').textContent");print(" S8 stack badge:",cnt)
    await pg.evaluate("document.querySelector('#actClose').click()");await pg.wait_for_timeout(200);print("   after one close:",(await card())[:2]);await close()
    await call("show_card",{"title":"أي وقت؟","choices":["8","9"]},300);await call("show_card",{"title":"أي مطعم؟","choices":["أ","ب"]},300);await pg.evaluate("document.querySelector('#actClose').click()");await pg.wait_for_timeout(300);c=await card();print(" S8 first question still there after the second closes:",c[:2])
    if not c[0] or c[1]!="أي وقت؟": F("MED","question card","is lost when another card arrives")
    await close()
    await call("today_data",{"show":"weather"},1000);on1=(await card())[0];await pg.wait_for_timeout(24000);on2=(await card())[0];print(" S8 info card leaves by itself:",on1,"->",on2)
    if on2: F("MED","weather card","stays on screen after 24 s without her speaking")
    await close()
    # S9 device
    r=await call("device_action",{"name":"Range Rover"});print(" S9 car in English:",json.dumps(r,ensure_ascii=False)[:90]);await close()
    if r.get("error"): F("MED","car","English name not matched")
    r=await call("device_action",{"name":"شغلي الرنج"});c=await card();print(" S9 car short Arabic:",json.dumps(r,ensure_ascii=False)[:70],"|",c[:2],c[4][:60]);await close()
    if r.get("error"): F("MED","car","short Arabic name not matched")
    r=await call("device_action",{"name":"المكيف في الصالة"});print(" S9 unknown device:",json.dumps(r,ensure_ascii=False)[:110]);await close()
    # S10 money
    r=await call("portfolio_update",{"action":"buy","name":"الراجحي","symbol":"1120","shares":50,"price":94});print(" S10 buy:",json.dumps(r,ensure_ascii=False)[:120])
    r=await call("portfolio_update",{"action":"sell","name":"الراجحي","symbol":"1120","shares":80,"price":99});print(" S10 oversell:",json.dumps(r,ensure_ascii=False)[:140])
    if r.get("ok"): F("LOW","portfolio","oversell accepted")
    r=await call("expense_add",{"amount":-50,"category":"قهوة"});print(" S10 negative expense:",json.dumps(r,ensure_ascii=False)[:100])
    if r.get("ok") or r.get("saved"): F("MED","expenses","accepts a negative amount")
    r=await call("expense_add",{"amount":45.5,"category":"قهوة"});r=await call("expenses_summary",{});print(" S10 summary:",json.dumps(r,ensure_ascii=False)[:120]);await close()
    # S11 unknown tool + malformed args
    r=await call("no_such_tool",{});print(" S11 unknown tool:",json.dumps(r,ensure_ascii=False)[:90])
    r=await call("show_card",{"title":"<img src=x onerror=alert(1)>","text":"<b>bold</b>","rows":[{"label":"<i>a</i>","value":"<script>1</script>"}]});inj=await pg.evaluate("document.querySelectorAll('#act img[src=x],#act script').length");print(" S11 markup shown as text:",inj==0,"| title:",(await card())[1][:30]);await close()
    if inj: F("HIGH","cards","markup from an answer is treated as page code")
    r=await call("calendar_add",None);print(" S11 null args:",json.dumps(r,ensure_ascii=False)[:80])
    # S12 damaged saved data, one key at a time
    for k,v in [("musaed.cal","{oops"),("musaed.cal","[1,null]"),("musaed.docs","[1,null]"),("musaed.pf","null"),("musaed.pf","[null]"),("musaed.ct","{}"),("musaed.ct","[null]"),("musaed.dev","[null]"),("musaed.notes","[null]"),("musaed.exp","[null]"),("musaed.log","{x"),("musaed.loc","{x")]:
        e0=len(pg.errs);await pg.evaluate("(a)=>localStorage.setItem(a[0],a[1])",[k,v]);await pg.reload();await pg.wait_for_timeout(1600)
        alive=await pg.evaluate("typeof __ws!=='undefined'&&__sent.length>0")
        if alive:
            await call("calendar_list",{"days":2},100);await call("show_agenda",{},200);await call("doc_show",{},100);await call("show_portfolio",{},200);await call("contacts_find",{"name":"محمد"},100);await call("device_action",{"name":"x"},100);await call("notes_find",{"query":"x"},100);await call("expenses_summary",{},100)
            await pg.click("#pfBtn");await pg.wait_for_timeout(500);await pg.evaluate("document.querySelector('#card').classList.remove('open')");await pg.wait_for_timeout(9500)
        er=pg.errs[e0:];print(" S12",k,v,"-> starts:",alive,"errors:",er[:1])
        if not alive: F("HIGH","damaged saved data",f"{k}={v}: the app does not start")
        elif er: F("MED","damaged saved data",f"{k}={v}: "+er[0][:90])
        await pg.evaluate("(k)=>localStorage.removeItem(k)",k)
    await b.close()
    # S13 services down
    b,pg,call,lay,card,close=await boot(p,390,844,NOG,offline=True)
    r=await call("today_data",{"show":"weather"},1500);print(" S13 weather offline:",json.dumps(r,ensure_ascii=False)[:190])
    if "weather" not in r: F("LOW","weather","no reason given when the service is down");c=await card();print("   card:",c[:3]);await close()
    r=await call("show_photo",{"query":"الربع الخالي"},2500);c=await card();print(" S13 photo offline:",json.dumps(r,ensure_ascii=False)[:100],"| card:",c[:3]);await close()
    r=await call("show_route",{"destination":"المطار"},3000);c=await card();print(" S13 route offline:",json.dumps(r,ensure_ascii=False)[:100],"| card:",c[:4]);await close()
    if pg.errs: F("HIGH","services down",str(pg.errs[:3]))
    await b.close()
async def modeltest(p):
    print("== voice model")
    b,pg,call,lay,card,close=await boot(p,390,844,NOG)
    st=json.loads(await pg.evaluate("__sent[0]"))["setup"];fd=[t for t in st["tools"] if "functionDeclarations" in t][0]["functionDeclarations"]
    print(" new model first:",st["model"],"| blocking on all tools:",all(f.get("behavior")=="BLOCKING" for f in fd),len(fd))
    await b.close()
    BAD=NOG.replace("if(m.setup)setTimeout(function(){w.onmessage({data:JSON.stringify({setupComplete:{}})})},50)","if(m.setup){if(m.setup.model.indexOf('3.8')>-1)setTimeout(function(){w.onclose({code:1008,reason:'models/gemini-3.8-live is not found for API version v1beta'})},30);else setTimeout(function(){w.onmessage({data:JSON.stringify({setupComplete:{}})})},50)}")
    assert BAD!=NOG
    b,pg,call,lay,card,close=await boot(p,390,844,BAD)
    await pg.wait_for_timeout(1200)
    ms=await pg.evaluate("__sent.filter(x=>x.indexOf('\"setup\"')>-1).map(x=>{var s=JSON.parse(x).setup,f=(s.tools||[]).filter(t=>t.functionDeclarations)[0];return [s.model,(s.tools||[]).length,f?f.functionDeclarations.filter(d=>d.behavior).length:0]})")
    print(" when the new model is refused:",ms,"| saved:",await pg.evaluate("localStorage.getItem('musaed.lm')"))
    if not ms or "3.1" not in ms[-1][0] or ms[-1][2]!=0: F("HIGH","voice model","does not fall back to the previous model")
    r=await call("show_card",{"title":"اختبار","text":"يعمل"});print(" works after fallback:",r.get("shown"))
    await pg.reload();await pg.wait_for_timeout(1400);print(" next session starts on:",json.loads(await pg.evaluate("__sent[0]"))["setup"]["model"])
    await pg.click("#setBtn");await pg.wait_for_timeout(500);print(" switch label:",await pg.evaluate("document.querySelector('#lmBtn').textContent"),"|",(await pg.evaluate("document.querySelector('#diag').textContent")).split("\n")[1])
    if pg.errs: F("HIGH","voice model",str(pg.errs[:2]))
    await b.close()
async def main():
    async with async_playwright() as p:
        if "s" in sys.argv[1]: await scenarios(p)
        if "m" in sys.argv[1]: await modeltest(p)
        if "l" in sys.argv[1]:
            for vw,vh in [(390,844),(320,568)]: await sweep(p,vw,vh)
    print("\nFINDINGS",len(FIND))
    for f in sorted(set(FIND)): print(" ",f)
asyncio.run(main())
