import asyncio, sys, time, json, subprocess, numpy as np, soundfile as sf
sys.argv=["x","none"]
_a=open("/tmp/shot/audit.py").read().replace("asyncio.run(main())","").replace("file:///home/claude/jarves/index.html","http://127.0.0.1:8775/index.html")
exec(_a)
exec(open("/tmp/shot/audit2.py").read().split('exec(open("/tmp/shot/audit.py")')[0].replace("import asyncio, sys, time",""))
_b=open("/tmp/shot/audit2.py").read();exec(_b[_b.index("FULL=INIT"):_b.index("async def A(p)")])
FIND.clear()
srv=subprocess.Popen(["python3","-m","http.server","8775","--bind","127.0.0.1"],cwd="/home/claude/jarves",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
D="/tmp/spk/sr-data/"
def wav(f): x,sr=sf.read(D+f,dtype='float32');return x
SIL=np.zeros(16000*1,dtype=np.float32)
async def say(pg,x):
    for i in range(0,len(x),4096): await pg.evaluate("a=>__vid.feed(a,16000)",x[i:i+4096].tolist())
    for i in range(0,len(SIL),4096): await pg.evaluate("a=>__vid.feed(a,16000)",SIL[i:i+4096].tolist())
    for _ in range(60):
        await pg.wait_for_timeout(200)
        if await pg.evaluate("__vid.pend()")==0: break
async def go():
    async with async_playwright() as p:
        b,pg,call,lay,card,close=await boot(p,390,844,wsvar(NOG,WS_COUNT))
        await pg.wait_for_timeout(800)
        await pg.evaluate("__vid.need(5,12,1)")
        owner=["enroll/fangjun-sr-1.wav","enroll/fangjun-sr-2.wav","enroll/fangjun-sr-3.wav","test/fangjun-test-sr-1.wav","enroll/fangjun-sr-2.wav"]
        for i,f in enumerate(owner+owner[:3]):
            if (await pg.evaluate("__vid.cfg()")).get("ready"): break
            await say(pg,wav(f));c=await pg.evaluate("__vid.cfg()");print(" learning after %d sentences: kept %s, %.1fs, ready %s"%(i+1,c.get("kept"),c.get("sec",0),c.get("ready")))
        c=await pg.evaluate("__vid.cfg()")
        if not c.get("ready"): F("HIGH","voice","did not finish learning")
        print(" owner threshold:",c.get("hi"),"| stored on phone for this account:",len(json.dumps(c))//1024,"KB")
        n0=await pg.evaluate("__sent.length")
        await say(pg,wav("test/fangjun-test-sr-2.wav"));cur=await pg.evaluate("__vid.cur()");print(" owner speaks:",cur)
        if cur["who"]!="owner": F("HIGH","voice","owner not recognised")
        r=await call("memory_list",{});print(" owner asks private thing ->", "allowed" if not (r or {}).get("error") else r.get("error"))
        await say(pg,wav("test/leijun-test-sr-1.wav"));cur=await pg.evaluate("__vid.cur()");print(" someone else speaks:",cur)
        if cur["who"]=="owner": F("HIGH","voice","stranger taken for the owner")
        notes=await pg.evaluate(f"__sent.slice({n0}).filter(s=>s.indexOf('مو صاحب الجوال')>-1).length");print(" hidden note to her about the stranger:",notes)
        r=await call("phone_messages",{});r2=await call("memory_list",{})
        print(" stranger asks private things ->",(r or {}).get("error"),(r2 or {}).get("error"))
        if (r2 or {}).get("error") not in ("not_owner","voice_not_sure"): F("HIGH","voice","private command allowed for a stranger")
        r=await call("web_search",{"query":"كم الساعة"});print(" stranger asks a general question -> blocked?",(r or {}).get("error")=="not_owner")
        if (r or {}).get("error")=="not_owner": F("MED","voice","general question blocked for stranger")
        await say(pg,wav("test/liudehua-test-sr-1.wav"));print(" third person:",await pg.evaluate("__vid.cur()"))
        await say(pg,wav("test/fangjun-test-sr-1.wav"));cur=await pg.evaluate("__vid.cur()");print(" owner again:",cur)
        back=await pg.evaluate(f"__sent.slice({n0}).filter(s=>s.indexOf('رجع يتكلم')>-1).length");print(" note that the owner is back:",back)
        r=await call("memory_list",{});print(" owner private command after ->","allowed" if not (r or {}).get("error") else r.get("error"))
        if (r or {}).get("error"): F("HIGH","voice","owner blocked")
        await pg.evaluate("__t.openCard('set')");await pg.wait_for_timeout(700)
        rows=await pg.evaluate("[...document.querySelectorAll('#vidG .cell')].map(b=>b.innerText.replace(/\\n/g,' : '))");print(" settings:",rows)
        dg=await pg.text_content("#diag");print(" status:",[l for l in dg.split("\n") if "بصمة" in l])
        # ignore mode
        await pg.evaluate("[...document.querySelectorAll('#vidG .cell')].find(b=>b.innerText.indexOf('غيرك')>-1).click()");await say(pg,wav("test/fangjun-test-sr-2.wav"));n1=await pg.evaluate("__sent.length")
        await say(pg,wav("test/leijun-test-sr-2.wav"));print(" stranger in ignore mode:",await pg.evaluate("__vid.cur()"));ig=await pg.evaluate(f"__sent.slice({n1}).filter(s=>s.indexOf('لا تردين عليه')>-1).length");print(" ignore mode note:",ig)
        if not ig: F("MED","voice","ignore mode not applied")
        print(" page errors:",pg.errs)
        await b.close()
    srv.terminate();print("\nFINDINGS:",len(FIND));[print(" ",f) for f in FIND]
asyncio.run(go())
