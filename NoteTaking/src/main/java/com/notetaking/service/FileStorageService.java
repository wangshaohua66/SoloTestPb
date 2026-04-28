package com.notetaking.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

public class FileStorageService {
    private static final Logger logger = LoggerFactory.getLogger(FileStorageService.class);
    private static final String APP_DIR = System.getProperty("user.home") + "/.notetaking";
    private static final String NOTES_DIR = APP_DIR + "/notes";
    private static final String NOTEBOOKS_DIR = APP_DIR + "/notebooks";
    private static final String TAGS_DIR = APP_DIR + "/tags";
    private static final String VERSIONS_DIR = APP_DIR + "/versions";
    private static final String TEMPLATES_DIR = APP_DIR + "/templates";
    private static final String SEARCH_HISTORY_FILE = APP_DIR + "/search_history.json";

    private final ObjectMapper objectMapper;

    public FileStorageService() {
        this.objectMapper = new ObjectMapper();
        this.objectMapper.registerModule(new JavaTimeModule());
        this.objectMapper.enable(SerializationFeature.INDENT_OUTPUT);
        this.objectMapper.disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
        initializeDirectories();
    }

    private void initializeDirectories() {
        try {
            Files.createDirectories(Paths.get(NOTES_DIR));
            Files.createDirectories(Paths.get(NOTEBOOKS_DIR));
            Files.createDirectories(Paths.get(TAGS_DIR));
            Files.createDirectories(Paths.get(VERSIONS_DIR));
            Files.createDirectories(Paths.get(TEMPLATES_DIR));
            Files.createDirectories(Paths.get(APP_DIR + "/logs"));
        } catch (IOException e) {
            logger.error("无法初始化存储目录", e);
            throw new RuntimeException("无法初始化存储目录", e);
        }
    }

    public <T> void save(String id, T entity, String directory) {
        Path filePath = Paths.get(directory, id + ".json");
        try {
            objectMapper.writeValue(filePath.toFile(), entity);
            logger.debug("已保存: {}", filePath);
        } catch (IOException e) {
            logger.error("保存失败: {}", filePath, e);
            throw new RuntimeException("保存失败: " + filePath, e);
        }
    }

    public <T> T load(String id, Class<T> clazz, String directory) {
        Path filePath = Paths.get(directory, id + ".json");
        File file = filePath.toFile();
        if (!file.exists()) {
            return null;
        }
        try {
            return objectMapper.readValue(file, clazz);
        } catch (IOException e) {
            logger.error("加载失败: {}", filePath, e);
            throw new RuntimeException("加载失败: " + filePath, e);
        }
    }

    public boolean delete(String id, String directory) {
        Path filePath = Paths.get(directory, id + ".json");
        try {
            return Files.deleteIfExists(filePath);
        } catch (IOException e) {
            logger.error("删除失败: {}", filePath, e);
            return false;
        }
    }

    public <T> List<T> loadAll(Class<T> clazz, String directory) {
        List<T> entities = new ArrayList<>();
        File dir = new File(directory);
        if (!dir.exists() || !dir.isDirectory()) {
            return entities;
        }

        File[] files = dir.listFiles((d, name) -> name.endsWith(".json"));
        if (files == null) {
            return entities;
        }

        for (File file : files) {
            try {
                T entity = objectMapper.readValue(file, clazz);
                entities.add(entity);
            } catch (IOException e) {
                logger.warn("无法加载文件: {}", file.getName(), e);
            }
        }
        return entities;
    }

    public <T> void saveList(List<T> entities, String filePath) {
        try {
            objectMapper.writeValue(Paths.get(filePath).toFile(), entities);
        } catch (IOException e) {
            logger.error("保存列表失败: {}", filePath, e);
            throw new RuntimeException("保存列表失败: " + filePath, e);
        }
    }

    public <T> List<T> loadList(Class<T> clazz, String filePath) {
        File file = Paths.get(filePath).toFile();
        if (!file.exists()) {
            return new ArrayList<>();
        }
        try {
            return objectMapper.readValue(file,
                    objectMapper.getTypeFactory().constructCollectionType(List.class, clazz));
        } catch (IOException e) {
            logger.error("加载列表失败: {}", filePath, e);
            return new ArrayList<>();
        }
    }

    public static String getNotesDir() {
        return NOTES_DIR;
    }

    public static String getNotebooksDir() {
        return NOTEBOOKS_DIR;
    }

    public static String getTagsDir() {
        return TAGS_DIR;
    }

    public static String getVersionsDir() {
        return VERSIONS_DIR;
    }

    public static String getTemplatesDir() {
        return TEMPLATES_DIR;
    }

    public static String getSearchHistoryFile() {
        return SEARCH_HISTORY_FILE;
    }

    public static String getAppDir() {
        return APP_DIR;
    }
}
