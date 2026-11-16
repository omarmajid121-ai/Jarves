package sa.musaed.app;

import android.Manifest;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.net.Uri;
import android.os.Build;
import android.provider.ContactsContract;
import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationManagerCompat;
import androidx.core.content.ContextCompat;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

final class Util {
    static volatile boolean foreground = false;
    static volatile long assistAt = 0;
    static final String PREFS = "musaed";
    static final String CH_CALLS = "calls";
    static final String CH_MONEY = "money";
    static final String CH_ALERTS = "alerts";

    private Util() {}

    static SharedPreferences prefs(Context c) {
        return c.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    static boolean on(Context c, String key) {
        return prefs(c).getBoolean("p_" + key, true);
    }

    static boolean granted(Context c, String perm) {
        return ContextCompat.checkSelfPermission(c, perm) == PackageManager.PERMISSION_GRANTED;
    }

    static void channels(Context c) {
        if (Build.VERSION.SDK_INT < 26) return;
        NotificationManager nm = c.getSystemService(NotificationManager.class);
        if (nm == null) return;
        NotificationChannel a = new NotificationChannel(CH_CALLS, "المكالمات", NotificationManager.IMPORTANCE_HIGH);
        a.setDescription("المكالمات الفائتة");
        NotificationChannel b = new NotificationChannel(CH_MONEY, "المصاريف", NotificationManager.IMPORTANCE_DEFAULT);
        b.setDescription("عمليات الشراء من رسائل البنك");
        NotificationChannel d = new NotificationChannel(CH_ALERTS, "تنبيهات مساعد", NotificationManager.IMPORTANCE_HIGH);
        d.setDescription("التذكيرات والتنبيهات المهمة");
        nm.createNotificationChannel(a);
        nm.createNotificationChannel(b);
        nm.createNotificationChannel(d);
    }

    static boolean canNotify(Context c) {
        if (Build.VERSION.SDK_INT >= 33 && !granted(c, Manifest.permission.POST_NOTIFICATIONS)) return false;
        return NotificationManagerCompat.from(c).areNotificationsEnabled();
    }

    static void post(Context c, String channel, int id, String title, String body) {
        try {
            channels(c);
            if (!canNotify(c)) return;
            Intent open = new Intent(c, MainActivity.class);
            open.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            PendingIntent pi = PendingIntent.getActivity(c, id, open,
                    PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
            NotificationCompat.Builder nb = new NotificationCompat.Builder(c, channel)
                    .setSmallIcon(R.drawable.ic_stat_musaed)
                    .setColor(0xFF5FE4FF)
                    .setContentTitle(title)
                    .setContentText(body)
                    .setStyle(new NotificationCompat.BigTextStyle().bigText(body))
                    .setAutoCancel(true)
                    .setContentIntent(pi)
                    .setPriority(CH_MONEY.equals(channel) ? NotificationCompat.PRIORITY_DEFAULT : NotificationCompat.PRIORITY_HIGH);
            NotificationManagerCompat.from(c).notify(id, nb.build());
        } catch (SecurityException ignored) {
        } catch (Exception ignored) {
        }
    }

    /** Arabic-aware text folding for matching names. */
    static String fold(String s) {
        if (s == null) return "";
        StringBuilder b = new StringBuilder(s.length());
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (ch >= 'ً' && ch <= 'ٟ') continue; // harakat
            if (ch == 'ـ') continue; // tatweel
            switch (ch) {
                case 'أ': case 'إ': case 'آ': case 'ٱ': ch = 'ا'; break;
                case 'ة': ch = 'ه'; break;
                case 'ى': ch = 'ي'; break;
                case 'ؤ': ch = 'و'; break;
                case 'ئ': ch = 'ي'; break;
                default: break;
            }
            if (ch >= '٠' && ch <= '٩') ch = (char) ('0' + (ch - '٠'));
            b.append(ch);
        }
        return b.toString().toLowerCase(Locale.ROOT).trim();
    }

    static String digits(String s) {
        if (s == null) return "";
        StringBuilder b = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            if (ch >= '٠' && ch <= '٩') ch = (char) ('0' + (ch - '٠'));
            if (ch >= '0' && ch <= '9') b.append(ch);
        }
        return b.toString();
    }

    /** Last 9 digits, enough to match Saudi numbers written with or without 966 / 0. */
    static String tail(String s) {
        String d = digits(s);
        return d.length() > 9 ? d.substring(d.length() - 9) : d;
    }

    static String contactName(Context c, String number) {
        if (number == null || number.isEmpty() || !granted(c, Manifest.permission.READ_CONTACTS)) return "";
        try (Cursor cur = c.getContentResolver().query(
                Uri.withAppendedPath(ContactsContract.PhoneLookup.CONTENT_FILTER_URI, Uri.encode(number)),
                new String[]{ContactsContract.PhoneLookup.DISPLAY_NAME}, null, null, null)) {
            if (cur != null && cur.moveToFirst()) {
                String n = cur.getString(0);
                return n == null ? "" : n;
            }
        } catch (Exception ignored) {
        }
        return "";
    }

    private static final Pattern AMT = Pattern.compile(
            "(?:SAR|SR|ر\\.?\\s?س|ريال)\\s*:?\\s*([0-9][0-9,]*(?:\\.[0-9]{1,2})?)|([0-9][0-9,]*(?:\\.[0-9]{1,2})?)\\s*(?:SAR|SR|ر\\.?\\s?س|ريال)",
            Pattern.CASE_INSENSITIVE);
    private static final Pattern SPEND = Pattern.compile(
            "شراء|مشتريات|مدي|خصم|سحب|دفع|سداد|purchase|\\bpos\\b|debit|withdraw|payment|paid|apple ?pay",
            Pattern.CASE_INSENSITIVE);
    private static final Pattern SKIP = Pattern.compile(
            "رمز|كلمه المرور|otp|code|ايداع|وارد|راتب|credited|deposit|refund|استرداد|مرفوض|declined|رفض",
            Pattern.CASE_INSENSITIVE);

    // Patterns are written in folded form (see fold): ة→ه, ى→ي, أ/إ→ا.
    /** Returns the amount text when an SMS looks like a purchase or withdrawal, otherwise null. */
    static String spendAmount(String body) {
        if (body == null) return null;
        String t = fold(body);
        if (!SPEND.matcher(t).find() || SKIP.matcher(t).find()) return null;
        Matcher m = AMT.matcher(t);
        if (!m.find()) return null;
        String a = m.group(1) != null ? m.group(1) : m.group(2);
        return a == null ? null : a.replace(",", "");
    }
}
