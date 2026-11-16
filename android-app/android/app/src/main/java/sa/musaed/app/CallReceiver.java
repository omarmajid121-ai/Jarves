package sa.musaed.app;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.telephony.TelephonyManager;
import com.getcapacitor.JSObject;

/** Watches the phone line: tells the open app when the phone rings, and posts a missed-call alert. */
public class CallReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context c, Intent in) {
        if (in == null || !TelephonyManager.ACTION_PHONE_STATE_CHANGED.equals(in.getAction())) return;
        String st = in.getStringExtra(TelephonyManager.EXTRA_STATE);
        if (st == null) return;
        @SuppressWarnings("deprecation")
        String num = in.getStringExtra(TelephonyManager.EXTRA_INCOMING_NUMBER);
        SharedPreferences sp = Util.prefs(c);
        String prev = sp.getString("cs", "idle");
        String now = TelephonyManager.EXTRA_STATE_RINGING.equals(st) ? "ringing"
                : TelephonyManager.EXTRA_STATE_OFFHOOK.equals(st) ? "active" : "idle";
        SharedPreferences.Editor ed = sp.edit();
        if (num != null && !num.isEmpty()) ed.putString("cn", num);
        if (!now.equals(prev)) ed.putString("cs", now);
        if ("ringing".equals(now) && !"ringing".equals(prev)) ed.putLong("ct", System.currentTimeMillis());
        ed.apply();
        String known = num != null && !num.isEmpty() ? num : sp.getString("cn", "");
        if (num == null && "ringing".equals(now) && "ringing".equals(prev)) return; // duplicate broadcast without number
        String name = Util.contactName(c, known);

        JSObject d = new JSObject();
        d.put("state", now);
        d.put("number", known);
        d.put("name", name);
        MusaedPlugin.emit("call", d);

        if ("idle".equals(now) && "ringing".equals(prev)) {
            if (Util.on(c, "missed")) {
                String who = !name.isEmpty() ? name : (!known.isEmpty() ? known : "رقم مخفي");
                Util.post(c, Util.CH_CALLS, 2000 + (int) (System.currentTimeMillis() % 1000),
                        "مكالمة فائتة", who + " · اطلب من مساعد يتصل أو يرسل رسالة");
            }
            sp.edit().remove("cn").apply();
        } else if ("idle".equals(now)) {
            sp.edit().remove("cn").apply();
        }
    }
}
