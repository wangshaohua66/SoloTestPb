package com.notetaking.service;

import com.notetaking.model.Tag;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;
import java.util.stream.Collectors;

public class TagService {
    private static final Logger logger = LoggerFactory.getLogger(TagService.class);

    private final FileStorageService storageService;

    public TagService() {
        this.storageService = new FileStorageService();
    }

    public TagService(FileStorageService storageService) {
        this.storageService = storageService;
    }

    public Tag createTag(String name) {
        return createTag(name, null);
    }

    public Tag createTag(String name, String color) {
        if (isTagNameExists(name)) {
            logger.warn("标签名称已存在: {}", name);
            return getTagByName(name);
        }
        Tag tag = new Tag(name);
        if (color != null && !color.isEmpty()) {
            tag.setColor(color);
        }
        saveTag(tag);
        logger.info("创建标签: {} (ID: {})", name, tag.getId());
        return tag;
    }

    public Tag getTagById(String id) {
        return storageService.load(id, Tag.class, FileStorageService.getTagsDir());
    }

    public Tag getTagByName(String name) {
        return getAllTags().stream()
                .filter(t -> t.getName().equalsIgnoreCase(name))
                .findFirst()
                .orElse(null);
    }

    public void saveTag(Tag tag) {
        storageService.save(tag.getId(), tag, FileStorageService.getTagsDir());
    }

    public void updateTag(Tag tag) {
        saveTag(tag);
        logger.info("更新标签: {} (ID: {})", tag.getName(), tag.getId());
    }

    public boolean deleteTag(String id) {
        NoteService noteService = new NoteService();
        List<String> noteIds = noteService.getNotesByTag(id).stream()
                .map(n -> n.getId())
                .collect(Collectors.toList());
        for (String noteId : noteIds) {
            noteService.removeTagFromNote(noteId, id);
        }
        boolean deleted = storageService.delete(id, FileStorageService.getTagsDir());
        if (deleted) {
            logger.info("删除标签: ID: {}", id);
        }
        return deleted;
    }

    public List<Tag> getAllTags() {
        return storageService.loadAll(Tag.class, FileStorageService.getTagsDir());
    }

    public boolean isTagNameExists(String name) {
        return getAllTags().stream()
                .anyMatch(t -> t.getName().equalsIgnoreCase(name));
    }

    public List<Tag> getTagsWithNoteCount() {
        NoteService noteService = new NoteService();
        List<Tag> tags = getAllTags();
        return tags;
    }

    public int getTagUsageCount(String tagId) {
        NoteService noteService = new NoteService();
        return noteService.getNotesByTag(tagId).size();
    }

    public List<Tag> sortTags(List<Tag> tags, SortBy sortBy, boolean ascending) {
        Comparator<Tag> comparator;
        switch (sortBy) {
            case NAME:
                comparator = Comparator.comparing(Tag::getName, String.CASE_INSENSITIVE_ORDER);
                break;
            case USAGE_COUNT:
                comparator = Comparator.comparingInt(tag -> getTagUsageCount(tag.getId()));
                break;
            case CREATED_DATE:
                comparator = Comparator.comparing(Tag::getCreatedAt);
                break;
            default:
                comparator = Comparator.comparing(Tag::getName, String.CASE_INSENSITIVE_ORDER);
        }

        if (!ascending) {
            comparator = comparator.reversed();
        }

        return tags.stream()
                .sorted(comparator)
                .collect(Collectors.toList());
    }

    public enum SortBy {
        NAME,
        USAGE_COUNT,
        CREATED_DATE
    }
}
