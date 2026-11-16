package sa.musaed.app;

import android.Manifest;
import android.app.AlarmManager;
import android.app.role.RoleManager;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.database.Cursor;
import android.net.Uri;
import android.os.Build;
import android.os.PowerManager;
import android.provider.CallLog;
import android.provider.ContactsContract;
import android.provider.Settings;
import androidx.core.app.NotificationManagerCompat;
import com.getcapacitor.JSArray;
import com.getcapacitor.JSObject;
import com.getcapacitor.PermissionState;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.getcapacitor.annotation.Permission;
import com.getcapacitor.annotation.PermissionCallback;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Set;
import org.json.JSONArray;
import org.json.JSONObject;

@CapacitorPlugin(
        name = "Musaed",
        permissions = {
                @Permission(alias = "sms", strings = {Manifest.permission.READ_SMS, Manifest.permission.RECEIVE_SMS}),
                @Permission(alias = "calls", strings = {Manifest.permission.READ_CALL_LOG, Manifest.permission.READ_PHONE_STATE}),
                @Permission(alias = "contacts", strings = {Manifest.permission.READ_CONTACTS}),
                @Permission(alias = "dial", strings = {Manifest.permission.CALL_PHONE}),
                @Permission(alias = "mic", strings = {Manifest.permission.RECORD_AUDIO}),
                @Permission(alias = "loc", strings = {Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION}),
                @Permission(alias = "camera", strings = {Manifest.permission.CAMERA}),
                @Permission(alias = "notify", strings = {"android.permission.POST_NOTIFICATIONS"})
        })
public class MusaedPlugin extends Plugin {
    private static volatile MusaedPlugin inst;
    private static final String[] RUNTIME = {"sms", "calls", "contacts", "dial", "mic", "loc", "camera"};

    @Override
    public void load() {
        inst = this;
        Util.channels(getContext());
    }

    @Override
    protected void handleOnDestroy() {
        if (inst == this) inst = null;
        super.handleOnDestroy();
    }

    static void emit(String event, JSObject data) {
        MusaedPlugin p = inst;
        if (p != null) {
            try {
                p.notifyListeners(event, data);
            } catch (Exception ignored) {
            }
        }
    }

    private String ps(String alias) {
        PermissionState s = getPermissionState(alias);
        if (s == PermissionState.GRANTED) return "granted";
        if (s == PermissionState.DENIED) return "denied";
        return "prompt";
    }

    private boolean ok(String alias) {
        return getPermissionState(alias) == PermissionState.GRANTED;
    }

    private String notifyState() {
        Context c = getContext();
        if (Build.VERSION.SDK_INT >= 33) {
            String s = ps("notify");
            if (!"granted".equals(s)) return s;
        }
        return NotificationManagerCompat.from(c).areNotificationsEnabled() ? "granted" : "off";
    }

    private boolean listenerOn() {
        Context c = getContext();
        return NotificationManagerCompat.getEnabledListenerPackages(c).contains(c.getPackageName());
    }

    private boolean batteryFree() {
        PowerManager pm = (PowerManager) getContext().getSystemService(Context.POWER_SERVICE);
        return pm != null && pm.isIgnoringBatteryOptimizations(getContext().getPackageName());
    }

    private boolean exactOk() {
        if (Build.VERSION.SDK_INT < 31) return true;
        AlarmManager am = (AlarmManager) getContext().getSystemService(Context.ALARM_SERVICE);
        return am != null && am.canScheduleExactAlarms();
    }

    private boolean assistantOn() {
        if (Build.VERSION.SDK_INT < 29) return false;
        try {
            RoleManager rm = getContext().getSystemService(RoleManager.class);
            return rm != null && rm.isRoleHeld(RoleManager.ROLE_ASSISTANT);
        } catch (Exception e) {
            return false;
        }
    }

    @PluginMethod
    public void launch(PluginCall call) {
        JSObject o = new JSObject();
        long at = Util.assistAt;
        o.put("assist", at > 0 && System.currentTimeMillis() - at < 20000);
        Util.assistAt = 0;
        call.resolve(o);
    }

    private JSObject states() {
        JSObject o = new JSObject();
        for (String a : RUNTIME) o.put(a, ps(a));
        o.put("notify", notifyState());
        o.put("listener", listenerOn() ? "granted" : "off");
        o.put("battery", batteryFree() ? "granted" : "off");
        o.put("exact", exactOk() ? "granted" : "off");
        o.put("assistant", assistantOn() ? "granted" : "off");
        return o;
    }

    @PluginMethod
    public void info(PluginCall call) {
        JSObject o = new JSObject();
        o.put("version", BuildConfig.VERSION_NAME);
        o.put("build", BuildConfig.VERSION_CODE);
        o.put("sdk", Build.VERSION.SDK_INT);
        o.put("model", Build.MANUFACTURER + " " + Build.MODEL);
        o.put("perms", states());
        SharedPreferences sp = Util.prefs(getContext());
        JSObject pr = new JSObject();
        for (String k : new String[]{"missed", "bank", "notes"}) pr.put(k, sp.getBoolean("p_" + k, true));
        o.put("prefs", pr);
        call.resolve(o);
    }

    @PluginMethod
    public void state(PluginCall call) {
        call.resolve(states());
    }

    private void open(Intent i) {
        i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        try {
            getContext().startActivity(i);
        } catch (Exception e) {
            Intent a = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.parse("package:" + getContext().getPackageName()));
            a.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            try {
                getContext().startActivity(a);
            } catch (Exception ignored) {
            }
        }
    }

    private void appSettings() {
        open(new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, Uri.parse("package:" + getContext().getPackageName())));
    }

    @PluginMethod
    public void ask(PluginCall call) {
        String n = call.getString("name", "");
        String pkg = getContext().getPackageName();
        JSObject r = new JSObject();
        switch (n) {
            case "listener":
                open(new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS));
                r.put("state", "settings");
                call.resolve(r);
                return;
            case "battery":
                if (batteryFree()) {
                    r.put("state", "granted");
                } else {
                    open(new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS, Uri.parse("package:" + pkg)));
                    r.put("state", "settings");
                }
                call.resolve(r);
                return;
            case "exact":
                if (Build.VERSION.SDK_INT >= 31 && !exactOk()) {
                    open(new Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM, Uri.parse("package:" + pkg)));
                    r.put("state", "settings");
                } else {
                    r.put("state", "granted");
                }
                call.resolve(r);
                return;
            case "assistant":
                if (assistantOn()) {
                    r.put("state", "granted");
                } else {
                    open(new Intent(Settings.ACTION_MANAGE_DEFAULT_APPS_SETTINGS));
                    r.put("state", "settings");
                }
                call.resolve(r);
                return;
            case "app":
                appSettings();
                r.put("state", "settings");
                call.resolve(r);
                return;
            case "notify":
                if (Build.VERSION.SDK_INT < 33 || ok("notify")) {
                    if (!NotificationManagerCompat.from(getContext()).areNotificationsEnabled()) {
                        Intent i = new Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS);
                        i.putExtra(Settings.EXTRA_APP_PACKAGE, pkg);
                        open(i);
                        r.put("state", "settings");
                    } else {
                        r.put("state", "granted");
                    }
                    call.resolve(r);
                    return;
                }
                break;
            default:
                break;
        }
        boolean known = "notify".equals(n);
        for (String a : RUNTIME) if (a.equals(n)) known = true;
        if (!known) {
            call.reject("unknown permission", "bad_name");
            return;
        }
        if (ok(n)) {
            r.put("state", "granted");
            call.resolve(r);
            return;
        }
        if (getPermissionState(n) == PermissionState.DENIED) {
            appSettings();
            r.put("state", "settings");
            call.resolve(r);
            return;
        }
        requestPermissionForAlias(n, call, "askDone");
    }

    @PermissionCallback
    private void askDone(PluginCall call) {
        JSObject r = new JSObject();
        r.put("state", ps(call.getString("name", "")));
        call.resolve(r);
    }

    @PluginMethod
    public void setPrefs(PluginCall call) {
        SharedPreferences.Editor ed = Util.prefs(getContext()).edit();
        for (String k : new String[]{"missed", "bank", "notes"}) {
            Boolean v = call.getBoolean(k, null);
            if (v != null) ed.putBoolean("p_" + k, v);
        }
        if (Boolean.FALSE.equals(call.getBoolean("notes", null))) ed.remove("notes");
        ed.apply();
        call.resolve();
    }

    private static int clamp(Integer v, int lo, int hi, int def) {
        int x = v == null ? def : v;
        return Math.max(lo, Math.min(hi, x));
    }

    @PluginMethod
    public void sms(PluginCall call) {
        if (!ok("sms")) {
            call.reject("SMS permission is off", "no_permission");
            return;
        }
        long since = call.getLong("since", 0L);
        int limit = clamp(call.getInt("limit"), 1, 500, 40);
        String q = Util.fold(call.getString("query", ""));
        String box = "sent".equals(call.getString("box")) ? "sent" : "inbox";
        Map<String, String> names = new LinkedHashMap<>();
        JSArray out = new JSArray();
        int scanned = 0;
        try (Cursor c = getContext().getContentResolver().query(Uri.parse("content://sms/" + box),
                new String[]{"_id", "address", "body", "date"}, "date>?", new String[]{String.valueOf(since)}, "date DESC")) {
            while (c != null && c.moveToNext() && out.length() < limit && scanned < 8000) {
                scanned++;
                String addr = c.getString(1) == null ? "" : c.getString(1);
                String body = c.getString(2) == null ? "" : c.getString(2);
                String name = names.get(addr);
                if (name == null) {
                    name = Util.contactName(getContext(), addr);
                    names.put(addr, name);
                }
                if (!q.isEmpty() && !Util.fold(addr + " " + name + " " + body).contains(q)) continue;
                JSObject o = new JSObject();
                o.put("id", c.getLong(0));
                o.put("from", addr);
                o.put("name", name);
                o.put("text", body.length() > 1200 ? body.substring(0, 1200) : body);
                o.put("t", c.getLong(3));
                o.put("spend", Util.spendAmount(body) != null);
                out.put(o);
            }
        } catch (Exception e) {
            call.reject("Could not read messages", "read_failed");
            return;
        }
        JSObject r = new JSObject();
        r.put("items", out);
        r.put("scanned", scanned);
        call.resolve(r);
    }

    private static String callType(int t) {
        switch (t) {
            case CallLog.Calls.INCOMING_TYPE: return "incoming";
            case CallLog.Calls.OUTGOING_TYPE: return "outgoing";
            case CallLog.Calls.MISSED_TYPE: return "missed";
            case CallLog.Calls.REJECTED_TYPE: return "rejected";
            case CallLog.Calls.BLOCKED_TYPE: return "blocked";
            case CallLog.Calls.VOICEMAIL_TYPE: return "voicemail";
            default: return "other";
        }
    }

    @PluginMethod
    public void calls(PluginCall call) {
        if (!ok("calls")) {
            call.reject("Call log permission is off", "no_permission");
            return;
        }
        long since = call.getLong("since", 0L);
        int limit = clamp(call.getInt("limit"), 1, 300, 20);
        String type = call.getString("type", "all");
        String q = Util.fold(call.getString("query", ""));
        String qd = Util.tail(q);
        JSArray out = new JSArray();
        int scanned = 0;
        try (Cursor c = getContext().getContentResolver().query(CallLog.Calls.CONTENT_URI,
                new String[]{CallLog.Calls.NUMBER, CallLog.Calls.CACHED_NAME, CallLog.Calls.TYPE, CallLog.Calls.DATE, CallLog.Calls.DURATION},
                CallLog.Calls.DATE + ">?", new String[]{String.valueOf(since)}, CallLog.Calls.DATE + " DESC")) {
            while (c != null && c.moveToNext() && out.length() < limit && scanned < 5000) {
                scanned++;
                String num = c.getString(0) == null ? "" : c.getString(0);
                String name = c.getString(1);
                if (name == null || name.isEmpty()) name = Util.contactName(getContext(), num);
                String ty = callType(c.getInt(2));
                if (!"all".equals(type) && !type.equals(ty)) continue;
                if (!q.isEmpty()) {
                    boolean hit = Util.fold(name).contains(q) || (qd.length() >= 6 && Util.tail(num).equals(qd));
                    if (!hit) continue;
                }
                JSObject o = new JSObject();
                o.put("number", num);
                o.put("name", name);
                o.put("type", ty);
                o.put("t", c.getLong(3));
                o.put("secs", c.getLong(4));
                out.put(o);
            }
        } catch (Exception e) {
            call.reject("Could not read the call log", "read_failed");
            return;
        }
        JSObject r = new JSObject();
        r.put("items", out);
        call.resolve(r);
    }

    @PluginMethod
    public void contacts(PluginCall call) {
        if (!ok("contacts")) {
            call.reject("Contacts permission is off", "no_permission");
            return;
        }
        String q = Util.fold(call.getString("query", ""));
        int limit = clamp(call.getInt("limit"), 1, 50, 8);
        String[] words = q.isEmpty() ? new String[0] : q.split("\\s+");
        String qd = Util.tail(q);
        Map<String, Set<String>> found = new LinkedHashMap<>();
        Map<String, Set<String>> tails = new LinkedHashMap<>();
        try (Cursor c = getContext().getContentResolver().query(ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                new String[]{ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME, ContactsContract.CommonDataKinds.Phone.NUMBER},
                null, null, ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME + " ASC")) {
            int scanned = 0;
            while (c != null && c.moveToNext() && scanned < 20000) {
                scanned++;
                String name = c.getString(0) == null ? "" : c.getString(0);
                String num = c.getString(1) == null ? "" : c.getString(1);
                String fn = Util.fold(name);
                boolean hit = words.length > 0;
                for (String w : words) if (!fn.contains(w)) { hit = false; break; }
                if (!hit && qd.length() >= 6 && Util.tail(num).equals(qd)) hit = true;
                if (!hit) continue;
                if (!found.containsKey(name)) {
                    if (found.size() >= limit) continue;
                    found.put(name, new LinkedHashSet<>());
                    tails.put(name, new LinkedHashSet<>());
                }
                if (tails.get(name).add(Util.tail(num))) found.get(name).add(num.replaceAll("[^0-9+]", ""));
            }
        } catch (Exception e) {
            call.reject("Could not read contacts", "read_failed");
            return;
        }
        JSArray out = new JSArray();
        for (Map.Entry<String, Set<String>> e : found.entrySet()) {
            JSObject o = new JSObject();
            o.put("name", e.getKey());
            JSArray ph = new JSArray();
            for (String p : e.getValue()) ph.put(p);
            o.put("phones", ph);
            out.put(o);
        }
        JSObject r = new JSObject();
        r.put("items", out);
        call.resolve(r);
    }

    @PluginMethod
    public void dial(PluginCall call) {
        String n = call.getString("number", "");
        n = n == null ? "" : n.replaceAll("[^0-9+*#]", "");
        if (n.isEmpty()) {
            call.reject("number is required", "bad_number");
            return;
        }
        boolean direct = Boolean.TRUE.equals(call.getBoolean("direct", false));
        if (direct && !ok("dial")) {
            requestPermissionForAlias("dial", call, "dialDone");
            return;
        }
        place(call, n, direct);
    }

    @PermissionCallback
    private void dialDone(PluginCall call) {
        String n = call.getString("number", "");
        place(call, n == null ? "" : n.replaceAll("[^0-9+*#]", ""), ok("dial"));
    }

    private void place(PluginCall call, String n, boolean direct) {
        Intent i = new Intent(direct ? Intent.ACTION_CALL : Intent.ACTION_DIAL, Uri.parse("tel:" + Uri.encode(n)));
        i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        try {
            getContext().startActivity(i);
            JSObject r = new JSObject();
            r.put("mode", direct ? "calling" : "dialer");
            call.resolve(r);
        } catch (Exception e) {
            call.reject("Could not open the phone app", "dial_failed");
        }
    }

    @PluginMethod
    public void notes(PluginCall call) {
        if (!listenerOn()) {
            call.reject("Notification access is off", "no_permission");
            return;
        }
        long since = call.getLong("since", 0L);
        int limit = clamp(call.getInt("limit"), 1, 300, 20);
        String app = Util.fold(call.getString("app", ""));
        String q = Util.fold(call.getString("query", ""));
        JSONArray all = NoteListener.load(getContext());
        JSArray out = new JSArray();
        for (int i = all.length() - 1; i >= 0 && out.length() < limit; i--) {
            JSONObject x = all.optJSONObject(i);
            if (x == null || x.optLong("t") <= since) continue;
            if (!app.isEmpty() && !Util.fold(x.optString("app") + " " + x.optString("pkg")).contains(app)) continue;
            if (!q.isEmpty() && !Util.fold(x.optString("title") + " " + x.optString("text")).contains(q)) continue;
            JSObject o = new JSObject();
            Iterator<String> it = x.keys();
            while (it.hasNext()) {
                String k = it.next();
                if (!"k".equals(k)) o.put(k, x.opt(k));
            }
            out.put(o);
        }
        JSObject r = new JSObject();
        r.put("items", out);
        call.resolve(r);
    }

    @PluginMethod
    public void clearNotes(PluginCall call) {
        NoteListener.clear(getContext());
        call.resolve();
    }
}
