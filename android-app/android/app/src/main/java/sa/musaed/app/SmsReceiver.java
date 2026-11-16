package sa.musaed.app;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.provider.Telephony;
import android.telephony.SmsMessage;
import com.getcapacitor.JSObject;

/** New SMS: tells the open app, and alerts when a bank message looks like a purchase. */
public class SmsReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context c, Intent in) {
        if (in == null || !Telephony.Sms.Intents.SMS_RECEIVED_ACTION.equals(in.getAction())) return;
        SmsMessage[] parts;
        try {
            parts = Telephony.Sms.Intents.getMessagesFromIntent(in);
        } catch (Exception e) {
            return;
        }
        if (parts == null || parts.length == 0) return;
        String from = "";
        StringBuilder body = new StringBuilder();
        long t = System.currentTimeMillis();
        for (SmsMessage m : parts) {
            if (m == null) continue;
            if (from.isEmpty() && m.getDisplayOriginatingAddress() != null) from = m.getDisplayOriginatingAddress();
            if (m.getDisplayMessageBody() != null) body.append(m.getDisplayMessageBody());
            t = m.getTimestampMillis() > 0 ? m.getTimestampMillis() : t;
        }
        String text = body.toString();
        JSObject d = new JSObject();
        d.put("from", from);
        d.put("text", text);
        d.put("t", t);
        String amt = Util.spendAmount(text);
        d.put("spend", amt != null);
        MusaedPlugin.emit("sms", d);

        if (amt != null && Util.on(c, "bank") && !Util.foreground) {
            Util.post(c, Util.CH_MONEY, 3000 + (int) (t % 1000), "مصروف جديد: " + amt + " ر.س",
                    "من " + from + " · افتح مساعد ويسجّله في مصاريفك");
        }
    }
}
