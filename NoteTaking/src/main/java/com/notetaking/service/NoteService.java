package com.notetaking.service;

import com.notetaking.model.Note;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

public class NoteService {
    private static final Logger logger = LoggerFactory.getLogger(NoteService.class);

    private final FileStorageService storageService;
    private final VersionService versionService;

    public NoteService() {
        this.storageService = new FileStorageService();
        this.versionService = new VersionService();
    }

    public NoteService(FileStorageService storageService, VersionService versionService) {
        this.storageService = storageService;
        this.versionService = versionService;
    }

    public Note createNote(String title, String content) {
        Note note = new Note(title, content);
        saveNote(note);
        logger.info("创建笔记: {} (ID: {})", title, note.getId());
        return note;
    }

    public Note createNote(String title) {
        return createNote(title, "");
    }

    public Note getNoteById(String id) {
        Note note = storageService.load(id, Note.class, FileStorageService.getNotesDir());
        if (note != null) {
            note.setLastAccessedAt(LocalDateTime.now());
            saveNote(note);
        }
        return note;
    }

    public void updateNote(Note note) {
        versionService.saveVersion(note);
        note.setUpdatedAt(LocalDateTime.now());
        saveNote(note);
        logger.info("更新笔记: {} (ID: {})", note.getTitle(), note.getId());
    }

    public void saveNote(Note note) {
        storageService.save(note.getId(), note, FileStorageService.getNotesDir());
    }

    public boolean deleteNote(String id) {
        Note note = getNoteById(id);
        if (note != null) {
            if (note.getNotebookId() != null) {
                NotebookService notebookService = new NotebookService();
                notebookService.removeNoteFromNotebook(note.getNotebookId(), id);
            }
        }
        boolean deleted = storageService.delete(id, FileStorageService.getNotesDir());
        if (deleted) {
            logger.info("删除笔记: ID: {}", id);
        }
        return deleted;
    }

    public List<Note> getAllNotes() {
        return storageService.loadAll(Note.class, FileStorageService.getNotesDir());
    }

    public List<Note> getNotesByNotebook(String notebookId) {
        return getAllNotes().stream()
                .filter(note -> notebookId.equals(note.getNotebookId()))
                .collect(Collectors.toList());
    }

    public List<Note> getNotesByTag(String tagId) {
        return getAllNotes().stream()
                .filter(note -> note.getTagIds().contains(tagId))
                .collect(Collectors.toList());
    }

    public List<Note> getFavoriteNotes() {
        return getAllNotes().stream()
                .filter(Note::isFavorite)
                .collect(Collectors.toList());
    }

    public List<Note> getRecentNotes(int limit) {
        return getAllNotes().stream()
                .sorted(Comparator.comparing(Note::getLastAccessedAt).reversed())
                .limit(limit)
                .collect(Collectors.toList());
    }

    public List<Note> sortNotes(List<Note> notes, SortBy sortBy, boolean ascending) {
        Comparator<Note> comparator;
        switch (sortBy) {
            case TITLE:
                comparator = Comparator.comparing(Note::getTitle, String.CASE_INSENSITIVE_ORDER);
                break;
            case CREATED_DATE:
                comparator = Comparator.comparing(Note::getCreatedAt);
                break;
            case UPDATED_DATE:
                comparator = Comparator.comparing(Note::getUpdatedAt);
                break;
            case ACCESSED_DATE:
                comparator = Comparator.comparing(Note::getLastAccessedAt);
                break;
            case WORD_COUNT:
                comparator = Comparator.comparingInt(Note::getWordCount);
                break;
            default:
                comparator = Comparator.comparing(Note::getUpdatedAt);
        }

        if (!ascending) {
            comparator = comparator.reversed();
        }

        return notes.stream()
                .sorted(comparator)
                .collect(Collectors.toList());
    }

    public void addTagToNote(String noteId, String tagId) {
        Note note = getNoteById(noteId);
        if (note != null) {
            note.addTag(tagId);
            saveNote(note);
            logger.info("添加标签 {} 到笔记 {}", tagId, noteId);
        }
    }

    public void removeTagFromNote(String noteId, String tagId) {
        Note note = getNoteById(noteId);
        if (note != null) {
            note.removeTag(tagId);
            saveNote(note);
            logger.info("从笔记 {} 移除标签 {}", noteId, tagId);
        }
    }

    public void moveNoteToNotebook(String noteId, String notebookId) {
        Note note = getNoteById(noteId);
        if (note != null) {
            String oldNotebookId = note.getNotebookId();
            if (oldNotebookId != null && !oldNotebookId.equals(notebookId)) {
                NotebookService notebookService = new NotebookService();
                notebookService.removeNoteFromNotebook(oldNotebookId, noteId);
            }
            note.setNotebookId(notebookId);
            saveNote(note);
            logger.info("移动笔记 {} 到笔记本 {}", noteId, notebookId);
        }
    }

    public void toggleFavorite(String noteId) {
        Note note = getNoteById(noteId);
        if (note != null) {
            note.setFavorite(!note.isFavorite());
            saveNote(note);
            logger.info("切换笔记 {} 收藏状态: {}", noteId, note.isFavorite());
        }
    }

    public int getTotalWordCount() {
        return getAllNotes().stream()
                .mapToInt(Note::getWordCount)
                .sum();
    }

    public enum SortBy {
        TITLE,
        CREATED_DATE,
        UPDATED_DATE,
        ACCESSED_DATE,
        WORD_COUNT
    }
}
