package com.passwordmanager;

import com.passwordmanager.service.DataStorageService;
import javafx.application.Platform;

import java.util.Timer;
import java.util.TimerTask;
import java.util.function.Consumer;

public class AppContext {
    private static AppContext instance;
    private DataStorageService dataStorageService;
    private javafx.stage.Stage primaryStage;

    private Timer autoLockTimer;
    private int autoLockTimeMinutes;
    private Consumer<Void> onLockCallback;
    private volatile long lastActivityTime;

    private AppContext() {
        this.dataStorageService = new DataStorageService();
        this.autoLockTimeMinutes = 5;
        this.lastActivityTime = System.currentTimeMillis();
    }

    public static AppContext getInstance() {
        if (instance == null) {
            instance = new AppContext();
        }
        return instance;
    }

    public DataStorageService getDataStorageService() {
        return dataStorageService;
    }

    public void setDataStorageService(DataStorageService dataStorageService) {
        this.dataStorageService = dataStorageService;
    }

    public javafx.stage.Stage getPrimaryStage() {
        return primaryStage;
    }

    public void setPrimaryStage(javafx.stage.Stage primaryStage) {
        this.primaryStage = primaryStage;
    }

    public int getAutoLockTimeMinutes() {
        return autoLockTimeMinutes;
    }

    public void setAutoLockTimeMinutes(int autoLockTimeMinutes) {
        this.autoLockTimeMinutes = autoLockTimeMinutes;
        if (dataStorageService.getAppData() != null && dataStorageService.getAppData().getSettings() != null) {
            dataStorageService.getAppData().getSettings().setAutoLockTimeMinutes(autoLockTimeMinutes);
        }
        resetAutoLockTimer();
    }

    public void setOnLockCallback(Consumer<Void> callback) {
        this.onLockCallback = callback;
    }

    public void updateUserActivity() {
        this.lastActivityTime = System.currentTimeMillis();
    }

    public void startAutoLockTimer() {
        stopAutoLockTimer();
        if (autoLockTimeMinutes > 0) {
            autoLockTimer = new Timer("AutoLockTimer", true);
            autoLockTimer.scheduleAtFixedRate(new TimerTask() {
                @Override
                public void run() {
                    long elapsed = System.currentTimeMillis() - lastActivityTime;
                    long timeout = autoLockTimeMinutes * 60 * 1000L;
                    if (elapsed >= timeout) {
                        lockApplication();
                    }
                }
            }, 1000, 1000);
        }
    }

    public void stopAutoLockTimer() {
        if (autoLockTimer != null) {
            autoLockTimer.cancel();
            autoLockTimer = null;
        }
    }

    public void resetAutoLockTimer() {
        updateUserActivity();
        if (autoLockTimer == null) {
            startAutoLockTimer();
        }
    }

    private void lockApplication() {
        stopAutoLockTimer();
        if (dataStorageService != null) {
            dataStorageService.lock();
        }
        if (onLockCallback != null) {
            Platform.runLater(() -> onLockCallback.accept(null));
        }
    }

    public long getRemainingLockTimeSeconds() {
        if (autoLockTimeMinutes <= 0) {
            return -1;
        }
        long elapsed = System.currentTimeMillis() - lastActivityTime;
        long timeout = autoLockTimeMinutes * 60 * 1000L;
        long remaining = timeout - elapsed;
        return Math.max(0, remaining / 1000);
    }
}
