package com.notetaking.model;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class Note {
    private String id;
    private String title;
    private String content;
    private String notebookId;
    private List<String> tagIds;
    private boolean encrypted;
    private boolean favorite;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private LocalDateTime lastAccessedAt;
    private int wordCount;

    public Note() {
        this.id = UUID.randomUUID().toString();
        this.tagIds = new ArrayList<>();
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        this.lastAccessedAt = LocalDateTime.now();
        this.title = "未命名笔记";
        this.content = "";
        this.encrypted = false;
        this.favorite = false;
        this.wordCount = 0;
    }

    public Note(String title, String content) {
        this();
        this.title = title;
        this.content = content;
        this.wordCount = calculateWordCount(content);
    }

    private int calculateWordCount(String content) {
        if (content == null || content.isEmpty()) {
            return 0;
        }
        String trimmed = content.trim();
        if (trimmed.isEmpty()) {
            return 0;
        }
        return trimmed.split("\\s+|(?=[\\u4e00-\\u9fff])|(?<=[\\u4e00-\\u9fff])").length;
    }

    public void updateContent(String content) {
        this.content = content;
        this.wordCount = calculateWordCount(content);
        this.updatedAt = LocalDateTime.now();
    }

    public void addTag(String tagId) {
        if (!tagIds.contains(tagId)) {
            tagIds.add(tagId);
            this.updatedAt = LocalDateTime.now();
        }
    }

    public void removeTag(String tagId) {
        tagIds.remove(tagId);
        this.updatedAt = LocalDateTime.now();
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
        this.updatedAt = LocalDateTime.now();
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
        this.wordCount = calculateWordCount(content);
        this.updatedAt = LocalDateTime.now();
    }

    public String getNotebookId() {
        return notebookId;
    }

    public void setNotebookId(String notebookId) {
        this.notebookId = notebookId;
        this.updatedAt = LocalDateTime.now();
    }

    public List<String> getTagIds() {
        return tagIds;
    }

    public void setTagIds(List<String> tagIds) {
        this.tagIds = tagIds;
        this.updatedAt = LocalDateTime.now();
    }

    public boolean isEncrypted() {
        return encrypted;
    }

    public void setEncrypted(boolean encrypted) {
        this.encrypted = encrypted;
        this.updatedAt = LocalDateTime.now();
    }

    public boolean isFavorite() {
        return favorite;
    }

    public void setFavorite(boolean favorite) {
        this.favorite = favorite;
        this.updatedAt = LocalDateTime.now();
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

    public LocalDateTime getLastAccessedAt() {
        return lastAccessedAt;
    }

    public void setLastAccessedAt(LocalDateTime lastAccessedAt) {
        this.lastAccessedAt = lastAccessedAt;
    }

    public int getWordCount() {
        return wordCount;
    }

    public void setWordCount(int wordCount) {
        this.wordCount = wordCount;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Note note = (Note) o;
        return id.equals(note.id);
    }

    @Override
    public int hashCode() {
        return id.hashCode();
    }
}
