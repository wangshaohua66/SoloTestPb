package com.passwordmanager.service;

import com.passwordmanager.model.AppData;
import com.passwordmanager.model.PasswordEntry;
import com.passwordmanager.model.PasswordHistory;
import com.passwordmanager.model.UserSettings;
import com.passwordmanager.util.CryptoUtil;
import com.passwordmanager.util.JsonUtil;
import com.passwordmanager.util.KeyDerivationUtil;

import javax.crypto.SecretKey;
import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

public class DataStorageService {
    private static final String DATA_DIRECTORY = System.getProperty("user.home") + File.separator + ".passwordmanager";
    private static final String DATA_FILE = "data.enc";
    private static final String METADATA_FILE = "meta.dat";
    private static final String BACKUP_DIRECTORY = "backups";
    private static final String EXPORT_FILE_NAME = "passwords_export.json";

    private AppData appData;
    private MetaData metaData;
    private SecretKey encryptionKey;
    private boolean isLocked = true;

    public DataStorageService() {
        ensureDataDirectoryExists();
    }

    private void ensureDataDirectoryExists() {
        File dataDir = new File(DATA_DIRECTORY);
        if (!dataDir.exists()) {
            dataDir.mkdirs();
        }
        File backupDir = new File(DATA_DIRECTORY + File.separator + BACKUP_DIRECTORY);
        if (!backupDir.exists()) {
            backupDir.mkdirs();
        }
    }

    public boolean isFirstTimeSetup() {
        File dataFile = new File(DATA_DIRECTORY + File.separator + DATA_FILE);
        return !dataFile.exists();
    }

    public boolean createMasterPassword(char[] masterPassword) throws Exception {
        if (!isFirstTimeSetup()) {
            return false;
        }

        String salt = KeyDerivationUtil.generateSaltAsString();
        String passwordHash = KeyDerivationUtil.deriveKeyAsString(masterPassword, salt);

        this.metaData = new MetaData(salt, passwordHash);
        this.encryptionKey = CryptoUtil.deriveSecretKey(masterPassword, java.util.Base64.getDecoder().decode(salt));

        AppData newAppData = new AppData();
        UserSettings settings = newAppData.getSettings();
        settings.setFirstTimeSetup(false);
        settings.setMasterPasswordHash(passwordHash);
        settings.setSalt(salt);
        settings.setLastMasterPasswordChange(LocalDateTime.now());

        this.appData = newAppData;
        this.isLocked = false;

        saveMetaData();
        saveData();

        return true;
    }

    private void saveMetaData() throws Exception {
        if (metaData == null) {
            return;
        }
        metaData.setLastModifiedTimestamp(System.currentTimeMillis());
        File metaFile = new File(DATA_DIRECTORY + File.separator + METADATA_FILE);
        String json = JsonUtil.toJson(metaData);
        try (FileWriter writer = new FileWriter(metaFile)) {
            writer.write(json);
        }
    }

    private MetaData loadMetaData() throws Exception {
        File metaFile = new File(DATA_DIRECTORY + File.separator + METADATA_FILE);
        if (!metaFile.exists()) {
            return null;
        }
        StringBuilder jsonData = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new FileReader(metaFile))) {
            String line;
            while ((line = reader.readLine()) != null) {
                jsonData.append(line);
            }
        }
        return JsonUtil.fromJson(jsonData.toString(), MetaData.class);
    }

    public boolean verifyMasterPassword(char[] masterPassword) throws Exception {
        if (isFirstTimeSetup()) {
            return false;
        }

        this.metaData = loadMetaData();
        if (metaData == null || metaData.getSalt() == null || metaData.getPasswordHash() == null) {
            return false;
        }

        boolean verified = KeyDerivationUtil.verifyPassword(masterPassword, metaData.getSalt(), metaData.getPasswordHash());

        if (verified) {
            this.encryptionKey = CryptoUtil.deriveSecretKey(masterPassword, java.util.Base64.getDecoder().decode(metaData.getSalt()));
            loadData();
            this.isLocked = false;
        }

        return verified;
    }

    public void lock() {
        this.isLocked = true;
        this.encryptionKey = null;
        this.appData = null;
    }

    public void unlock(SecretKey key) {
        this.encryptionKey = key;
        this.isLocked = false;
    }

    public boolean isLocked() {
        return isLocked;
    }

    public AppData getAppData() {
        return appData;
    }

    public void setAppData(AppData appData) {
        this.appData = appData;
    }

    public void saveData() throws Exception {
        if (isLocked || encryptionKey == null || appData == null) {
            throw new IllegalStateException("应用已锁定或数据未加载");
        }

        String jsonData = JsonUtil.toJson(appData);
        String encryptedData = CryptoUtil.encrypt(jsonData, encryptionKey);

        File dataFile = new File(DATA_DIRECTORY + File.separator + DATA_FILE);
        try (FileWriter writer = new FileWriter(dataFile)) {
            writer.write(encryptedData);
        }
    }

    public void loadData() throws Exception {
        if (isLocked || encryptionKey == null) {
            throw new IllegalStateException("应用已锁定");
        }

        File dataFile = new File(DATA_DIRECTORY + File.separator + DATA_FILE);
        if (!dataFile.exists()) {
            this.appData = new AppData();
            return;
        }

        String encryptedData = readEncryptedData();
        String jsonData = CryptoUtil.decrypt(encryptedData, encryptionKey);
        this.appData = JsonUtil.fromJson(jsonData, AppData.class);
    }

    private String readEncryptedData() throws IOException {
        File dataFile = new File(DATA_DIRECTORY + File.separator + DATA_FILE);
        try (BufferedReader reader = new BufferedReader(new FileReader(dataFile))) {
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                sb.append(line);
            }
            return sb.toString();
        }
    }

    public String createBackup() throws Exception {
        if (isLocked) {
            throw new IllegalStateException("应用已锁定");
        }

        LocalDateTime now = LocalDateTime.now();
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss");
        String timestamp = now.format(formatter);

        String backupFileName = "backup_" + timestamp + ".enc";
        Path sourcePath = Paths.get(DATA_DIRECTORY, DATA_FILE);
        Path backupPath = Paths.get(DATA_DIRECTORY, BACKUP_DIRECTORY, backupFileName);

        Files.copy(sourcePath, backupPath, StandardCopyOption.REPLACE_EXISTING);

        return backupPath.toString();
    }

    public boolean restoreFromBackup(String backupFilePath) throws Exception {
        File backupFile = new File(backupFilePath);
        if (!backupFile.exists()) {
            return false;
        }

        Path backupPath = Paths.get(backupFilePath);
        Path dataPath = Paths.get(DATA_DIRECTORY, DATA_FILE);

        Files.copy(backupPath, dataPath, StandardCopyOption.REPLACE_EXISTING);

        return true;
    }

    public List<File> listBackups() {
        File backupDir = new File(DATA_DIRECTORY + File.separator + BACKUP_DIRECTORY);
        File[] files = backupDir.listFiles((dir, name) -> name.startsWith("backup_") && name.endsWith(".enc"));
        if (files == null) {
            return new ArrayList<>();
        }
        java.util.Arrays.sort(files, (f1, f2) -> Long.compare(f2.lastModified(), f1.lastModified()));
        return java.util.Arrays.asList(files);
    }

    public String exportData() throws Exception {
        if (isLocked || appData == null) {
            throw new IllegalStateException("应用已锁定或数据未加载");
        }

        return JsonUtil.toJson(appData.getPasswordEntries());
    }

    public void exportToFile(String filePath) throws Exception {
        if (isLocked || appData == null) {
            throw new IllegalStateException("应用已锁定或数据未加载");
        }

        String jsonData = JsonUtil.toJson(appData.getPasswordEntries());
        try (FileWriter writer = new FileWriter(filePath)) {
            writer.write(jsonData);
        }
    }

    public int importData(String jsonData) throws Exception {
        if (isLocked || appData == null) {
            throw new IllegalStateException("应用已锁定或数据未加载");
        }

        List<PasswordEntry> importedEntries = JsonUtil.fromJson(jsonData, new com.fasterxml.jackson.core.type.TypeReference<List<PasswordEntry>>() {});

        if (importedEntries == null || importedEntries.isEmpty()) {
            return 0;
        }

        for (PasswordEntry entry : importedEntries) {
            if (entry.getId() == null || entry.getId().isEmpty()) {
                entry.setId(com.passwordmanager.util.IdGenerator.generatePasswordEntryId());
            }
            appData.addPasswordEntry(entry);
        }

        saveData();

        return importedEntries.size();
    }

    public int importFromFile(String filePath) throws Exception {
        File importFile = new File(filePath);
        if (!importFile.exists()) {
            throw new FileNotFoundException("导入文件不存在: " + filePath);
        }

        StringBuilder jsonData = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new FileReader(importFile))) {
            String line;
            while ((line = reader.readLine()) != null) {
                jsonData.append(line);
            }
        }

        return importData(jsonData.toString());
    }

    public void addPasswordEntry(PasswordEntry entry) throws Exception {
        if (isLocked || appData == null) {
            throw new IllegalStateException("应用已锁定或数据未加载");
        }

        if (entry.getId() == null || entry.getId().isEmpty()) {
            entry.setId(com.passwordmanager.util.IdGenerator.generatePasswordEntryId());
        }

        appData.addPasswordEntry(entry);
        saveData();
    }

    public void updatePasswordEntry(PasswordEntry entry, String oldPassword) throws Exception {
        if (isLocked || appData == null) {
            throw new IllegalStateException("应用已锁定或数据未加载");
        }

        List<PasswordEntry> entries = appData.getPasswordEntries();
        for (int i = 0; i < entries.size(); i++) {
            if (entries.get(i).getId().equals(entry.getId())) {
                if (oldPassword != null && !oldPassword.equals(entry.getPassword())) {
                    addPasswordHistory(entry.getId(), oldPassword);
                    int newCount = entries.get(i).getPasswordHistoryCount() + 1;
                    entry.setPasswordHistoryCount(newCount);
                }
                entry.updateTimestamp();
                entries.set(i, entry);
                saveData();
                return;
            }
        }

        throw new IllegalArgumentException("密码记录不存在");
    }

    public List<PasswordHistory> getPasswordHistoriesByEntryId(String entryId) {
        return getPasswordHistory(entryId);
    }

    public void deletePasswordEntry(String entryId) throws Exception {
        if (isLocked || appData == null) {
            throw new IllegalStateException("应用已锁定或数据未加载");
        }

        List<PasswordEntry> entries = appData.getPasswordEntries();
        entries.removeIf(entry -> entry.getId().equals(entryId));
        saveData();
    }

    public List<PasswordEntry> searchPasswords(String keyword) {
        if (isLocked || appData == null) {
            return new ArrayList<>();
        }

        List<PasswordEntry> results = new ArrayList<>();
        String lowerKeyword = keyword.toLowerCase();

        for (PasswordEntry entry : appData.getPasswordEntries()) {
            if (entry.getTitle() != null && entry.getTitle().toLowerCase().contains(lowerKeyword)) {
                results.add(entry);
            } else if (entry.getUsername() != null && entry.getUsername().toLowerCase().contains(lowerKeyword)) {
                results.add(entry);
            } else if (entry.getUrl() != null && entry.getUrl().toLowerCase().contains(lowerKeyword)) {
                results.add(entry);
            } else if (entry.getNotes() != null && entry.getNotes().toLowerCase().contains(lowerKeyword)) {
                results.add(entry);
            }
        }

        return results;
    }

    public List<PasswordEntry> getPasswordsByCategory(com.passwordmanager.model.PasswordCategory category) {
        if (isLocked || appData == null) {
            return new ArrayList<>();
        }

        List<PasswordEntry> results = new ArrayList<>();
        for (PasswordEntry entry : appData.getPasswordEntries()) {
            if (entry.getCategory() == category) {
                results.add(entry);
            }
        }
        return results;
    }

    public List<PasswordEntry> getFavoritePasswords() {
        if (isLocked || appData == null) {
            return new ArrayList<>();
        }

        List<PasswordEntry> results = new ArrayList<>();
        for (PasswordEntry entry : appData.getPasswordEntries()) {
            if (entry.isFavorite()) {
                results.add(entry);
            }
        }
        return results;
    }

    public void addPasswordHistory(String entryId, String oldPassword) throws Exception {
        addPasswordHistory(entryId, oldPassword, com.passwordmanager.model.PasswordHistory.ActionType.UPDATE);
    }

    public void addPasswordHistory(String entryId, String oldPassword, com.passwordmanager.model.PasswordHistory.ActionType actionType) throws Exception {
        if (isLocked || appData == null) {
            throw new IllegalStateException("应用已锁定或数据未加载");
        }

        PasswordHistory history = new PasswordHistory(entryId, oldPassword, actionType);
        history.setId(com.passwordmanager.util.IdGenerator.generateHistoryId());
        appData.addPasswordHistory(history);
        saveData();
    }

    public List<PasswordHistory> getPasswordHistory(String entryId) {
        if (isLocked || appData == null) {
            return new ArrayList<>();
        }

        List<PasswordHistory> results = new ArrayList<>();
        for (PasswordHistory history : appData.getPasswordHistories()) {
            if (history.getEntryId().equals(entryId)) {
                results.add(history);
            }
        }
        results.sort((h1, h2) -> h2.getChangedAt().compareTo(h1.getChangedAt()));
        return results;
    }

    public void changeMasterPassword(char[] oldPassword, char[] newPassword) throws Exception {
        if (isLocked || appData == null) {
            throw new IllegalStateException("应用已锁定或数据未加载");
        }

        if (metaData == null) {
            metaData = loadMetaData();
        }

        if (metaData == null) {
            throw new IllegalStateException("元数据不存在");
        }

        if (!KeyDerivationUtil.verifyPassword(oldPassword, metaData.getSalt(), metaData.getPasswordHash())) {
            throw new IllegalArgumentException("原密码错误");
        }

        String newSalt = KeyDerivationUtil.generateSaltAsString();
        String newHash = KeyDerivationUtil.deriveKeyAsString(newPassword, newSalt);

        SecretKey newKey = CryptoUtil.deriveSecretKey(newPassword, java.util.Base64.getDecoder().decode(newSalt));

        metaData.setSalt(newSalt);
        metaData.setPasswordHash(newHash);

        appData.getSettings().setSalt(newSalt);
        appData.getSettings().setMasterPasswordHash(newHash);
        appData.getSettings().setLastMasterPasswordChange(LocalDateTime.now());

        this.encryptionKey = newKey;
        saveMetaData();
        saveData();
    }

    public UserSettings getUserSettings() {
        if (appData != null) {
            return appData.getSettings();
        }
        return null;
    }

    public void updateUserSettings(UserSettings settings) throws Exception {
        if (isLocked || appData == null) {
            throw new IllegalStateException("应用已锁定或数据未加载");
        }

        appData.setSettings(settings);
        saveData();
    }
}
