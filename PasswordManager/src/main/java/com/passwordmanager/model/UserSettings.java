package com.passwordmanager.model;

import java.io.Serializable;
import java.time.LocalDateTime;

public class UserSettings implements Serializable {
    private boolean isFirstTimeSetup;
    private String masterPasswordHash;
    private String salt;
    private int autoLockTimeMinutes;
    private int passwordGeneratorDefaultLength;
    private boolean includeUppercase;
    private boolean includeLowercase;
    private boolean includeNumbers;
    private boolean includeSymbols;
    private boolean excludeAmbiguous;
    private int clipboardClearDelaySeconds;
    private LocalDateTime lastMasterPasswordChange;
    private int masterPasswordExpiryDays;

    public UserSettings() {
        this.isFirstTimeSetup = true;
        this.autoLockTimeMinutes = 5;
        this.passwordGeneratorDefaultLength = 16;
        this.includeUppercase = true;
        this.includeLowercase = true;
        this.includeNumbers = true;
        this.includeSymbols = true;
        this.excludeAmbiguous = false;
        this.clipboardClearDelaySeconds = 30;
        this.masterPasswordExpiryDays = 90;
    }

    public boolean isFirstTimeSetup() {
        return isFirstTimeSetup;
    }

    public void setFirstTimeSetup(boolean firstTimeSetup) {
        isFirstTimeSetup = firstTimeSetup;
    }

    public String getMasterPasswordHash() {
        return masterPasswordHash;
    }

    public void setMasterPasswordHash(String masterPasswordHash) {
        this.masterPasswordHash = masterPasswordHash;
    }

    public String getSalt() {
        return salt;
    }

    public void setSalt(String salt) {
        this.salt = salt;
    }

    public int getAutoLockTimeMinutes() {
        return autoLockTimeMinutes;
    }

    public void setAutoLockTimeMinutes(int autoLockTimeMinutes) {
        this.autoLockTimeMinutes = autoLockTimeMinutes;
    }

    public int getPasswordGeneratorDefaultLength() {
        return passwordGeneratorDefaultLength;
    }

    public void setPasswordGeneratorDefaultLength(int passwordGeneratorDefaultLength) {
        this.passwordGeneratorDefaultLength = passwordGeneratorDefaultLength;
    }

    public boolean isIncludeUppercase() {
        return includeUppercase;
    }

    public void setIncludeUppercase(boolean includeUppercase) {
        this.includeUppercase = includeUppercase;
    }

    public boolean isIncludeLowercase() {
        return includeLowercase;
    }

    public void setIncludeLowercase(boolean includeLowercase) {
        this.includeLowercase = includeLowercase;
    }

    public boolean isIncludeNumbers() {
        return includeNumbers;
    }

    public void setIncludeNumbers(boolean includeNumbers) {
        this.includeNumbers = includeNumbers;
    }

    public boolean isIncludeSymbols() {
        return includeSymbols;
    }

    public void setIncludeSymbols(boolean includeSymbols) {
        this.includeSymbols = includeSymbols;
    }

    public boolean isExcludeAmbiguous() {
        return excludeAmbiguous;
    }

    public void setExcludeAmbiguous(boolean excludeAmbiguous) {
        this.excludeAmbiguous = excludeAmbiguous;
    }

    public int getClipboardClearDelaySeconds() {
        return clipboardClearDelaySeconds;
    }

    public void setClipboardClearDelaySeconds(int clipboardClearDelaySeconds) {
        this.clipboardClearDelaySeconds = clipboardClearDelaySeconds;
    }

    public LocalDateTime getLastMasterPasswordChange() {
        return lastMasterPasswordChange;
    }

    public void setLastMasterPasswordChange(LocalDateTime lastMasterPasswordChange) {
        this.lastMasterPasswordChange = lastMasterPasswordChange;
    }

    public int getMasterPasswordExpiryDays() {
        return masterPasswordExpiryDays;
    }

    public void setMasterPasswordExpiryDays(int masterPasswordExpiryDays) {
        this.masterPasswordExpiryDays = masterPasswordExpiryDays;
    }
}
