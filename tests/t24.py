import asyncio, json, subprocess, time
from playwright.async_api import async_playwright
FIND=[]
def F(sev,area,msg): FIND.append((sev,area,msg)); print("  !!",sev,area,"-",msg)
srv=subprocess.Popen(["python3","-m","http.server","8769","--bind","127.0.0.1"],cwd="/home/claude/jarves",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
URL="http://127.0.0.1:8769/index.html"
NOW=int(time.time()*1000)
SMS=[
 {"id":1,"from":"AlRajhiBank","name":"","text":"شراء عبر نقاط البيع\nبطاقة: مدى *4321\nمبلغ: SAR 45.50\nلدى: STARBUCKS RIYADH\nفي: 16/11/26 09:14","t":NOW-3600e3},
 {"id":2,"from":"SNB-AlAhli","name":"","text":"Purchase\nCard: *8877\nAmount: SAR 1,250.00\nAt: EXTRA STORES\nDate: 2026-11-15 18:20","t":NOW-26*3600e3},
 {"id":3,"from":"STCBank","name":"","text":"شراء انترنت\nبطاقة ائتمانية: ****5566\nمن: AMAZON\nمبلغ: USD 20.00","t":NOW-30*3600e3},
 {"id":4,"from":"AlRajhiBank","name":"","text":"رمز التحقق: 482913 لا تشاركه مع أحد. عملية شراء SAR 30","t":NOW-31*3600e3},
 {"id":5,"from":"AlRajhiBank","name":"","text":"إيداع راتب SAR 15,000.00 في حسابك","t":NOW-40*3600e3},
 {"id":6,"from":"BankAlbilad","name":"","text":"Apple Pay شراء\nبـ 23.00 ر.س\nمن: KUDU","t":NOW-50*3600e3},
 {"id":7,"from":"AlinmaBank","name":"","text":"سداد فاتورة STC بمبلغ 230.00 ريال","t":NOW-60*3600e3},
 {"id":8,"from":"Riyad Bank","name":"","text":"شراء مدى ٧٥٫٥٠ ريال لدى العثيم","t":NOW-70*3600e3},
 {"id":9,"from":"+966501112233","name":"أحمد","text":"وصلت؟ أنا عند الباب","t":NOW-600e3}]
MOCK="""
window.__nat={calls:[],ln:[],lnCancel:[],sms:%s,listeners:{},perms:{mic:'granted',loc:'granted',camera:'prompt',notify:'granted',sms:'granted',calls:'granted',contacts:'granted',dial:'prompt',listener:'off',battery:'off',exact:'granted',assistant:'off'},prefs:{missed:true,bank:true,notes:true}};
(function(){var N=window.__nat;function rec(m,a){N.calls.push([m,a||{}])}
 var P={info:function(a){rec('info',a);return Promise.resolve({version:'1.0.7',build:7,sdk:34,model:'samsung SM-S928B',perms:N.perms,prefs:N.prefs})},
  state:function(a){rec('state',a);return Promise.resolve(N.perms)},
  ask:function(a){rec('ask',a);if(a.name==='listener'||a.name==='app')return Promise.resolve({state:'settings'});N.perms[a.name]='granted';return Promise.resolve({state:'granted'})},
  setPrefs:function(a){rec('setPrefs',a);Object.assign(N.prefs,a);return Promise.resolve()},
  sms:function(a){rec('sms',a);var q=(a.query||'').toLowerCase();var l=N.sms.filter(function(s){return s.t>(a.since||0)&&(!q||(s.from+' '+s.name+' '+s.text).toLowerCase().indexOf(q)>-1)}).slice(0,a.limit||40);return Promise.resolve({items:l})},
  calls:function(a){rec('calls',a);var l=[{number:'+966501112233',name:'أحمد',type:'missed',t:Date.now()-1200e3,secs:0},{number:'0551234567',name:'أبوي',type:'outgoing',t:Date.now()-86400e3*2,secs:340}];
    if(a.query)l=l.filter(function(c){return c.name.indexOf(a.query)>-1||(a.query.replace(/\\D/g,'').length>=6&&c.number.indexOf(a.query.replace(/\\D/g,'').slice(-9))>-1)});if(a.type&&a.type!=='all')l=l.filter(function(c){return c.type===a.type});return Promise.resolve({items:l.slice(0,a.limit||20)})},
  contacts:function(a){rec('contacts',a);return Promise.resolve({items:a.query.indexOf('خالد')>-1?[{name:'خالد العتيبي',phones:['+966555000111']}]:[]})},
  dial:function(a){rec('dial',a);return Promise.resolve({mode:a.direct?'calling':'dialer'})},
  notes:function(a){rec('notes',a);if(N.perms.listener!=='granted'){var e=new Error('off');e.code='no_permission';return Promise.reject(e)}return Promise.resolve({items:[{app:'WhatsApp',title:'سارة',text:'رمز الدخول 123456',t:Date.now()-300e3}]})},
  addListener:function(ev,fn){(N.listeners[ev]=N.listeners[ev]||[]).push(fn);return Promise.resolve({remove:function(){}})}};
 var lp=function(){try{return JSON.parse(localStorage.getItem('__lnp')||'[]')}catch(e){return []}},ls=function(a){localStorage.setItem('__lnp',JSON.stringify(a))};
 var LN={schedule:function(a){N.ln.push(a);ls(lp().concat(a.notifications.map(function(n){return {id:n.id,extra:n.extra,title:n.title}})));return Promise.resolve()},getPending:function(){return Promise.resolve({notifications:lp()})},cancel:function(a){N.lnCancel.push(a);var ids=a.notifications.map(function(n){return n.id});ls(lp().filter(function(n){return ids.indexOf(n.id)<0}));return Promise.resolve()}};
 window.Capacitor={isNativePlatform:function(){return true},Plugins:{Musaed:P,LocalNotifications:LN}};
 window.__fire=function(ev,d){(N.listeners[ev]||[]).forEach(function(f){f(d)})};})();
""" % json.dumps(SMS,ensure_ascii=False)
async def signup(pg,name,email,pw):
    if await pg.evaluate("document.querySelector('#authSeg').hidden===false"): await pg.click("#authTabUp")
    await pg.fill("#auName",name);await pg.fill("#auEmail",email);await pg.fill("#auPass",pw);await pg.fill("#auPass2",pw);await pg.click("#authGo")
    for _ in range(40):
        await pg.wait_for_timeout(200)
        code=await pg.evaluate("(()=>{var d=[...document.querySelectorAll('[role=dialog] div')].find(x=>/^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$/.test(x.textContent));return d?d.textContent:''})()")
        if code: break
    if code:
        await pg.evaluate("document.querySelector('[role=dialog] input[type=checkbox]').click()");await pg.evaluate("[...document.querySelectorAll('[role=dialog] button')].find(b=>b.textContent==='تم').click()")
    await pg.wait_for_timeout(1500)
def tool(name,args): return "__nt.tool(%s,%s)"%(json.dumps(name),json.dumps(args,ensure_ascii=False))
async def go():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox","--use-fake-device-for-media-stream","--use-fake-ui-for-media-stream"])
        # ---------- native ----------
        c=await b.new_context(viewport={"width":390,"height":844});await c.add_init_script(MOCK);pg=await c.new_page();errs=[];pg.on("pageerror",lambda e:errs.append(str(e)[:200]))
        for u in ["**/*googleapis.com/**","**/api.open-meteo.com/**","**/api.aladhan.com/**","**/api.bigdatacloud.net/**"]: await c.route(u,lambda r:r.fulfill(json={}))
        await pg.goto(URL);await pg.evaluate("localStorage.clear()");await pg.reload();await pg.wait_for_timeout(800)
        await signup(pg,"عمر","omar@test.com","pass-omar-1")
        print(" native detected:",await pg.evaluate("__nt.on()"),"| body.native:",await pg.evaluate("document.body.classList.contains('native')"))
        su=await pg.evaluate("(()=>{var s=__nt.setup();return {names:s.tools[s.tools.length-1].functionDeclarations?s.tools[s.tools.length-1].functionDeclarations.map(f=>f.name):s.tools.map(t=>Object.keys(t)),txt:s.systemInstruction.parts[0].text.indexOf('## جوال أندرويد')>-1||s.systemInstruction.parts[0].text.indexOf('## Android phone')>-1}})()")
        nn=[n for n in ["phone_messages","bank_expenses","call_history","phone_notifications","phone_call","phone_call_confirm","open_permission"] if n in su["names"]]
        print(" model gets the phone tools:",len(nn),"of 7 | phone rules in prompt:",su["txt"],"| total tools:",len(su["names"]))
        if len(nn)<7 or not su["txt"]: F("HIGH","tools","phone tools missing from the session")
        # settings
        await pg.evaluate("__t.openCard('set')");await pg.wait_for_timeout(900)
        rows=await pg.evaluate("[...document.querySelectorAll('#permG button')].map(b=>b.innerText.replace(/\\n/g,' : '))")
        print(" permissions rows:",len(rows));[print("   ",r) for r in rows]
        if len(rows)!=13: F("HIGH","settings","native permission list wrong size")
        await pg.evaluate("[...document.querySelectorAll('#permG button')].find(b=>b.innerText.indexOf('الكاميرا')>-1).click()");await pg.wait_for_timeout(1200)
        cam=await pg.evaluate("[...document.querySelectorAll('#permG button')].find(b=>b.innerText.indexOf('الكاميرا')>-1).innerText")
        print(" tap camera -> asks Android, row now:",cam.replace("\n"," : "))
        if "مسموح" not in cam: F("MED","settings","row did not refresh after permission")
        al=await pg.evaluate("[...document.querySelectorAll('#natG button')].map(b=>b.innerText.replace(/\\n/g,' : '))");print(" alert switches:");[print("   ",r) for r in al]
        if len(al)!=5: F("HIGH","settings","alert switches missing")
        await pg.evaluate("[...document.querySelectorAll('#natG button')][0].click()");await pg.wait_for_timeout(400)
        print(" missed-call switch -> native prefs:",await pg.evaluate("__nat.prefs.missed"),"| row:",await pg.evaluate("[...document.querySelectorAll('#natG button')][0].innerText.replace(/\\n/g,' : ')"))
        if await pg.evaluate("__nat.prefs.missed")!=False: F("HIGH","settings","missed-call switch not saved")
        dg=await pg.text_content("#diag");print(" status line:", [l for l in dg.split("\n") if "أندرويد" in l])
        if "أندرويد" not in dg: F("LOW","status","no Android version in status")
        await pg.evaluate("__t.closeCard()")
        # messages
        r=await pg.evaluate(tool("phone_messages",{"days":2}));print(" phone_messages:",r["count"],"msgs | OTP hidden:", all("482913" not in m["text"] for m in r["messages"]))
        if any("482913" in m["text"] for m in r["messages"]): F("HIGH","privacy","verification code read out")
        r=await pg.evaluate(tool("phone_messages",{"query":"أحمد"}));print(" messages from أحمد:",[m["text"] for m in r["messages"]])
        # bank import preview & import
        r=await pg.evaluate(tool("bank_expenses",{"action":"preview","days":30}));print(" preview:",[(x["amount"],x["category"],x["where"]) for x in r["purchases"]],"| foreign:",r["foreign_currency"])
        exp={45.5:"مطاعم",1250:"تسوق",23:"مطاعم",230:"فواتير",75.5:"بقالة"}
        got={x["amount"]:x["category"] for x in r["purchases"]}
        if got!=exp: F("HIGH","bank","parsing wrong: "+json.dumps(got,ensure_ascii=False))
        if not r["foreign_currency"] or r["foreign_currency"][0]["amount"]!=20: F("MED","bank","foreign purchase not flagged")
        n0=await pg.evaluate("JSON.parse(localStorage.getItem('musaed.exp')||'[]').length")
        r=await pg.evaluate(tool("bank_expenses",{"action":"import"}));n1=await pg.evaluate("JSON.parse(localStorage.getItem('musaed.exp')||'[]').length")
        print(" import saved:",r["saved"],"total",r["total"],"| expenses before/after:",n0,n1,"| toast:",await pg.text_content("#toastT"))
        r2=await pg.evaluate(tool("bank_expenses",{"action":"import"}));print(" second import adds:",r2["saved"],"(must be 0)")
        if r["saved"]!=5 or r2["saved"]!=0 or n1-n0!=5: F("HIGH","bank","import or de-dup wrong")
        # new bank SMS arrives -> auto import
        await pg.evaluate("__nat.sms.unshift({id:20,from:'AlRajhiBank',name:'',text:'شراء عبر نقاط البيع مبلغ SAR 18.00 لدى HALF MILLION',t:Date.now()-5000});__fire('sms',{from:'AlRajhiBank',text:'x',t:Date.now()-5000,spend:true})")
        await pg.wait_for_timeout(2300);n2=await pg.evaluate("JSON.parse(localStorage.getItem('musaed.exp')||'[]').length")
        print(" new bank SMS logged by itself:",n2-n1==1,"| toast:",await pg.text_content("#toastT"))
        if n2-n1!=1: F("HIGH","bank","auto-log of new SMS failed")
        # calls
        r=await pg.evaluate(tool("call_history",{"type":"missed"}));print(" missed calls:",r["calls"])
        r=await pg.evaluate(tool("call_history",{"name":"أبوي","limit":1}));print(" last call with أبوي:",r["calls"])
        if not r["calls"] or r["calls"][0]["name"]!="أبوي": F("MED","calls","last-contact lookup failed")
        # notifications (permission off -> clear message, then on)
        r=await pg.evaluate(tool("phone_notifications",{}));print(" notifications with access off:",r.get("error"),"|",r.get("tell_user","")[:90])
        await pg.evaluate("__nat.perms.listener='granted'");r=await pg.evaluate(tool("phone_notifications",{"app":"WhatsApp"}));print(" notifications:",r["notifications"])
        if "123456" in json.dumps(r,ensure_ascii=False): F("HIGH","privacy","code in notification read out")
        # contacts
        r=await pg.evaluate(tool("contacts_find",{"name":"خالد"}));print(" contacts_find from phone:",r)
        if r.get("source")!="his phone contacts": F("HIGH","contacts","phone contacts not used")
        # call flow
        r=await pg.evaluate(tool("phone_call",{"name":"خالد","number":"+966555000111"}));await pg.wait_for_timeout(500)
        card=await pg.evaluate("document.querySelector('#act').classList.contains('on')");print(" phone_call -> card on screen:",card,"| ask:",r.get("ask_user","")[:40])
        d0=len([x for x in await pg.evaluate("__nat.calls") if x[0]=="dial"])
        if d0: F("HIGH","calls","dialed before he said yes")
        r=await pg.evaluate(tool("phone_call_confirm",{}));dl=[x for x in await pg.evaluate("__nat.calls") if x[0]=="dial"];print(" after yes -> dial:",dl[-1] if dl else None,"|",r)
        if not dl or not dl[-1][1].get("direct"): F("HIGH","calls","confirm did not place the call")
        r=await pg.evaluate(tool("phone_call_confirm",{}));print(" confirm again (nothing waiting):",r.get("error"))
        # tapping the call button on a card calls directly
        await pg.evaluate("__nt.act({type:'call',name:'أبوي',number:'0551234567'})");await pg.wait_for_timeout(500);await pg.click("#actGo");await pg.wait_for_timeout(400)
        dl=[x for x in await pg.evaluate("__nat.calls") if x[0]=="dial"];print(" tap call button -> dial:",dl[-1][1])
        if dl[-1][1].get("number")!="0551234567": F("HIGH","calls","card button did not call")
        # incoming call while app open
        await pg.evaluate("__fire('call',{state:'ringing',number:'+966501112233',name:'أحمد'})");await pg.wait_for_timeout(300);print(" ringing toast:",await pg.text_content("#toastT"))
        await pg.evaluate("__fire('call',{state:'idle',number:'+966501112233',name:'أحمد'})");await pg.wait_for_timeout(600)
        mc=await pg.evaluate("(()=>{var a=document.querySelector('#act');return a.classList.contains('on')?a.innerText.replace(/\\n+/g,' | '):''})()");print(" missed-call card:",mc[:120])
        if "مكالمة فائتة" not in mc: F("MED","calls","no missed-call card in the app")
        # reminders -> native alarms
        await pg.evaluate("__nat.ln=[]");r=await pg.evaluate(tool("reminder_add",{"text":"أتصل على البنك","at":time.strftime("%Y-%m-%dT%H:%M",time.localtime(time.time()+7200))}))
        await pg.wait_for_timeout(1500);ln=await pg.evaluate("__nat.ln");sch=[n for x in ln for n in x["notifications"]]
        print(" reminder saved:",r.get("ok"),"| alarms scheduled:",[(n["title"],str(n["schedule"]["at"])[:16]) for n in sch])
        if not any("أتصل على البنك" in n["title"] for n in sch): F("HIGH","alerts","reminder not scheduled on the phone")
        # sign out -> alarms cancelled, not rescheduled for nobody
        await pg.evaluate("__nat.ln=[];__nat.lnCancel=[]");await pg.evaluate("document.querySelector('#acOut').click()");await pg.wait_for_timeout(3000)
        left=await pg.evaluate("JSON.parse(localStorage.getItem('__lnp')||'[]')");print(" after sign-out: alarms still pending on the phone:",left)
        if left: F("HIGH","separation","reminders of a signed-out account still ring")
        print(" page errors:",errs)
        if errs: F("HIGH","errors","page errors in native mode")
        await c.close()
        # ---------- browser (not the Android app) ----------
        c=await b.new_context(viewport={"width":390,"height":844});pg=await c.new_page();errs=[];pg.on("pageerror",lambda e:errs.append(str(e)[:200]))
        for u in ["**/*googleapis.com/**","**/api.open-meteo.com/**","**/api.aladhan.com/**","**/api.bigdatacloud.net/**"]: await c.route(u,lambda r:r.fulfill(json={}))
        await pg.goto(URL);await pg.evaluate("localStorage.clear()");await pg.reload();await pg.wait_for_timeout(800);await signup(pg,"عمر","omar@test.com","pass-omar-1")
        su=await pg.evaluate("(()=>{var s=__nt.setup(),t=s.tools.filter(t=>t.functionDeclarations)[0];return {n:t.functionDeclarations.length,ph:t.functionDeclarations.some(f=>f.name==='phone_messages'),txt:s.systemInstruction.parts[0].text.indexOf('## جوال أندرويد')>-1||s.systemInstruction.parts[0].text.indexOf('## Android phone')>-1}})()")
        await pg.evaluate("__t.openCard('set')");await pg.wait_for_timeout(700);rows=await pg.evaluate("document.querySelectorAll('#permG button').length");hid=await pg.evaluate("document.querySelector('#natG').hidden")
        print(" browser: phone tools offered:",su["ph"],"| prompt section:",su["txt"],"| tools:",su["n"],"| permission rows:",rows,"| alert group hidden:",hid,"| errors:",errs)
        if su["ph"] or su["txt"] or rows!=3 or not hid or errs: F("HIGH","web","browser version changed")
        await b.close()
    srv.terminate()
    print("\nFINDINGS:",len(FIND));[print(" ",f) for f in FIND]
asyncio.run(go())
