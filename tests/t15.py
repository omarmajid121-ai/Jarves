import asyncio,sys
sys.argv=["x","none"]
exec(open("tests/audit.py").read().replace("asyncio.run(main())",""))
async def go():
    async with async_playwright() as p:
        b,pg,call,lay,card,close=await boot(p,390,844,NOG)
        await pg.click("#setBtn");await pg.wait_for_timeout(500);await call("reminder_add",{"text":"موعد الدواء","at":h(-1)},200)
        for i in range(16):
            await pg.wait_for_timeout(2000);t=await pg.evaluate("(function(){var e=document.querySelector('#toast');var r=e.getBoundingClientRect();var top=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);return [e.className,e.textContent.slice(0,50),!!top&&!!top.closest('#toast')]})()")
            if "حان وقته" in t[1]: print("toast over Settings:",t);break
        else: print("NO TOAST",t)
        print(pg.errs);await b.close()
asyncio.run(go())
