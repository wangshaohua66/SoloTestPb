package com.passwordmanager.util;

import java.awt.*;
import java.awt.datatransfer.Clipboard;
import java.awt.datatransfer.StringSelection;
import java.awt.datatransfer.Transferable;
import java.util.Timer;
import java.util.TimerTask;

public class ClipboardUtil {
    private static Timer clearTimer;
    private static int clearDelaySeconds = 30;

    public static void copyToClipboard(String text) {
        if (text == null || text.isEmpty()) {
            return;
        }

        try {
            Clipboard clipboard = Toolkit.getDefaultToolkit().getSystemClipboard();
            StringSelection stringSelection = new StringSelection(text);
            clipboard.setContents(stringSelection, stringSelection);

            scheduleClearClipboard();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static String getFromClipboard() {
        try {
            Clipboard clipboard = Toolkit.getDefaultToolkit().getSystemClipboard();
            Transferable contents = clipboard.getContents(null);
            if (contents != null && contents.isDataFlavorSupported(java.awt.datatransfer.DataFlavor.stringFlavor)) {
                return (String) contents.getTransferData(java.awt.datatransfer.DataFlavor.stringFlavor);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }

    public static void clearClipboard() {
        try {
            Clipboard clipboard = Toolkit.getDefaultToolkit().getSystemClipboard();
            StringSelection emptySelection = new StringSelection("");
            clipboard.setContents(emptySelection, emptySelection);
            cancelClearTimer();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void setClearDelaySeconds(int seconds) {
        if (seconds >= 0) {
            clearDelaySeconds = seconds;
        }
    }

    public static int getClearDelaySeconds() {
        return clearDelaySeconds;
    }

    private static void scheduleClearClipboard() {
        cancelClearTimer();

        if (clearDelaySeconds > 0) {
            clearTimer = new Timer(true);
            clearTimer.schedule(new TimerTask() {
                @Override
                public void run() {
                    clearClipboard();
                }
            }, clearDelaySeconds * 1000);
        }
    }

    private static void cancelClearTimer() {
        if (clearTimer != null) {
            clearTimer.cancel();
            clearTimer = null;
        }
    }
}
