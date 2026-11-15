import asyncio, sys, time, datetime
src=open("tests/audit2.py").read().replace("asyncio.run(main2())","")
exec(src)
FIND.clear()
LOG=[]
RC={"is_receipt":True,"merchant":"مطعم البيك","amount":86.5,"currency":"SAR","date":"2026-11-14","category":"مطاعم","items":["وجبة دجاج","بطاطس"]}
BL={"is_bill":True,"name":"الكهرباء","amount":450,"currency":"SAR","due_date":(datetime.date.today()+datetime.timedelta(days=9)).isoformat(),"every":"month"}
PR={"found":True,"product":"سماعات سوني WH-1000XM6","brand":"Sony","model":"WH-1000XM6","size":"","search_query":"سعر Sony WH-1000XM6 السعودية"}
async def gem(route):
    rq=route.request
    if rq.method=="GET": return await route.fulfill(json={"models":[{"name":"models/"+n,"supportedGenerationMethods":["generateContent"]} for n in ["gemini-3.8-flash","gemini-3.5-flash-lite"]]})
    b=json.loads(rq.post_data);sysx=b.get("systemInstruction",{}).get("parts",[{}])[0].get("text","");parts=b["contents"][0]["parts"];img=sum(1 for p in parts if "inlineData" in p)
    kind="receipt" if "shop receipt" in sysx else "bill" if "subscription bill" in sysx else "product" if "identify a product" in sysx else "read" if "look at a picture" in sysx else "search" if b.get("tools") else "summary"
    LOG.append((kind,img,parts[0].get("text","")[:40]))
    out={"receipt":json.dumps(RC,ensure_ascii=False),"bill":json.dumps(BL,ensure_ascii=False),"product":json.dumps(PR,ensure_ascii=False),"read":"قائمة طعام بالإيطالية.\nMargherita: بيتزا بالطماطم والجبن، 45 ريال.\nتحذير: قد تحتوي على مكسرات.","summary":"ملخص"}.get(kind,"نتيجة")
    j={"candidates":[{"content":{"parts":[{"text":out}]}}]}
    if kind=="search": j["candidates"][0]["groundingMetadata"]={"webSearchQueries":["x"],"groundingChunks":[{"web":{"uri":"https://example.org/a","title":"example.org"}}]}
    await route.fulfill(json=j)
up=lambda pg: pg.set_input_files("#docImg","tests/docs/bp.png")
async def run(p,vw,vh,full):
    b,pg,call,lay,card,close=await boot(p,vw,vh,wsvar(NOG,WS_COUNT))
    await pg.context.grant_permissions(["microphone","geolocation"]);await pg.context.set_geolocation({"latitude":24.7136,"longitude":46.6753})
    await pg.route(re.compile(r"generativelanguage\.googleapis\.com/v1beta/models"),gem)
    await pg.route("**/api.aladhan.com/**",lambda r:r.fulfill(json={"code":200,"data":{"timings":{"Fajr":"04:48","Dhuhr":"11:38","Asr":"14:45","Maghrib":"17:07","Isha":"18:37"}}}))
    await pg.add_init_script("window.__opened=[];window.open=function(u){__opened.push(u);return null}");await pg.evaluate("window.__opened=[];window.open=function(u){__opened.push(u);return null}")
    setup=json.loads(await pg.evaluate("__sent[0]"))["setup"];print(f"@{vw}: tools",len(setup["tools"][0]["functionDeclarations"]),"| prompt chars",len(json.dumps(setup["systemInstruction"],ensure_ascii=False)))
    body=lambda: pg.evaluate("document.querySelector('#act').innerText.replace(/\\n+/g,' | ').slice(0,230)")
    last=lambda: texts(pg)
    # look: read
    r=await call("camera_look",{"kind":"read","question":"ترجمي لي هذي القائمة"});await lay("look card");await pg.screenshot(path=f"tests/out/p1_look_{vw}.png");await pg.evaluate("document.querySelector('#docImg').value=''");await up(pg);await pg.wait_for_timeout(1800)
    print(" read:",await body());await lay("read result");tx=await last();print("   told:",tx[-1][:90].replace("\n"," "));await close()
    # budget + receipt
    r=await call("budget",{"action":"set","category":"مطاعم","amount":100});r=await call("budget",{"action":"set","amount":3000});await lay("budget card");await close()
    r=await call("camera_look",{"kind":"receipt"});await pg.evaluate("document.querySelector('#docImg').value=''");await up(pg);await pg.wait_for_timeout(1800);print(" receipt:",await body());await lay("receipt card");await pg.screenshot(path=f"tests/out/p1_rc_{vw}.png")
    await pg.click("#actGo");await pg.wait_for_timeout(500);ex=json.loads(await pg.evaluate("localStorage.getItem('musaed.exp')"));tx=await last();print("   saved:",[(e["a"],e["c"],e["x"],datetime.date.fromtimestamp(e["d"]/1000).isoformat()) for e in ex],"| told:",tx[-1][:120])
    if not ex or ex[-1]["a"]!=86.5 or ex[-1]["c"]!="مطاعم": F("HIGH","receipt","expense not saved correctly")
    await close();r=await call("expense_add",{"amount":40,"category":"المطاعم","note":"قهوة"});print(" by voice, budget alert:",r.get("budget_alert"))
    if not r.get("budget_alert") or not r["budget_alert"][0]["over"]: F("HIGH","budget","no alert over the limit");r=await call("budget",{"action":"status"});print(" budget:",await body());await close()
    if full:
        r=await call("budget",{"action":"set","category":"المطاعم","amount":0});print(" removed:",[x["name"] for x in r["state"]["budgets"]]);await close()
        # bills
        dd=(datetime.date.today()+datetime.timedelta(days=3)).day;r=await call("bills",{"action":"add","name":"STC","amount":230,"due_day":dd});print(" bill add:",r);await lay("bills card");await close()
        cal=[e for e in json.loads(await pg.evaluate("localStorage.getItem('musaed.cal')||'[]'")) if e.get("bill")];print("   reminder planned:",[(e["title"][:44],datetime.datetime.fromtimestamp(e["s"]/1000).strftime("%m-%d %H:%M")) for e in cal])
        r=await call("bills",{"action":"add","name":"نتفلكس","amount":56,"due_day":40});print(" bad day:",r.get("error","")[:50]);r=await call("bills",{"action":"add","name":"تأمين السيارة","amount":2400,"due_date":"2027-03-10","every":"year"});print(" yearly:",r["bill"]["next_due"],r["bill"]["status"]);await close()
        r=await call("bills",{"action":"paid","name":"stc"});print(" paid -> next:",r["bill"]["next_due"],"| reminders now:",len([e for e in json.loads(await pg.evaluate("localStorage.getItem('musaed.cal')")) if e.get("bill")]));await close()
        r=await call("camera_look",{"kind":"bill"});await pg.evaluate("document.querySelector('#docImg').value=''");await up(pg);await pg.wait_for_timeout(1800);print(" bill photo:",await body());await pg.click("#actGo");await pg.wait_for_timeout(500);print("   bills:",[(x["name"],x.get("amount")) for x in json.loads(await pg.evaluate("localStorage.getItem('musaed.bills')"))]);await close()
        r=await call("bills",{"action":"delete","name":"نتفلكس"});print(" delete missing:",r.get("error"));r=await call("bills",{"action":"delete","name":"STC"});await pg.click("#actGo");await pg.wait_for_timeout(400);print(" deleted by tap:",[x["name"] for x in json.loads(await pg.evaluate("localStorage.getItem('musaed.bills')"))],"| its reminders left:",len([e for e in json.loads(await pg.evaluate("localStorage.getItem('musaed.cal')")) if e.get("bill") and "STC" in e["title"]]));await close()
        # product
        r=await call("camera_look",{"kind":"product"});await pg.evaluate("document.querySelector('#docImg').value=''");await up(pg);await pg.wait_for_timeout(1800);tx=await last();print(" product:",(await card())[1:3],"| told:",tx[-1][:70],"…web_search" if "web_search" in tx[-1] else "NO SEARCH INSTRUCTION");await close()
    # places
    r=await call("show_places",{"title":"صيدليات فاتحة الآن","places":[{"name":"صيدلية النهدي","area":"العليا","distance":"400 م","hours":"24 ساعة","rating":"4.5"},{"name":"صيدلية الدواء فرع طريق الملك فهد الرئيسي","area":"الورود","distance":"1.2 كم","hours":"حتى 12 ص"}]});await lay("places card")
    await pg.click("#act .cb-opts button:nth-child(1)");await pg.wait_for_timeout(200);print(" places tap opens:",(await pg.evaluate("__opened"))[-1][:90]);await close()
    # parking
    r=await call("parking",{"action":"save","note":"الدور B2 عمود 14"},1500);print(" park save:",r);await lay("parking card");await pg.screenshot(path=f"tests/out/p1_park_{vw}.png");await close()
    await pg.context.set_geolocation({"latitude":24.7160,"longitude":46.6790});r=await call("parking",{"action":"show"},600);print(" park show:",r.get("distance_m"),"m |",await body(),"| link:",(await card())[4][:80]);await lay("parking show");await close()
    if full:
        r=await call("parking",{"action":"clear"});r=await call("parking",{"action":"show"});print(" after clear:",r.get("found"))
        await pg.context.clear_permissions();await pg.context.grant_permissions(["microphone"]);r=await call("parking",{"action":"save"},400);print(" no location, no note:",r.get("saved"),r.get("error","")[:40]);r=await call("parking",{"action":"save","note":"مواقف البوابة 3"},400);print(" no location, with note:",r.get("saved"),r.get("position_saved"),"|",(await card())[2]);await close()
        await pg.context.grant_permissions(["microphone","geolocation"])
    # routines
    r=await call("routine",{"action":"save","name":"طالع من البيت","steps":["الطريق للدوام","ملخص اليوم","شغّلي الرنج والمكيف"]});await lay("routine card");await close()
    r=await call("routine",{"action":"run","name":"طالع من البيت"});print(" routine run:",r.get("steps"),"|",(await card())[1:3]);await lay("routine run");await close()
    if full:
        r=await call("routine",{"action":"run","name":"روتين النوم"});print(" unknown routine:",r.get("found"),r.get("routines"))
        await pg.evaluate("__ws.onclose({code:1006,reason:''})");await pg.wait_for_timeout(900);sy=await pg.evaluate("(function(){var a=__sent.filter(function(x){return x.indexOf('systemInstruction')>-1});return JSON.parse(a[a.length-1]).setup.systemInstruction.parts[0].text})()");print(" she knows the routine name after reconnect:","طالع من البيت" in sy,"| budget names:", "تصنيفات ميزانيته" in sy or "الإجمالي" in sy)
        r=await call("routine",{"action":"delete","name":"طالع من البيت"});await pg.click("#actGo");await pg.wait_for_timeout(400);print(" routine deleted:",json.loads(await pg.evaluate("localStorage.getItem('musaed.rt')")));await close()
    # prayer clash
    tm=(datetime.date.today()+datetime.timedelta(days=1)).isoformat()
    r=await call("calendar_add",{"title":"اجتماع الشركاء","start":tm+"T17:00","minutes":60,"kind":"meeting"},500);print(" prayer clash:",r.get("prayer_clash"),"|",await body());await lay("prayer card");await pg.screenshot(path=f"tests/out/p1_pray_{vw}.png")
    await pg.click("#actGo");await pg.wait_for_timeout(500);ev=[e for e in json.loads(await pg.evaluate("localStorage.getItem('musaed.cal')")) if e["title"]=="اجتماع الشركاء"];print("   moved to:",[datetime.datetime.fromtimestamp(e["s"]/1000).strftime("%H:%M") for e in ev]);await close()
    if not ev or datetime.datetime.fromtimestamp(ev[0]["s"]/1000).strftime("%H:%M")!="17:40": F("HIGH","prayer","suggested time wrong")
    if full:
        r=await call("calendar_add",{"title":"عشاء عمل","start":(datetime.date.today()+datetime.timedelta(days=2)).isoformat()+"T18:30","minutes":60,"kind":"meeting","allow_prayer":True},400);print(" keep own time:",{k:v for k,v in r.items() if k in("ok","saved","prayer_clash","error","conflict")});await close()
        r=await call("calendar_add",{"title":"اجتماع الصباح","start":tm+"T09:00","minutes":60,"kind":"meeting"},400);print(" no prayer then:",bool(r.get("ok")),r.get("prayer_clash"));await close()
        r=await call("reminder_add",{"text":"خذ الدواء","at":tm+"T17:05"},300);print(" reminders are not checked:",bool(r.get("ok")));await close()
    # hijri and occasions
    r=await call("show_occasions",{},400);print(" occasions:",r["today_hijri"],"|",[(x["name"],x["date"]) for x in r["occasions"]][:4]);await lay("occasions card");await close()
    r=await call("today_data",{"show":"none"},800);print(" today_data hijri:",r.get("hijri_date"),"| coming:",r.get("coming_occasions"));await close()
    await call("show_brief",{},1200);print(" Today page date line:",await pg.evaluate("document.querySelector('#bDate').textContent"));await pg.evaluate("document.querySelector('#briefClose').click()")
    print(" calls to Google:",[x[:2] for x in LOG][:8]);print(" errors",pg.errs);LOG.clear();await b.close()
async def go():
    async with async_playwright() as p:
        await run(p,390,844,True);await run(p,320,568,False)
    print("FINDINGS",len(FIND))
    for f in sorted(set(FIND)): print(" ",f)
asyncio.run(go())
