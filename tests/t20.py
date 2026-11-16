import asyncio, datetime, base64
src=open("tests/audit2.py").read().replace("asyncio.run(main2())","")
exec(src)
FIND.clear()
PCM=base64.b64encode(bytes(9600)).decode()
now=datetime.datetime.now()
async def go():
    async with async_playwright() as p:
        b,pg,call,lay,card,close=await boot(p,390,844,wsvar(NOG,WS_COUNT))
        await pg.context.grant_permissions(["microphone","geolocation"])
        msg=lambda o: pg.evaluate("o=>__ws.onmessage({data:JSON.stringify(o)})",o)
        audio=lambda: msg({"serverContent":{"modelTurn":{"parts":[{"inlineData":{"mimeType":"audio/pcm;rate=24000","data":PCM}}]}}})
        st=lambda: pg.evaluate("({...__mz(),sent:__sent.length,last:__sent[__sent.length-1].slice(0,160),bubbles:[...document.querySelectorAll('#msgs .msg')].slice(-3).map(e=>e.className+': '+e.textContent.slice(0,40))})")
        await pg.wait_for_timeout(600)
        # 1 hush by voice while she speaks
        await msg({"serverContent":{"inputTranscription":{"text":"احكي لي عن تاريخ الرياض"}}});await msg({"serverContent":{"turnComplete":True}})
        for i in range(4): await audio()
        await msg({"serverContent":{"outputTranscription":{"text":"الرياض مدينة قديمة"}}})
        a=await st();print(" speaking:",a["playing"],"chunks")
        await msg({"serverContent":{"inputTranscription":{"text":"اسكتي"}}});await pg.wait_for_timeout(900)
        a=await st();sent_note=await pg.evaluate("__sent.some(x=>x.indexOf('قلت لك تسكتين')>-1)");print(" after «اسكتي»: playing",a["playing"],"| hushed",a["hushed"],"| note sent:",sent_note)
        if a["playing"] or not a["hushed"] or not sent_note: F("HIGH","hush","she did not stop on «اسكتي»")
        for i in range(3): await audio()
        await msg({"serverContent":{"outputTranscription":{"text":"تمام، سكتت"}}})
        a=await st();print(" her reply while hushed: playing",a["playing"],"| bubbles",a["bubbles"])
        if a["playing"] or any("سكتت" in x for x in a["bubbles"]): F("HIGH","hush","she still talks after being told to stop")
        await msg({"serverContent":{"turnComplete":True}})
        await msg({"serverContent":{"inputTranscription":{"text":"وش الطقس اليوم"}}})
        await audio();a=await st();print(" next question: hushed",a["hushed"],"| playing",a["playing"])
        if a["hushed"] or not a["playing"]: F("HIGH","hush","she stays silent after he asks something new")
        await msg({"serverContent":{"turnComplete":True}});await pg.wait_for_timeout(500)
        # 1b sentences that START with a stop word, arriving in pieces
        for parts in (["خلاص"," احفظيه"],["بس"," أبي أسألك عن الموعد"]):
            for i in range(3): await audio()
            await msg({"serverContent":{"inputTranscription":{"text":parts[0]}}});await pg.wait_for_timeout(250)
            await msg({"serverContent":{"inputTranscription":{"text":parts[1]}}});await pg.wait_for_timeout(800)
            a=await st();print(" «"+"".join(parts)+"» in pieces: hushed",a["hushed"])
            if a["hushed"]: F("HIGH","hush","a sentence starting with "+parts[0]+" silenced her")
            await msg({"serverContent":{"turnComplete":True}})
        # 1c app notes wait for her to finish
        for i in range(6): await audio()
        n0=len(await pg.evaluate("__sent"));await call("driving_mode",{"on":True},100)
        a=await st();print(" app note while she speaks: playing still",a["playing"]>0)
        await call("driving_mode",{"on":False},100)
        await msg({"serverContent":{"turnComplete":True}});await pg.wait_for_timeout(2500)
        # 2 a normal sentence with بس
        await msg({"serverContent":{"inputTranscription":{"text":"ابي قهوة بس"}}});a=await st();print(" «ابي قهوة بس» hushes:",a["hushed"])
        if a["hushed"]: F("HIGH","hush","a normal sentence ending in بس silenced her")
        await msg({"serverContent":{"turnComplete":True}})
        # 3 tap to cut her off
        for i in range(4): await audio()
        await pg.evaluate("document.querySelector('#stage').click()");a=await st()
        print(" tap while speaking: playing",a["playing"],"| she is told:",'قاطعتك' in a["last"])
        if a["playing"] or 'قاطعتك' not in a["last"]: F("HIGH","tap","she is not told he cut her off")
        await msg({"serverContent":{"turnComplete":True}});await msg({"serverContent":{"inputTranscription":{"text":"كمّلي"}}});a=await st();print(" he speaks again: hushed",a["hushed"])
        await msg({"serverContent":{"turnComplete":True}})
        # 4 rules
        sy=json.loads(await pg.evaluate("__sent.filter(x=>x.indexOf('systemInstruction')>-1).pop()"))["setup"]
        txt=sy["systemInstruction"]["parts"][0]["text"];names=[f["name"] for f in sy["tools"][0]["functionDeclarations"]]
        order=[txt.find(k) for k in ["## طريقة كلامك","## الصلاحيات","## اللغة واللهجة","## الأوامر والتفاصيل"]]
        print(" rules order:",order,"| set_language declared:","set_language" in names,"| tools:",len(names),"| chars:",len(txt))
        if sorted(order)!=order or -1 in order: F("MED","rules","sections missing or out of order")
        # 5 language switch
        n0=await pg.evaluate("__sent.length")
        r=await call("set_language",{"language":"en"});await pg.wait_for_timeout(1600)
        ss=[json.loads(x) for x in await pg.evaluate(f"__sent.slice({n0})")]
        su=[x for x in ss if "setup" in x];tx=[x["realtimeInput"]["text"] for x in ss if "realtimeInput" in x and "text" in x["realtimeInput"]]
        v=su[-1]["setup"]["generationConfig"]["speechConfig"]["voiceConfig"]["prebuiltVoiceConfig"]["voiceName"] if su else None
        print(" to English:",r.get("switching"),"| new voice",v,"| prompt starts:",su[-1]["setup"]["systemInstruction"]["parts"][0]["text"][:30] if su else None,"| first line:",tx[-1][:60] if tx else None)
        if not su or not su[-1]["setup"]["systemInstruction"]["parts"][0]["text"].find("You are Musaed")>-1: F("HIGH","language","switch to English did not happen")
        n0=await pg.evaluate("__sent.length");r=await call("set_language",{"language":"ar"});await pg.wait_for_timeout(1600)
        su=[json.loads(x) for x in await pg.evaluate(f"__sent.slice({n0})") if '"setup"' in x]
        print(" back to Arabic:",su[-1]["setup"]["generationConfig"]["speechConfig"]["voiceConfig"]["prebuiltVoiceConfig"]["voiceName"] if su else None,"| prompt:",su[-1]["setup"]["systemInstruction"]["parts"][0]["text"][:20] if su else None)
        r=await call("set_language",{"language":"ar"});print(" again Arabic:",r)
        # 6 cards
        await call("budget",{"action":"set","category":"مطاعم","amount":1000});await call("budget",{"action":"set","category":"وقود","amount":500});await close()
        await call("expense_add",{"amount":850,"category":"مطاعم"});await call("expense_add",{"amount":600,"category":"وقود"});await close()
        await call("budget",{"action":"status"});await pg.wait_for_timeout(900)
        bars=await pg.evaluate("[...document.querySelectorAll('#act .cb-bars > div')].map(d=>[d.className,d.querySelector('.t i').style.width,d.innerText.replace(/\\n/g,' ')])")
        solo=await pg.evaluate("[document.querySelector('#act').classList.contains('solo'),getComputedStyle(document.querySelector('#act .abtns')).display,!!document.querySelector('#actX').offsetWidth]")
        print(" budget bars:",bars,"| solo card:",solo);await pg.screenshot(path="tests/out/k2_budget.png")
        await pg.evaluate("document.querySelector('#actX').click()");await pg.wait_for_timeout(300);print(" X closes:",not await pg.evaluate("document.querySelector('#act').classList.contains('on')"))
        # swipe down
        await call("show_occasions",{});await pg.wait_for_timeout(500)
        await pg.evaluate("""(()=>{var el=document.querySelector('#act .arow'),r=el.getBoundingClientRect();function T(type,y){var t=new Touch({identifier:1,target:el,clientX:r.left+60,clientY:y});el.dispatchEvent(new TouchEvent(type,{touches:type==='touchend'?[]:[t],changedTouches:[t],bubbles:true}))}
          T('touchstart',r.top+10);T('touchmove',r.top+60);T('touchmove',r.top+140);T('touchend',r.top+140)})()""");await pg.wait_for_timeout(300)
        print(" swipe down closes:",not await pg.evaluate("document.querySelector('#act').classList.contains('on')"))
        # card with a button keeps its row
        await call("show_action",{"type":"call","name":"محمد","number":"+966500000001"});print(" call card buttons shown:",await pg.evaluate("getComputedStyle(document.querySelector('#act .abtns')).display"));await close()
        # counts
        dd=(now+datetime.timedelta(days=2)).day;r=await call("bills",{"action":"add","name":"STC","amount":230,"due_day":dd});print(" bill in 2 days:",r["bill"]["status"]);await close()
        r=await call("routine",{"action":"save","name":"صباحي","steps":["الطقس","ملخص اليوم"]});print(" routine steps:",(await card())[1:3]);await close()
        if "بعد يومين" not in r and r: pass
        # delete unknown meeting without Google
        r=await call("calendar_delete",{"event_id":"abc123"});c=await card();print(" delete unknown:",r.get("error"),"| card:",c[1] if c[0] else "none");await close()
        if c[0] and "Google" in str(c[1]): F("LOW","delete","unknown meeting still shows Connect Google")
        print(" errors",pg.errs);await b.close()
    print("FINDINGS",len(FIND))
    for f in FIND: print(" ",f)
asyncio.run(go())
