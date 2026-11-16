package sa.musaed.app;

import android.content.Intent;
import android.os.Bundle;
import com.getcapacitor.BridgeActivity;
import com.getcapacitor.JSObject;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(MusaedPlugin.class);
        super.onCreate(savedInstanceState);
        try {
            getBridge().getWebView().getSettings().setMediaPlaybackRequiresUserGesture(false);
        } catch (Exception ignored) {
        }
        assist(getIntent());
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        assist(intent);
    }

    /** Opened from the side button / assistant gesture: tell the page to start listening. */
    private void assist(Intent i) {
        if (i == null || i.getAction() == null) return;
        String a = i.getAction();
        if (Intent.ACTION_ASSIST.equals(a) || Intent.ACTION_VOICE_COMMAND.equals(a)) {
            Util.assistAt = System.currentTimeMillis();
            MusaedPlugin.emit("assist", new JSObject());
        }
    }

    @Override
    public void onResume() {
        super.onResume();
        Util.foreground = true;
    }

    @Override
    public void onPause() {
        Util.foreground = false;
        super.onPause();
    }
}
