package com.unitconverter.persistence;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonSyntaxException;
import com.google.gson.reflect.TypeToken;
import com.unitconverter.model.*;
import com.unitconverter.registry.UnitRegistry;

import java.io.*;
import java.lang.reflect.Type;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.prefs.Preferences;

public class DataManager {
    private static DataManager instance;
    private final Gson gson;
    private final String dataDirectory;
    private final Preferences preferences;

    private static final String CUSTOM_UNITS_FILE = "custom_units.json";
    private static final String CONVERSION_HISTORY_FILE = "conversion_history.json";
    private static final String CALCULATION_HISTORY_FILE = "calculation_history.json";
    private static final String FAVORITES_FILE = "favorites.json";
    private static final String SETTINGS_FILE = "settings.json";

    private DataManager() {
        gson = new GsonBuilder()
            .setPrettyPrinting()
            .registerTypeAdapter(LocalDateTime.class, new LocalDateTimeAdapter())
            .create();

        dataDirectory = System.getProperty("user.home") + File.separator + ".unitconverter";
        ensureDataDirectory();

        preferences = Preferences.userNodeForPackage(DataManager.class);
    }

    public static synchronized DataManager getInstance() {
        if (instance == null) {
            instance = new DataManager();
        }
        return instance;
    }

    private void ensureDataDirectory() {
        File dir = new File(dataDirectory);
        if (!dir.exists()) {
            dir.mkdirs();
        }
    }

    public void saveCustomUnits(List<UnitDefinition> customUnits) {
        List<UnitDefinition> unitsToSave = new ArrayList<>();
        for (UnitDefinition unit : customUnits) {
            if (unit.isCustom()) {
                unitsToSave.add(unit);
            }
        }

        String json = gson.toJson(unitsToSave);
        writeFile(CUSTOM_UNITS_FILE, json);
    }

    public List<UnitDefinition> loadCustomUnits() {
        String json = readFile(CUSTOM_UNITS_FILE);
        if (json == null || json.isEmpty()) {
            return new ArrayList<>();
        }

        try {
            Type listType = new TypeToken<List<UnitDefinition>>() {}.getType();
            List<UnitDefinition> units = gson.fromJson(json, listType);
            return units != null ? units : new ArrayList<>();
        } catch (JsonSyntaxException e) {
            return new ArrayList<>();
        }
    }

    public void saveConversionHistory(List<ConversionHistory> history) {
        String json = gson.toJson(history);
        writeFile(CONVERSION_HISTORY_FILE, json);
    }

    public List<ConversionHistory> loadConversionHistory() {
        String json = readFile(CONVERSION_HISTORY_FILE);
        if (json == null || json.isEmpty()) {
            return new ArrayList<>();
        }

        try {
            Type listType = new TypeToken<List<ConversionHistory>>() {}.getType();
            List<ConversionHistory> history = gson.fromJson(json, listType);
            return history != null ? history : new ArrayList<>();
        } catch (JsonSyntaxException e) {
            return new ArrayList<>();
        }
    }

    public void saveFavorites(List<String> favoriteUnitIds) {
        String json = gson.toJson(favoriteUnitIds);
        writeFile(FAVORITES_FILE, json);
    }

    public List<String> loadFavorites() {
        String json = readFile(FAVORITES_FILE);
        if (json == null || json.isEmpty()) {
            return new ArrayList<>();
        }

        try {
            Type listType = new TypeToken<List<String>>() {}.getType();
            List<String> favorites = gson.fromJson(json, listType);
            return favorites != null ? favorites : new ArrayList<>();
        } catch (JsonSyntaxException e) {
            return new ArrayList<>();
        }
    }

    public void saveSettings(AppSettings settings) {
        String json = gson.toJson(settings);
        writeFile(SETTINGS_FILE, json);
    }

    public AppSettings loadSettings() {
        String json = readFile(SETTINGS_FILE);
        if (json == null || json.isEmpty()) {
            return new AppSettings();
        }

        try {
            AppSettings settings = gson.fromJson(json, AppSettings.class);
            return settings != null ? settings : new AppSettings();
        } catch (JsonSyntaxException e) {
            return new AppSettings();
        }
    }

    public void exportData(String exportPath) {
        AppData data = new AppData();
        data.customUnits = loadCustomUnits();
        data.favorites = loadFavorites();
        data.settings = loadSettings();

        String json = gson.toJson(data);
        try {
            Files.write(Paths.get(exportPath), json.getBytes(StandardCharsets.UTF_8));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void importData(String importPath) {
        try {
            String json = new String(Files.readAllBytes(Paths.get(importPath)), StandardCharsets.UTF_8);
            AppData data = gson.fromJson(json, AppData.class);

            if (data.customUnits != null) {
                for (UnitDefinition unit : data.customUnits) {
                    UnitRegistry.getInstance().addUnit(unit);
                }
                saveCustomUnits(data.customUnits);
            }

            if (data.favorites != null) {
                for (String unitId : data.favorites) {
                    UnitRegistry.getInstance().updateUnitFavorite(unitId, true);
                }
                saveFavorites(data.favorites);
            }

            if (data.settings != null) {
                saveSettings(data.settings);
            }
        } catch (IOException | JsonSyntaxException e) {
            e.printStackTrace();
        }
    }

    private void writeFile(String filename, String content) {
        try {
            Path path = Paths.get(dataDirectory, filename);
            Files.write(path, content.getBytes(StandardCharsets.UTF_8));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private String readFile(String filename) {
        try {
            Path path = Paths.get(dataDirectory, filename);
            if (!Files.exists(path)) {
                return null;
            }
            return new String(Files.readAllBytes(path), StandardCharsets.UTF_8);
        } catch (IOException e) {
            return null;
        }
    }

    public String getDataDirectory() {
        return dataDirectory;
    }

    public static class AppData implements Serializable {
        public List<UnitDefinition> customUnits;
        public List<String> favorites;
        public AppSettings settings;
    }

    public static class AppSettings implements Serializable {
        private static final long serialVersionUID = 1L;
        
        private int decimalPlaces = 6;
        private boolean useScientificNotation = false;
        private String defaultUnitType = "LENGTH";
        private String theme = "LIGHT";
        private int maxHistoryItems = 100;
        private boolean autoSaveHistory = true;

        public int getDecimalPlaces() {
            return decimalPlaces;
        }

        public void setDecimalPlaces(int decimalPlaces) {
            this.decimalPlaces = decimalPlaces;
        }

        public boolean isUseScientificNotation() {
            return useScientificNotation;
        }

        public void setUseScientificNotation(boolean useScientificNotation) {
            this.useScientificNotation = useScientificNotation;
        }

        public String getDefaultUnitType() {
            return defaultUnitType;
        }

        public void setDefaultUnitType(String defaultUnitType) {
            this.defaultUnitType = defaultUnitType;
        }

        public String getTheme() {
            return theme;
        }

        public void setTheme(String theme) {
            this.theme = theme;
        }

        public int getMaxHistoryItems() {
            return maxHistoryItems;
        }

        public void setMaxHistoryItems(int maxHistoryItems) {
            this.maxHistoryItems = maxHistoryItems;
        }

        public boolean isAutoSaveHistory() {
            return autoSaveHistory;
        }

        public void setAutoSaveHistory(boolean autoSaveHistory) {
            this.autoSaveHistory = autoSaveHistory;
        }
    }

    private static class LocalDateTimeAdapter implements com.google.gson.JsonSerializer<LocalDateTime>, 
                                                         com.google.gson.JsonDeserializer<LocalDateTime> {
        private final DateTimeFormatter formatter = DateTimeFormatter.ISO_LOCAL_DATE_TIME;

        @Override
        public com.google.gson.JsonElement serialize(LocalDateTime src, java.lang.reflect.Type typeOfSrc, 
                                                      com.google.gson.JsonSerializationContext context) {
            return new com.google.gson.JsonPrimitive(src.format(formatter));
        }

        @Override
        public LocalDateTime deserialize(com.google.gson.JsonElement json, java.lang.reflect.Type typeOfT,
                                          com.google.gson.JsonDeserializationContext context) throws com.google.gson.JsonParseException {
            return LocalDateTime.parse(json.getAsString(), formatter);
        }
    }
}
