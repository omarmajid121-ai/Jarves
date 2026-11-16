# Runs a test file with a signed-in test account already on the phone (the app now needs an account).
import sys, runpy
from playwright.async_api import BrowserContext, Browser
SEED="(function(){try{if(!localStorage.getItem('musaed.users')){localStorage.setItem('musaed.users',JSON.stringify([{id:'t1',email:'t@t.t',name:'T',salt:'',hash:'',it:1}]));localStorage.setItem('musaed.cur','t1')}}catch(e){}})();"
_np=BrowserContext.new_page
async def new_page(self,*a,**k):
    pg=await _np(self,*a,**k)
    if not getattr(self,"_seeded",False):
        await self.add_init_script(SEED);self._seeded=True
    return pg
BrowserContext.new_page=new_page
_bnp=Browser.new_page
async def bnew_page(self,*a,**k):
    pg=await _bnp(self,*a,**k);await pg.context.add_init_script(SEED);return pg
Browser.new_page=bnew_page
_nc=Browser.new_context
async def new_context(self,*a,**k):
    c=await _nc(self,*a,**k);await c.add_init_script(SEED);c._seeded=True;return c
Browser.new_context=new_context
sys.argv=sys.argv[1:]
runpy.run_path(sys.argv[0],run_name="__main__")
