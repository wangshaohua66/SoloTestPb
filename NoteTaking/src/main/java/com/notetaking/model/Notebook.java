package com.notetaking.model;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class Notebook {
    private String id;
    private String name;
    private String description;
    private String parentId;
    private List<String> noteIds;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public Notebook() {
        this.id = UUID.randomUUID().toString();
        this.noteIds = new ArrayList<>();
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    public Notebook(String name) {
        this();
        this.name = name;
    }

    public void addNote(String noteId) {
        if (!noteIds.contains(noteId)) {
            noteIds.add(noteId);
            this.updatedAt = LocalDateTime.now();
        }
    }

    public void removeNote(String noteId) {
        noteIds.remove(noteId);
        this.updatedAt = LocalDateTime.now();
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
        this.updatedAt = LocalDateTime.now();
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
        this.updatedAt = LocalDateTime.now();
    }

    public String getParentId() {
        return parentId;
    }

    public void setParentId(String parentId) {
        this.parentId = parentId;
        this.updatedAt = LocalDateTime.now();
    }

    public List<String> getNoteIds() {
        return noteIds;
    }

    public void setNoteIds(List<String> noteIds) {
        this.noteIds = noteIds;
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

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Notebook notebook = (Notebook) o;
        return id.equals(notebook.id);
    }

    @Override
    public int hashCode() {
        return id.hashCode();
    }
}
