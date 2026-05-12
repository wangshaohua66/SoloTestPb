package com.passwordmanager.model;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

public class AppData implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private UserSettings settings;
    private List<PasswordEntry> passwordEntries;
    private List<PasswordHistory> passwordHistories;

    public AppData() {
        this.settings = new UserSettings();
        this.passwordEntries = new ArrayList<>();
        this.passwordHistories = new ArrayList<>();
    }

    public UserSettings getSettings() {
        return settings;
    }

    public void setSettings(UserSettings settings) {
        this.settings = settings;
    }

    public List<PasswordEntry> getPasswordEntries() {
        return passwordEntries;
    }

    public void setPasswordEntries(List<PasswordEntry> passwordEntries) {
        this.passwordEntries = passwordEntries;
    }

    public List<PasswordHistory> getPasswordHistories() {
        return passwordHistories;
    }

    public void setPasswordHistories(List<PasswordHistory> passwordHistories) {
        this.passwordHistories = passwordHistories;
    }

    public void addPasswordEntry(PasswordEntry entry) {
        if (passwordEntries == null) {
            passwordEntries = new ArrayList<>();
        }
        passwordEntries.add(entry);
    }

    public void addPasswordHistory(PasswordHistory history) {
        if (passwordHistories == null) {
            passwordHistories = new ArrayList<>();
        }
        passwordHistories.add(history);
    }
}
