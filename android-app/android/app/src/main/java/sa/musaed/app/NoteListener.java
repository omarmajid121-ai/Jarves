package sa.musaed.app;

import android.app.Notification;
import android.content.Context;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;
import com.getcapacitor.JSObject;
import org.json.JSONArray;
import org.json.JSONObject;

/** Keeps a short, on-phone list of notifications from other apps so Musaed can read them out on request. */
public class NoteListener extends NotificationListenerService {
    static final int KEEP = 300;
    static final long KEEP_MS = 3L * 24 * 3600 * 1000;
    private static final Object LOCK = new Object();

    static JSONArray load(Context c) {
        try {
            return new JSONArray(Util.prefs(c).getString("notes", "[]"));
        } catch (Exception e) {
            return new JSONArray();
        }
    }

    static void clear(Context c) {
        synchronized (LOCK) {
            Util.prefs(c).edit().remove("notes").apply();
        }
    }

    @Override
    public void onNotificationPosted(StatusBarNotification sbn) {
        try {
            if (sbn == null || getPackageName().equals(sbn.getPackageName())) return;
            if (!Util.on(this, "notes")) return;
            Notification n = sbn.getNotification();
            if (n == null || (n.flags & Notification.FLAG_GROUP_SUMMARY) != 0) return;
            if ((n.flags & Notification.FLAG_ONGOING_EVENT) != 0) return;
            Bundle ex = n.extras;
            if (ex == null) return;
            CharSequence ti = ex.getCharSequence(Notification.EXTRA_TITLE);
            CharSequence tx = ex.getCharSequence(Notification.EXTRA_BIG_TEXT);
            if (tx == null) tx = ex.getCharSequence(Notification.EXTRA_TEXT);
            String title = ti == null ? "" : ti.toString();
            String text = tx == null ? "" : tx.toString();
            if (title.isEmpty() && text.isEmpty()) return;
            if (text.length() > 600) text = text.substring(0, 600);
            String app = label(sbn.getPackageName());
            long now = System.currentTimeMillis();
            JSONObject o = new JSONObject();
            o.put("k", sbn.getKey());
            o.put("pkg", sbn.getPackageName());
            o.put("app", app);
            o.put("title", title);
            o.put("text", text);
            o.put("t", sbn.getPostTime() > 0 ? sbn.getPostTime() : now);
            synchronized (LOCK) {
                JSONArray old = load(this), out = new JSONArray();
                for (int i = 0; i < old.length(); i++) {
                    JSONObject x = old.optJSONObject(i);
                    if (x == null) continue;
                    if (now - x.optLong("t") > KEEP_MS) continue;
                    if (sbn.getKey().equals(x.optString("k")) && title.equals(x.optString("title"))
                            && text.equals(x.optString("text"))) continue;
                    out.put(x);
                }
                out.put(o);
                JSONArray cut = new JSONArray();
                for (int i = Math.max(0, out.length() - KEEP); i < out.length(); i++) cut.put(out.get(i));
                Util.prefs(this).edit().putString("notes", cut.toString()).apply();
            }
            JSObject d = new JSObject();
            d.put("app", app);
            d.put("title", title);
            d.put("text", text);
            d.put("t", o.optLong("t"));
            MusaedPlugin.emit("note", d);
        } catch (Exception ignored) {
        }
    }

    private String label(String pkg) {
        try {
            PackageManager pm = getPackageManager();
            ApplicationInfo ai = pm.getApplicationInfo(pkg, 0);
            CharSequence l = pm.getApplicationLabel(ai);
            return l == null ? pkg : l.toString();
        } catch (Exception e) {
            return pkg;
        }
    }
}
