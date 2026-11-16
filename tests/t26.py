import asyncio, base64
src=open("/tmp/shot/audit2.py").read().replace("asyncio.run(main2())","")
exec(src)
FIND.clear()
PCM=base64.b64encode(bytes(9600)).decode()
async def go():
    async with async_playwright() as p:
        b,pg,call,lay,card,close=await boot(p,390,844,wsvar(NOG,WS_COUNT))
        await pg.context.grant_permissions(["microphone","geolocation"])
        msg=lambda o: pg.evaluate("o=>__ws.onmessage({data:JSON.stringify(o)})",o)
        audio=lambda: msg({"serverContent":{"modelTurn":{"parts":[{"inlineData":{"mimeType":"audio/pcm;rate=24000","data":PCM}}]}}})
        await pg.wait_for_timeout(800)
        setup=await pg.evaluate("__sent.map(s=>{try{return JSON.parse(s)}catch(e){return null}}).filter(x=>x&&x.setup)[0]")
        si=setup["setup"]["systemInstruction"]["parts"][0]["text"] if setup else ""
        print(" language lock at start and end of rules:",si.startswith("RESPOND IN ARABIC"),si.rstrip().endswith("then ask him to repeat in Arabic."))
        if not si.startswith("RESPOND IN ARABIC"): F("HIGH","language","no language lock in rules")
        n0=await pg.evaluate("__sent.length")
        # normal Saudi reply with an English brand name: no correction
        await audio();await msg({"serverContent":{"outputTranscription":{"text":"تمام، فتحت لك Starbucks في Google Maps"}}});await msg({"serverContent":{"turnComplete":True}});await pg.wait_for_timeout(300)
        n1=await pg.evaluate("__sent.length");notes=await pg.evaluate(f"__sent.slice({n0}).filter(s=>s.indexOf('غير العربية')>-1).length")
        print(" Arabic reply with English names corrected:",notes,"(must be 0)")
        if notes: F("HIGH","language","false correction of an Arabic reply")
        # drifts into Spanish
        await audio();await msg({"serverContent":{"outputTranscription":{"text":"Claro, el restaurante más cercano está "}}})
        await msg({"serverContent":{"outputTranscription":{"text":"a dos kilómetros de aquí"}}});await pg.wait_for_timeout(300)
        notes=await pg.evaluate(f"__sent.slice({n1}).filter(s=>s.indexOf('غير العربية')>-1).length");a=await pg.evaluate("__mz()")
        print(" Spanish reply -> stopped and asked to repeat in Saudi:",notes==1,"| audio stopped:",a["playing"]==0)
        if notes!=1: F("HIGH","language","Spanish reply not corrected")
        await msg({"serverContent":{"outputTranscription":{"text":" y tiene muy buena comida"}}});await pg.wait_for_timeout(200)
        notes=await pg.evaluate(f"__sent.slice({n1}).filter(s=>s.indexOf('غير العربية')>-1).length");print(" corrected only once per reply:",notes==1)
        await msg({"serverContent":{"interrupted":True}});await msg({"serverContent":{"outputTranscription":{"text":"أقرب مطعم يبعد كيلوين"}}});await msg({"serverContent":{"turnComplete":True}})
        await pg.evaluate("__t.openCard('set')");await pg.wait_for_timeout(600);dg=await pg.text_content("#diag");print(" status:",[l for l in dg.split("\n") if "اللغة" in l])
        await b.close()
    print("\nFINDINGS:",len(FIND));[print(" ",f) for f in FIND]
asyncio.run(go())
