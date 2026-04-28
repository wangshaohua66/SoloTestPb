package com.passwordmanager.model;

import java.io.Serializable;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;

public class PasswordEntry implements Serializable, Cloneable {
    private String id;
    private String title;
    private String username;
    private String password;
    private String url;
    private String notes;
    private PasswordCategory category;
    private boolean isFavorite;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private LocalDateTime lastUsedAt;
    private int passwordHistoryCount;
    private LocalDate expiryDate;
    private boolean passwordExpiryEnabled;

    public PasswordEntry() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        this.isFavorite = false;
        this.category = PasswordCategory.OTHER;
        this.passwordExpiryEnabled = false;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getUrl() {
        return url;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    public String getNotes() {
        return notes;
    }

    public void setNotes(String notes) {
        this.notes = notes;
    }

    public PasswordCategory getCategory() {
        return category;
    }

    public void setCategory(PasswordCategory category) {
        this.category = category;
    }

    public boolean isFavorite() {
        return isFavorite;
    }

    public void setFavorite(boolean favorite) {
        isFavorite = favorite;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }

    public LocalDateTime getLastUsedAt() {
        return lastUsedAt;
    }

    public void setLastUsedAt(LocalDateTime lastUsedAt) {
        this.lastUsedAt = lastUsedAt;
    }

    public int getPasswordHistoryCount() {
        return passwordHistoryCount;
    }

    public void setPasswordHistoryCount(int passwordHistoryCount) {
        this.passwordHistoryCount = passwordHistoryCount;
    }

    public LocalDate getExpiryDate() {
        return expiryDate;
    }

    public void setExpiryDate(LocalDate expiryDate) {
        this.expiryDate = expiryDate;
    }

    public boolean isPasswordExpiryEnabled() {
        return passwordExpiryEnabled;
    }

    public void setPasswordExpiryEnabled(boolean passwordExpiryEnabled) {
        this.passwordExpiryEnabled = passwordExpiryEnabled;
    }

    public boolean isPasswordExpired() {
        if (!passwordExpiryEnabled || expiryDate == null) {
            return false;
        }
        return LocalDate.now().isAfter(expiryDate);
    }

    public boolean isPasswordExpiringSoon() {
        if (!passwordExpiryEnabled || expiryDate == null) {
            return false;
        }
        long daysUntilExpiry = ChronoUnit.DAYS.between(LocalDate.now(), expiryDate);
        return daysUntilExpiry <= 7 && daysUntilExpiry >= 0;
    }

    public long getDaysUntilExpiry() {
        if (!passwordExpiryEnabled || expiryDate == null) {
            return -1;
        }
        return ChronoUnit.DAYS.between(LocalDate.now(), expiryDate);
    }

    public void updateTimestamp() {
        this.updatedAt = LocalDateTime.now();
    }

    public void markAsUsed() {
        this.lastUsedAt = LocalDateTime.now();
    }

    @Override
    public PasswordEntry clone() {
        try {
            return (PasswordEntry) super.clone();
        } catch (CloneNotSupportedException e) {
            PasswordEntry entry = new PasswordEntry();
            entry.setId(this.id);
            entry.setTitle(this.title);
            entry.setUsername(this.username);
            entry.setPassword(this.password);
            entry.setUrl(this.url);
            entry.setNotes(this.notes);
            entry.setCategory(this.category);
            entry.setFavorite(this.isFavorite);
            entry.setCreatedAt(this.createdAt);
            entry.setUpdatedAt(this.updatedAt);
            entry.setLastUsedAt(this.lastUsedAt);
            entry.setPasswordHistoryCount(this.passwordHistoryCount);
            entry.setExpiryDate(this.expiryDate);
            entry.setPasswordExpiryEnabled(this.passwordExpiryEnabled);
            return entry;
        }
    }
}
