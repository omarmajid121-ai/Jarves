import asyncio, json, subprocess, time, re
from playwright.async_api import async_playwright
FIND=[]
def F(sev,area,msg): FIND.append((sev,area,msg)); print("  !!",sev,area,"-",msg)
srv=subprocess.Popen(["python3","-m","http.server","8773","--bind","127.0.0.1"],cwd="/home/claude/jarves",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
MODELS=["gemini-flash-latest","gemini-3.8-flash","gemini-3.6-flash","gemini-3.5-flash-lite","gemini-2.5-flash"]
G=[]
async def gapi(route):
    u=route.request.url
    if "/models?" in u: return await route.fulfill(json={"models":[{"name":"models/"+m,"supportedGenerationMethods":["generateContent"]} for m in MODELS]})
    if ":generateContent" in u:
        G.append(u);return await route.fulfill(status=429,json={"error":{"code":429,"message":"quota","details":[{"@type":"type.googleapis.com/google.rpc.QuotaFailure","violations":[{"quotaId":"GenerateRequestsPerMinutePerProjectPerModel-FreeTier"}]}]}})
    return await route.fulfill(json={})
FX={"result":"success","time_last_update_utc":"Mon, 16 Nov 2026 00:02:31 +0000","rates":{"SAR":1,"USD":0.2667,"EUR":0.2293,"GBP":0.2011,"AED":0.9793,"EGP":13.1}}
FXU={"result":"success","rates":{"SAR":3.75}}
async def free(route):
    u=route.request.url
    if "open.er-api.com/v6/latest/SAR" in u: return await route.fulfill(json=FX)
    if "open.er-api.com/v6/latest/USD" in u: return await route.fulfill(json=FXU)
    if "gold-api.com/price/XAU" in u: return await route.fulfill(json={"name":"Gold","price":3887.6,"symbol":"XAU"})
    if "coingecko" in u: return await route.fulfill(json={"bitcoin":{"sar":360000,"usd":96000,"sar_24h_change":-1.23}})
    if "gdeltproject" in u: return await route.fulfill(json={"articles":[{"title":"خبر أول عن الرياض","domain":"spa.gov.sa","url":"https://spa.gov.sa/1"},{"title":"خبر ثاني","domain":"alarabiya.net","url":"https://alarabiya.net/2"}]})
    if "wikipedia.org/w/api.php" in u: return await route.fulfill(json={"query":{"search":[{"title":"محمد عبده"}]}})
    if "wikipedia.org/api/rest_v1/page/summary" in u: return await route.fulfill(json={"extract":"محمد عبده فنان سعودي ولد عام 1949."})
    if "overpass" in u: return await route.fulfill(json={"elements":[{"type":"node","lat":24.7139,"lon":46.6755,"tags":{"amenity":"pharmacy","name:ar":"صيدلية النهدي"}}]})
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
        c=await b.new_context(geolocation={"latitude":24.7136,"longitude":46.6753},permissions=["geolocation"]);pg=await c.new_page();errs=[];pg.on("pageerror",lambda e:errs.append(str(e)[:200]))
        await c.route("**/generativelanguage.googleapis.com/**",gapi)
        for h in ["**/open.er-api.com/**","**/api.gold-api.com/**","**/api.coingecko.com/**","**/api.gdeltproject.org/**","**/*.wikipedia.org/**","**/overpass-api.de/**","**/api.open-meteo.com/**","**/api.aladhan.com/**","**/api.bigdatacloud.net/**"]: await c.route(h,free)
        await pg.goto("http://127.0.0.1:8773/index.html");await pg.evaluate("localStorage.clear()");await pg.reload();await pg.wait_for_timeout(800);await signup(pg)
        await pg.evaluate("localStorage.setItem('musaed.key','AIzaTEST')");await pg.reload();await pg.wait_for_timeout(1800)
        cases=[("كم سعر الذهب اليوم","fact","Gold API","عيار 21"),("كم 100 دولار بالريال","fact","Exchange Rate API","100 USD"),("كم سعر البيتكوين","fact","CoinGecko","bitcoin"),
               ("وش آخر أخبار الرياض","news","GDELT","خبر أول"),("مين محمد عبده","fact","Wikipedia","1949"),("وين أقرب صيدلية","place","OpenStreetMap (free map)","النهدي"),("كم الجنيه الاسترليني","fact","Exchange Rate API","GBP")]
        for q,k,src,must in cases:
            G.clear();r=await pg.evaluate("__nt.tool('web_search',%s)"%json.dumps({"query":q,"kind":k},ensure_ascii=False))
            ok=r.get("source")==src and must in r.get("answer","")
            print(" %-22s -> %-24s google calls %d | %s"%(q,r.get("source") or r.get("error"),len(G),r.get("answer","").replace("\n"," | ")[:90]))
            if not ok: F("HIGH","free",q+" not answered from "+src)
        g=await pg.evaluate("__nt.tool('web_search',{query:'كم 100 دولار بالريال'})");print(" gbp check: EGP mixed in?", "EGP" in json.dumps(await pg.evaluate("__nt.tool('web_search',{query:'كم الجنيه الاسترليني'})")))
        await pg.evaluate("__t.openCard('set')");await pg.wait_for_timeout(700);dg=await pg.text_content("#diag");print(" status:",[l for l in dg.split("\n") if l.startswith("البحث") or l.startswith("النماذج")])
        print(" errors:",errs);await b.close()
    srv.terminate();print("\nFINDINGS:",len(FIND));[print(" ",f) for f in FIND]
asyncio.run(go())
