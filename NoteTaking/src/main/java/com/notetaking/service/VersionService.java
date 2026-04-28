package com.notetaking.service;

import com.notetaking.model.Note;
import com.notetaking.model.NoteVersion;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

public class VersionService {
    private static final Logger logger = LoggerFactory.getLogger(VersionService.class);
    private static final int MAX_VERSIONS_PER_NOTE = 50;
    private static final DateTimeFormatter VERSION_DATE_FORMAT = DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss");

    private final FileStorageService storageService;

    public VersionService() {
        this.storageService = new FileStorageService();
    }

    public VersionService(FileStorageService storageService) {
        this.storageService = storageService;
    }

    public void saveVersion(Note note) {
        NoteVersion version = new NoteVersion(note);
        version.setVersionNumber(generateVersionNumber());
        String noteVersionDir = getNoteVersionDir(note.getId());
        try {
            Files.createDirectories(Paths.get(noteVersionDir));
        } catch (Exception e) {
            logger.error("无法创建版本目录: {}", noteVersionDir, e);
        }
        storageService.save(version.getId(), version, noteVersionDir);
        logger.debug("保存版本: 笔记 {}, 版本 {}", note.getId(), version.getVersionNumber());
        cleanOldVersions(note.getId());
    }

    private String generateVersionNumber() {
        return "v_" + VERSION_DATE_FORMAT.format(LocalDateTime.now());
    }

    public List<NoteVersion> getVersions(String noteId) {
        String noteVersionDir = getNoteVersionDir(noteId);
        File dir = new File(noteVersionDir);
        if (!dir.exists() || !dir.isDirectory()) {
            return new ArrayList<>();
        }
        return storageService.loadAll(NoteVersion.class, noteVersionDir).stream()
                .sorted((v1, v2) -> v2.getCreatedAt().compareTo(v1.getCreatedAt()))
                .collect(Collectors.toList());
    }

    public NoteVersion getVersion(String noteId, String versionId) {
        String noteVersionDir = getNoteVersionDir(noteId);
        return storageService.load(versionId, NoteVersion.class, noteVersionDir);
    }

    public void restoreVersion(Note note, NoteVersion version) {
        note.setTitle(version.getTitle());
        note.setContent(version.getContent());
        logger.info("恢复笔记 {} 到版本 {}", note.getId(), version.getVersionNumber());
    }

    private void cleanOldVersions(String noteId) {
        List<NoteVersion> versions = getVersions(noteId);
        if (versions.size() > MAX_VERSIONS_PER_NOTE) {
            String noteVersionDir = getNoteVersionDir(noteId);
            for (int i = MAX_VERSIONS_PER_NOTE; i < versions.size(); i++) {
                NoteVersion oldVersion = versions.get(i);
                storageService.delete(oldVersion.getId(), noteVersionDir);
                logger.debug("删除旧版本: 笔记 {}, 版本 {}", noteId, oldVersion.getVersionNumber());
            }
        }
    }

    public boolean deleteVersion(String noteId, String versionId) {
        String noteVersionDir = getNoteVersionDir(noteId);
        boolean deleted = storageService.delete(versionId, noteVersionDir);
        if (deleted) {
            logger.info("删除版本: 笔记 {}, 版本 {}", noteId, versionId);
        }
        return deleted;
    }

    public void deleteAllVersions(String noteId) {
        String noteVersionDir = getNoteVersionDir(noteId);
        List<NoteVersion> versions = getVersions(noteId);
        for (NoteVersion version : versions) {
            storageService.delete(version.getId(), noteVersionDir);
        }
        logger.info("删除所有版本: 笔记 {}", noteId);
    }

    public String compareVersions(NoteVersion v1, NoteVersion v2) {
        StringBuilder diff = new StringBuilder();
        diff.append("=== 版本对比 ===\n");
        diff.append("版本1: ").append(v1.getVersionNumber()).append(" (").append(v1.getCreatedAt()).append(")\n");
        diff.append("版本2: ").append(v2.getVersionNumber()).append(" (").append(v2.getCreatedAt()).append(")\n\n");
        if (!v1.getTitle().equals(v2.getTitle())) {
            diff.append("--- 标题变化 ---\n");
            diff.append("旧: ").append(v1.getTitle()).append("\n");
            diff.append("新: ").append(v2.getTitle()).append("\n\n");
        }
        if (!v1.getContent().equals(v2.getContent())) {
            diff.append("--- 内容变化 ---\n");
            diff.append("注意: 内容有变化，详细差异需要专业对比工具\n");
        } else {
            diff.append("--- 内容无变化 ---\n");
        }
        return diff.toString();
    }

    private String getNoteVersionDir(String noteId) {
        return FileStorageService.getVersionsDir() + "/" + noteId;
    }
}
