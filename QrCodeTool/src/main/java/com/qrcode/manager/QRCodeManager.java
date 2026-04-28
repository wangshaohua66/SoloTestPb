package com.qrcode.manager;

import com.qrcode.model.QRCodeRecord;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

public class QRCodeManager {

    private static QRCodeManager instance;
    private List<QRCodeRecord> records;
    private Map<String, List<QRCodeRecord>> categoryMap;
    private Set<Long> favoriteIds;
    private long nextId = 1;
    
    private static final String DATA_DIR = System.getProperty("user.home") + "/.qrcode_tool";
    private static final String RECORDS_FILE = DATA_DIR + "/records.dat";
    private static final String CATEGORIES_FILE = DATA_DIR + "/categories.dat";
    private static final String FAVORITES_FILE = DATA_DIR + "/favorites.dat";

    private QRCodeManager() {
        records = new ArrayList<>();
        categoryMap = new HashMap<>();
        favoriteIds = new HashSet<>();
        loadData();
    }

    public static synchronized QRCodeManager getInstance() {
        if (instance == null) {
            instance = new QRCodeManager();
        }
        return instance;
    }

    public QRCodeRecord addRecord(String content, QRCodeRecord.QRCodeType type) {
        QRCodeRecord record = new QRCodeRecord(content, type);
        record.setId(nextId++);
        records.add(0, record);
        saveRecords();
        return record;
    }

    public QRCodeRecord addRecord(String content, QRCodeRecord.QRCodeType type, String filePath) {
        QRCodeRecord record = addRecord(content, type);
        record.setFilePath(filePath);
        saveRecords();
        return record;
    }

    public void updateRecord(QRCodeRecord record) {
        record.setUpdateTime(LocalDateTime.now());
        saveRecords();
    }

    public void deleteRecord(Long id) {
        records.removeIf(r -> r.getId().equals(id));
        favoriteIds.remove(id);
        
        for (List<QRCodeRecord> categoryRecords : categoryMap.values()) {
            categoryRecords.removeIf(r -> r.getId().equals(id));
        }
        
        saveAll();
    }

    public List<QRCodeRecord> getAllRecords() {
        return new ArrayList<>(records);
    }

    public QRCodeRecord getRecordById(Long id) {
        return records.stream()
                .filter(r -> r.getId().equals(id))
                .findFirst()
                .orElse(null);
    }

    public List<QRCodeRecord> searchRecords(String keyword) {
        if (keyword == null || keyword.isEmpty()) {
            return getAllRecords();
        }
        
        String lowerKeyword = keyword.toLowerCase();
        return records.stream()
                .filter(r -> r.getContent() != null && r.getContent().toLowerCase().contains(lowerKeyword))
                .collect(Collectors.toList());
    }

    public void addToFavorites(Long id) {
        QRCodeRecord record = getRecordById(id);
        if (record != null) {
            record.setFavorite(true);
            favoriteIds.add(id);
            saveAll();
        }
    }

    public void removeFromFavorites(Long id) {
        QRCodeRecord record = getRecordById(id);
        if (record != null) {
            record.setFavorite(false);
            favoriteIds.remove(id);
            saveAll();
        }
    }

    public List<QRCodeRecord> getFavorites() {
        return records.stream()
                .filter(QRCodeRecord::isFavorite)
                .collect(Collectors.toList());
    }

    public boolean isFavorite(Long id) {
        return favoriteIds.contains(id);
    }

    public void addCategory(String category) {
        if (!categoryMap.containsKey(category)) {
            categoryMap.put(category, new ArrayList<>());
            saveCategories();
        }
    }

    public void deleteCategory(String category) {
        List<QRCodeRecord> categoryRecords = categoryMap.get(category);
        if (categoryRecords != null) {
            for (QRCodeRecord record : categoryRecords) {
                record.setCategory(null);
            }
        }
        categoryMap.remove(category);
        saveAll();
    }

    public Set<String> getCategories() {
        return new HashSet<>(categoryMap.keySet());
    }

    public void assignCategory(Long id, String category) {
        QRCodeRecord record = getRecordById(id);
        if (record != null) {
            if (record.getCategory() != null && categoryMap.containsKey(record.getCategory())) {
                categoryMap.get(record.getCategory()).removeIf(r -> r.getId().equals(id));
            }
            
            record.setCategory(category);
            
            if (category != null) {
                if (!categoryMap.containsKey(category)) {
                    categoryMap.put(category, new ArrayList<>());
                }
                categoryMap.get(category).add(record);
            }
            
            saveAll();
        }
    }

    public List<QRCodeRecord> getRecordsByCategory(String category) {
        List<QRCodeRecord> result = categoryMap.get(category);
        return result != null ? new ArrayList<>(result) : new ArrayList<>();
    }

    public Statistics getStatistics() {
        Statistics stats = new Statistics();
        stats.totalCount = records.size();
        stats.favoriteCount = favoriteIds.size();
        stats.categoryCount = categoryMap.size();
        
        Map<QRCodeRecord.QRCodeType, Long> typeCount = records.stream()
                .collect(Collectors.groupingBy(QRCodeRecord::getType, Collectors.counting()));
        stats.typeDistribution = typeCount;
        
        return stats;
    }

    private void loadData() {
        try {
            Path dataPath = Paths.get(DATA_DIR);
            if (!Files.exists(dataPath)) {
                Files.createDirectories(dataPath);
                return;
            }
            
            loadRecords();
            loadCategories();
            loadFavorites();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @SuppressWarnings("unchecked")
    private void loadRecords() {
        File file = new File(RECORDS_FILE);
        if (file.exists()) {
            try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream(file))) {
                records = (List<QRCodeRecord>) ois.readObject();
                if (!records.isEmpty()) {
                    nextId = records.stream()
                            .max(Comparator.comparing(QRCodeRecord::getId))
                            .get()
                            .getId() + 1;
                }
            } catch (Exception e) {
                records = new ArrayList<>();
            }
        }
    }

    @SuppressWarnings("unchecked")
    private void loadCategories() {
        File file = new File(CATEGORIES_FILE);
        if (file.exists()) {
            try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream(file))) {
                categoryMap = (Map<String, List<QRCodeRecord>>) ois.readObject();
            } catch (Exception e) {
                categoryMap = new HashMap<>();
            }
        }
    }

    @SuppressWarnings("unchecked")
    private void loadFavorites() {
        File file = new File(FAVORITES_FILE);
        if (file.exists()) {
            try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream(file))) {
                favoriteIds = (Set<Long>) ois.readObject();
            } catch (Exception e) {
                favoriteIds = new HashSet<>();
            }
        }
    }

    private void saveRecords() {
        try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(RECORDS_FILE))) {
            oos.writeObject(records);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void saveCategories() {
        try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(CATEGORIES_FILE))) {
            oos.writeObject(categoryMap);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void saveFavorites() {
        try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(FAVORITES_FILE))) {
            oos.writeObject(favoriteIds);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void saveAll() {
        saveRecords();
        saveCategories();
        saveFavorites();
    }

    public static class Statistics {
        public int totalCount;
        public int favoriteCount;
        public int categoryCount;
        public Map<QRCodeRecord.QRCodeType, Long> typeDistribution;
    }
}
