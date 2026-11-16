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
