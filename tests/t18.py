import asyncio, sys, time
src=open("tests/audit2.py").read().replace("asyncio.run(main2())","")
exec(src)
FIND.clear()
LOG=[];MODE={"s":"ok"};ACT={"n":0,"max":0}
async def gem(route):
    rq=route.request;u=rq.url
    if rq.method=="GET": return await route.fulfill(json={"models":[{"name":"models/"+n,"supportedGenerationMethods":["generateContent"]} for n in ["gemini-3.8-flash","gemini-3.6-flash","gemini-3.5-flash-lite","gemini-2.5-flash"]]})
    b=json.loads(rq.post_data);m=re.search(r"models/([^:]+):",u).group(1);tool=list(b["tools"][0].keys())[0] if b.get("tools") else "none";q=b["contents"][0]["parts"][0]["text"]
    LOG.append((m,tool,q[:40].replace("\n"," ")))
    if tool=="none": return await route.fulfill(json={"candidates":[{"content":{"parts":[{"text":"يخطط لرحلة جدة يوم الأحد 15 نوفمبر، واختار رحلة السعودية 7:05 ص بسعر 340 ريال.\nباقي: حجز فندق قريب من الكورنيش بحد 600 ريال لليلة."}]}}]})
    if tool=="google_search":
        ACT["n"]+=1;ACT["max"]=max(ACT["max"],ACT["n"]);await asyncio.sleep(0.5);ACT["n"]-=1
        if MODE["s"]=="lite429" and "lite" in m: return await route.fulfill(status=429,json={"error":{"code":429,"message":"Quota exceeded for metric: generate_content_free_tier_requests, limit: 5","details":[{"@type":"type.googleapis.com/google.rpc.QuotaFailure","violations":[{"quotaId":"GenerateRequestsPerMinutePerProjectPerModel-FreeTier"}]},{"@type":"type.googleapis.com/google.rpc.RetryInfo","retryDelay":"31s"}]}})
        if MODE["s"]=="day429": return await route.fulfill(status=429,json={"error":{"code":429,"message":"You exceeded your current quota. Quota exceeded for metric: grounding requests per day","details":[{"violations":[{"quotaId":"GroundingRequestsPerDayPerProject-FreeTier"}]}]}})
        if MODE["s"]=="zero": return await route.fulfill(status=429,json={"error":{"code":429,"message":"Quota exceeded for metric: search_grounding_free_tier, limit: 0","details":[]}})
        return await route.fulfill(json={"candidates":[{"content":{"parts":[{"text":"الراجحي 94.30، أرامكو 27.10، stc 41.85 ريال."}]},"groundingMetadata":{"webSearchQueries":["x"],"groundingChunks":[{"web":{"uri":"https://example.org/a","title":"saudiexchange.sa"}}]}}]})
    await route.fulfill(json={"candidates":[{"content":{"parts":[{"text":"ok"}]}}]})
say=lambda pg,u,a: pg.evaluate("(x)=>{__ws.onmessage({data:JSON.stringify({serverContent:{inputTranscription:{text:x[0]}}})});__ws.onmessage({data:JSON.stringify({serverContent:{outputTranscription:{text:x[1]}}})});__ws.onmessage({data:JSON.stringify({serverContent:{turnComplete:true}})})}",[u,a])
sysof=lambda pg: pg.evaluate("(function(){var a=__sent.filter(function(x){return x.indexOf('systemInstruction')>-1});var s=JSON.parse(a[a.length-1]).setup;return [JSON.stringify(s.systemInstruction),Object.keys(s).join(','),a.length,(s.tools[0].functionDeclarations||[]).length]})()")
async def go():
    async with async_playwright() as p:
        b,pg,call,lay,card,close=await boot(p,390,844,wsvar(NOG,WS_COUNT))
        await pg.route(re.compile(r"generativelanguage\.googleapis\.com/v1beta/models"),gem)
        s0=await sysof(pg);print("setup keys:",s0[1],"| tools:",s0[3])
        if "sessionResumption" in s0[1] or "contextWindowCompression" in s0[1]: F("HIGH","connection","continuous-session fields still sent")
        n0=len(await texts(pg))
        r=await call("memory_save",{"fact":"محاسبه اسمه خالد ورقمه 0500000000"});print("save:",r)
        r=await call("memory_save",{"fact":"يفضّل المقعد عند الممر ورحلات الصباح"},100);r=await call("memory_save",{"fact":"يفضّل المقعد عند الممر ورحلات الصباح"},100);print("same fact again:",r)
        r=await call("memory_save",{"fact":"رقم بطاقته 4111 1111 1111 1111"},100);print("card number:",r);r=await call("memory_save",{"fact":"كلمة السر حق البنك 1234"},100);print("password:",r.get("saved"))
        for u,a in [("أبغى أسافر جدة يوم الأحد","تمام، أي وقت يناسبك؟"),("الصبح بدري","لقيت لك رحلة السعودية 7:05 ص بـ 340 ريال"),("زين خذيها","تمام اخترتها. تبي فندق؟"),("إيه قريب من الكورنيش وحدّي 600","لحظة أشوف لك")]:
            await say(pg,u,a);await pg.wait_for_timeout(150)
        await pg.wait_for_timeout(2500)
        print("summary saved:",(await pg.evaluate("JSON.parse(localStorage.getItem('musaed.sum')||'{}').x||''"))[:70].replace("\n"," "),"| summary calls:",[x for x in LOG if x[1]=="none"][:1])
        hist=await pg.evaluate("new Promise(function(res){var q=indexedDB.open('musaed',1);q.onsuccess=function(){var g=q.result.transaction('files').objectStore('files').getAllKeys();g.onsuccess=function(){var ks=g.result.filter(function(k){return String(k).indexOf('hist/')===0});var v=q.result.transaction('files').objectStore('files').get(ks[0]);v.onsuccess=function(){res([ks,(v.result||[]).length])}}}})");print("history on the phone:",hist)
        # Google warns it will reset -> quiet reconnect with memory
        await pg.evaluate("__ws.onmessage({data:JSON.stringify({goAway:{timeLeft:'50s'}})})");await pg.wait_for_timeout(900)
        s1=await sysof(pg);tx=await texts(pg);st=await pg.evaluate("document.querySelector('#state').textContent")
        print("after Google's reset: connections",s1[2],"| greeting sent:",len(tx)>n0,"| state:",st)
        for needle,label in [("خالد","fact"),("الممر","preference"),("يخطط لرحلة جدة","summary"),("الكورنيش","last lines")]:
            ok=needle in json.loads(s1[0])["parts"][0]["text"];print("   she still has the",label+":",ok)
            if not ok: F("HIGH","memory",label+" missing after reconnect")
        if len(tx)>n0: F("HIGH","reconnect","she greets again")
        await pg.evaluate("__ws.onclose({code:1006,reason:''})");await pg.wait_for_timeout(900);s2=await sysof(pg);print("after a dropped connection: connections",s2[2],"| greeting:",len(await texts(pg))>n0,"| memory in:", "خالد" in s2[0])
        r=await call("memory_list",{},400);print("list:",len(r["facts"]),"facts |",(await card())[1:3]);await lay("memory card");await close()
        r=await call("history_search",{"query":"الفندق الكورنيش"});print("look back by words:",r.get("found"),[(x["who"],x["text"][:24]) for x in r.get("lines",[])][:2])
        r=await call("history_search",{"date":time.strftime("%Y-%m-%d")});print("look back by day:",len(r.get("lines",[])),"lines");r=await call("history_search",{"query":"برشلونة"});print("nothing there:",r.get("found"),r.get("note","")[:40])
        r=await call("memory_forget",{"query":"المقعد"},300);print("forget by words:",r.get("forgotten","")[:30],"| left:",len(json.loads(await pg.evaluate("localStorage.getItem('musaed.mem')"))))
        # a new conversation hours later keeps the old summary
        await pg.evaluate("localStorage.setItem('musaed.lt',String(Date.now()-5*3600000))");await say(pg,"السلام عليكم","وعليكم السلام");await pg.wait_for_timeout(300)
        print("next conversation: old summary archived:",len(json.loads(await pg.evaluate("localStorage.getItem('musaed.sums')||'[]'"))),"| current summary empty:",(await pg.evaluate("JSON.parse(localStorage.getItem('musaed.sum')).x"))=="")
        await pg.evaluate("__ws.onclose({code:1006,reason:''})");await pg.wait_for_timeout(900);s3=await sysof(pg);print("   previous conversation in her memory:", "محادثتكم السابقة" in json.loads(s3[0])["parts"][0]["text"])
        # search limits
        LOG.clear();MODE["s"]="lite429";r=await call("web_search",{"query":"سعر الراجحي وأرامكو و stc الآن","kind":"price"},100);print("fast model over its limit -> other model:",r.get("checked_on_web"),[x[0] for x in LOG if x[1]=="google_search"])
        LOG.clear();r=await call("web_search",{"query":"سعر الذهب","kind":"price"},100);print("  next search skips the limited model:",[x[0] for x in LOG if x[1]=="google_search"])
        MODE["s"]="ok";ACT["max"]=0;n1=await pg.evaluate("__sent.filter(x=>x.indexOf('toolResponse')>-1).length")
        await pg.evaluate("__ws.onmessage({data:JSON.stringify({toolCall:{functionCalls:[1,2,3,4].map(function(i){return {id:'s'+i,name:'web_search',args:{query:'سؤال رقم '+i,kind:'fact',depth:'deep'}}})}})})")
        while await pg.evaluate("__sent.filter(x=>x.indexOf('toolResponse')>-1).length")==n1: await pg.wait_for_timeout(100)
        print("four searches at once: most running together:",ACT["max"])
        MODE["s"]="day429";r=await call("web_search",{"query":"أخبار اليوم","kind":"news"},100);print("daily allowance used:",r.get("reason"),"|",r.get("tell_user","")[:70])
        await pg.evaluate("localStorage.removeItem('musaed.gm')");b2=None
        await pg.click("#setBtn");await pg.wait_for_timeout(400);print("status:",[l for l in (await pg.evaluate("document.querySelector('#diag').textContent")).split("\n") if any(k in l for k in ["البحث","رد Google","الذاكرة","الهادئة"])]);await pg.evaluate("document.querySelector('#card').classList.remove('open')");await pg.wait_for_timeout(300)
        # memory page + wipe
        await pg.click("#pfBtn");await pg.wait_for_timeout(600);print("memory page:",await pg.evaluate("[document.querySelectorAll('#mmList li').length,document.querySelector('#mmSum').textContent.replace(/\\n/g,' | ').slice(0,90)]"))
        await pg.click("#mmClear");await pg.wait_for_timeout(200);lab=await pg.evaluate("document.querySelector('#mmClear').textContent");await pg.click("#mmClear");await pg.wait_for_timeout(700)
        print("wipe (two taps):",lab,"->",await pg.evaluate("[localStorage.getItem('musaed.mem'),localStorage.getItem('musaed.sum'),localStorage.getItem('musaed.hd'),JSON.parse(localStorage.getItem('musaed.log')).length]"))
        print("errors",pg.errs);await b.close()
    print("FINDINGS",FIND)
asyncio.run(go())
