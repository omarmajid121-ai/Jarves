import asyncio,sys,time
sys.argv=["x","none"]
exec(open("tests/audit.py").read().replace("asyncio.run(main())",""))
LOG=[];MODE={"v":"ok","delay":300}
async def gem(route):
    rq=route.request;u=rq.url
    if rq.method=="GET":
        LOG.append("list");return await route.fulfill(json={"models":[{"name":"models/"+n,"supportedGenerationMethods":["generateContent"]} for n in ["gemini-3.8-flash","gemini-3.6-flash","gemini-3.5-flash-lite","gemini-3.8-flash-tts","gemini-3.1-flash-image-preview","gemini-2.5-flash"]]+[{"name":"models/gemini-3.8-live","supportedGenerationMethods":["bidiGenerateContent"]}]})
    b=json.loads(rq.post_data);m=re.search(r"models/([^:]+):",u).group(1);q=b["contents"][0]["parts"][0]["text"]
    LOG.append((m,"search" if b.get("tools")==[{"google_search":{}}] else "NO-TOOL",b.get("generationConfig"),q[:30]))
    if MODE["v"]=="lite400" and "lite" in m: return await route.fulfill(status=400,json={"error":{"message":"Search grounding is not supported"}})
    if MODE["v"]=="cfg400" and b.get("generationConfig"): return await route.fulfill(status=400,json={"error":{"message":"thinkingLevel unsupported"}})
    if MODE["v"]=="quota": return await route.fulfill(status=429,json={"error":{}})
    await asyncio.sleep(MODE["delay"]/1000)
    if MODE["v"]=="nog": return await route.fulfill(json={"candidates":[{"content":{"parts":[{"text":"أعتقد أن السعر 94"}]}}]})
    await route.fulfill(json={"candidates":[{"content":{"parts":[{"thought":True,"text":"thinking"},{"text":"**سعر سهم الراجحي** 94.30 ريال، مرتفع 0.8% اليوم.\nوقت السعر 3:10 م، تداول."}]},"groundingMetadata":{"webSearchQueries":["سعر الراجحي"],"groundingChunks":[{"web":{"uri":"https://vertexaisearch.cloud.google.com/grounding-api-redirect/abc","title":"saudiexchange.sa"}},{"web":{"uri":"https://vertexaisearch.cloud.google.com/grounding-api-redirect/def","title":"argaam.com"}},{"web":{"uri":"javascript:alert(1)","title":"bad"}}]}}]})
async def go():
    async with async_playwright() as p:
        b,pg,call,lay,card,close=await boot(p,390,844,NOG)
        await pg.route(re.compile(r"generativelanguage\.googleapis\.com/v1beta/models"),gem)
        st=json.loads(await pg.evaluate("__sent[0]"))["setup"];print("setup:",st["model"],"| built-in search sent:",any("googleSearch" in t for t in st["tools"]),"| tools:",len(st["tools"][0]["functionDeclarations"]),"| connects:",await pg.evaluate("__sent.filter(x=>x.indexOf('systemInstruction')>-1).length"))
        await pg.evaluate("localStorage.removeItem('musaed.gm')")
        t=time.time();r=await call("web_search",{"query":"كم سعر سهم الراجحي الآن","kind":"price"},50);print("1 price:",round(time.time()-t,2),"s",json.dumps(r,ensure_ascii=False)[:330]);print("  calls:",LOG);LOG.clear()
        t=time.time();r=await call("web_search",{"query":"كم سعر سهم الراجحي الآن","kind":"price"},50);print("2 same again (cache):",round(time.time()-t,2),"s",r.get("from_cache"),LOG);LOG.clear()
        t=time.time();r=await call("web_search",{"query":"رحلات الرياض جدة الأحد 15 نوفمبر","kind":"flights"},50);print("3 flights uses the smart model:",LOG);LOG.clear()
        # parallel
        n0=await pg.evaluate("__sent.filter(x=>x.indexOf('toolResponse')>-1).length");MODE["delay"]=1200;t=time.time()
        await pg.evaluate("__ws.onmessage({data:JSON.stringify({toolCall:{functionCalls:[{id:'a',name:'web_search',args:{query:'سعر أرامكو',kind:'price'}},{id:'b',name:'web_search',args:{query:'سعر سابك',kind:'price'}},{id:'c',name:'web_search',args:{query:'سعر stc',kind:'price'}}]}})})")
        await pg.wait_for_timeout(150);print("4 status while searching:",await pg.evaluate("document.querySelector('#state').textContent"))
        while await pg.evaluate("__sent.filter(x=>x.indexOf('toolResponse')>-1).length")==n0: await pg.wait_for_timeout(50)
        rr=json.loads(await pg.evaluate("__sent.filter(x=>x.indexOf('toolResponse')>-1).slice(-1)[0]"))["toolResponse"]["functionResponses"];print("  three searches together:",round(time.time()-t,2),"s for",len(rr),"answers | status after:",await pg.evaluate("document.querySelector('#state').textContent"));MODE["delay"]=300;LOG.clear()
        r=await call("show_sources",{},500);print("5 sources card:",(await pg.evaluate("document.querySelector('#act').innerText")).replace("\n"," | ")[:160]);await lay("sources card");await close()
        MODE["v"]="lite400";await pg.evaluate("localStorage.removeItem('musaed.gm')");await pg.reload();await pg.wait_for_timeout(1500);await pg.route(re.compile(r"generativelanguage\.googleapis\.com/v1beta/models"),gem);LOG.clear()
        r=await call("web_search",{"query":"من فاز بمباراة الهلال أمس","kind":"fact"},50);print("6 fast model refuses search -> falls to smart:",r.get("checked_on_web"),LOG);LOG.clear()
        r=await call("web_search",{"query":"متى مباراة النصر القادمة","kind":"fact"},50);print("  next call goes straight to smart:",LOG);LOG.clear()
        MODE["v"]="cfg400";r=await call("web_search",{"query":"سعر الذهب اليوم","kind":"price"},50);print("7 setting refused -> retried without it:",r.get("found"),[x[2] for x in LOG]);LOG.clear()
        r=await call("web_search",{"query":"سعر الفضة اليوم","kind":"price"},50);print("  remembered:",[x[2] for x in LOG]);LOG.clear()
        MODE["v"]="nog";r=await call("web_search",{"query":"سعر سهم المراعي","kind":"price"},50);print("8 answer without a web check:",r.get("checked_on_web"),"|",r.get("note","")[:60])
        MODE["v"]="quota";r=await call("web_search",{"query":"أخبار اليوم","kind":"news"},50);print("9 limit reached:",json.dumps(r,ensure_ascii=False)[:150])
        MODE["v"]="ok";MODE["delay"]=11500;t=time.time();r=await call("web_search",{"query":"ساعات دوام مكتبة جرير اليوم","kind":"place"},50);print("10 too slow:",round(time.time()-t,1),"s",json.dumps(r,ensure_ascii=False)[:110]);MODE["delay"]=300
        r=await call("web_search",{"query":""},50);print("11 empty:",r)
        await pg.click("#setBtn");await pg.wait_for_timeout(500);print("status:",(await pg.evaluate("document.querySelector('#diag').textContent")).replace("\n"," | ")[:200])
        print("errors",pg.errs);await b.close()
asyncio.run(go())
