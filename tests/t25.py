import asyncio, json, subprocess, time, re
from playwright.async_api import async_playwright
FIND=[]
def F(sev,area,msg): FIND.append((sev,area,msg)); print("  !!",sev,area,"-",msg)
srv=subprocess.Popen(["python3","-m","http.server","8771","--bind","127.0.0.1"],cwd="/home/claude/jarves",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
URL="http://127.0.0.1:8771/index.html"
MODELS=["gemini-flash-latest","gemini-flash-lite-latest","gemini-3.8-flash","gemini-3.6-flash","gemini-3.5-flash-lite","gemini-2.5-flash","gemini-2.5-flash-lite","gemini-2-flash"]
FULL={"gemini-flash-latest","gemini-flash-lite-latest","gemini-3.8-flash","gemini-3.6-flash"}
TRIED=[]
def q429(day):
    return {"error":{"code":429,"message":"You exceeded your current quota","details":[{"@type":"type.googleapis.com/google.rpc.QuotaFailure","violations":[{"quotaId":"GenerateRequestsPerDayPerProjectPerModel-FreeTier" if day else "GenerateRequestsPerMinutePerProjectPerModel-FreeTier"}]}]}}
async def gapi(route):
    u=route.request.url
    if "/models?" in u:
        return await route.fulfill(json={"models":[{"name":"models/"+m,"supportedGenerationMethods":["generateContent"]} for m in MODELS]})
    m=re.search(r"models/([^:]+):generateContent",u)
    if m:
        name=m.group(1);TRIED.append(name)
        if name in FULL: return await route.fulfill(status=429,json=q429(True))
        return await route.fulfill(json={"candidates":[{"content":{"parts":[{"text":"سعر الذهب اليوم 320 ريال للغرام."}]},"groundingMetadata":{"groundingChunks":[{"web":{"uri":"https://example.com/gold","title":"example.com"}}]}}]})
    return await route.fulfill(json={})
async def signup(pg):
    if await pg.evaluate("document.querySelector('#authSeg').hidden===false"): await pg.click("#authTabUp")
    await pg.fill("#auName","عمر");await pg.fill("#auEmail","o@t.com");await pg.fill("#auPass","pass-omar-1");await pg.fill("#auPass2","pass-omar-1");await pg.click("#authGo")
    for _ in range(40):
        await pg.wait_for_timeout(200)
        if await pg.evaluate("!!document.querySelector('[role=dialog] input[type=checkbox]')"): break
    await pg.evaluate("document.querySelector('[role=dialog] input[type=checkbox]').click()");await pg.evaluate("[...document.querySelectorAll('[role=dialog] button')].find(b=>b.textContent==='تم').click()");await pg.wait_for_timeout(1200)
async def go():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
        c=await b.new_context();pg=await c.new_page();errs=[];pg.on("pageerror",lambda e:errs.append(str(e)[:200]))
        await c.route("**/generativelanguage.googleapis.com/**",gapi)
        for u in ["**/api.open-meteo.com/**","**/api.aladhan.com/**","**/api.bigdatacloud.net/**"]: await c.route(u,lambda r:r.fulfill(json={}))
        await pg.goto(URL);await pg.evaluate("localStorage.clear()");await pg.reload();await pg.wait_for_timeout(800);await signup(pg)
        await pg.evaluate("localStorage.setItem('musaed.key','AIzaTEST')");await pg.reload();await pg.wait_for_timeout(2000);print(' errs so far:',errs, await pg.evaluate('typeof __nt'))
        r=await pg.evaluate("__nt.tool('web_search',{query:'سعر الذهب اليوم'})")
        print(" search answer:",json.dumps(r,ensure_ascii=False)[:200]);print(" models tried:",TRIED)
        if not r or r.get("error"): F("HIGH","search","no answer although free models had room")
        n1=len(TRIED);TRIED.clear()
        r=await pg.evaluate("__nt.tool('web_search',{query:'سعر الدولار'})");print(" 2nd search tried:",TRIED)
        if any(m in FULL for m in TRIED): F("MED","search","retried models already over their daily limit")
        await pg.reload();await pg.wait_for_timeout(1500);TRIED.clear()
        r=await pg.evaluate("__nt.tool('web_search',{query:'سعر النفط'})");print(" after reopening the app, tried:",TRIED)
        if any(m in FULL for m in TRIED): F("MED","search","daily-limit memory lost on reopen")
        print(" errors:",errs)
        await b.close()
    srv.terminate();print("\nFINDINGS:",len(FIND));[print(" ",f) for f in FIND]
asyncio.run(go())
# ---- part 2: every Google model over its limit -> nearby places from the free map
FULL2=set(MODELS)
async def gapi2(route):
    u=route.request.url
    if "/models?" in u: return await route.fulfill(json={"models":[{"name":"models/"+m,"supportedGenerationMethods":["generateContent"]} for m in MODELS]})
    if ":generateContent" in u: return await route.fulfill(status=429,json=q429(True))
    return await route.fulfill(json={})
OSM={"elements":[{"type":"node","lat":24.7140,"lon":46.6760,"tags":{"amenity":"restaurant","name":"مطعم البيك","cuisine":"chicken"}},
 {"type":"way","center":{"lat":24.7200,"lon":46.6800},"tags":{"amenity":"fast_food","name":"Kudu","name:ar":"كودو"}},
 {"type":"node","lat":24.7135,"lon":46.6752,"tags":{"amenity":"restaurant","name":"Najd Village","name:ar":"قرية نجد","opening_hours":"12:00-24:00"}},
 {"type":"node","lat":24.7300,"lon":46.7000,"tags":{"amenity":"restaurant"}}]}
async def go2():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/usr/bin/google-chrome",args=["--no-sandbox"])
        c=await b.new_context();pg=await c.new_page();errs=[];pg.on("pageerror",lambda e:errs.append(str(e)[:200]))
        await c.route("**/generativelanguage.googleapis.com/**",gapi2)
        seen=[]
        async def osm(route): seen.append(route.request.post_data or "");await route.fulfill(json=OSM)
        await c.route("**/overpass-api.de/**",osm)
        for u in ["**/api.open-meteo.com/**","**/api.aladhan.com/**","**/api.bigdatacloud.net/**"]: await c.route(u,lambda r:r.fulfill(json={}))
        srv2=subprocess.Popen(["python3","-m","http.server","8772","--bind","127.0.0.1"],cwd="/home/claude/jarves",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
        await pg.goto("http://127.0.0.1:8772/index.html");await pg.evaluate("localStorage.clear()");await pg.reload();await pg.wait_for_timeout(800);await signup(pg)
        await pg.evaluate("localStorage.setItem('musaed.key','AIzaTEST');localStorage.setItem('musaed.loc',JSON.stringify({lat:24.7136,lon:46.6753,city:'الرياض',t:Date.now()}))");await pg.reload();await pg.wait_for_timeout(1800)
        r=await pg.evaluate("__nt.tool('web_search',{query:'وين أقرب مطعم',kind:'place'})")
        print(" all Google models over limit -> places:",json.dumps(r.get("places"),ensure_ascii=False)[:300])
        print(" answer:",r.get("answer","").replace("\n"," | ")[:200],"| error:",r.get("error"))
        if not r.get("places") or r["places"][0]["name"]!="قرية نجد": F("HIGH","places","map fallback did not give nearest places")
        r2=await pg.evaluate("__nt.tool('web_search',{query:'كم سعر الذهب'})");print(" non-place search still reports the limit:",r2.get("error"),r2.get("reason"))
        if r2.get("places"): F("MED","search","map used for a non-place question")
        await pg.evaluate("__t.openCard('set')");await pg.wait_for_timeout(800);dg=await pg.text_content("#diag")
        print(" status:",[l for l in dg.split("\n") if l.startswith("البحث") or l.startswith("النماذج")])
        print(" errors:",errs);await b.close();srv2.terminate()
    print("\nFINDINGS total:",len(FIND))
asyncio.run(go2())
