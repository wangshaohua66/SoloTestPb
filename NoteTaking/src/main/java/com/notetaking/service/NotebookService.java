package com.notetaking.service;

import com.notetaking.model.Notebook;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;
import java.util.stream.Collectors;

public class NotebookService {
    private static final Logger logger = LoggerFactory.getLogger(NotebookService.class);

    private final FileStorageService storageService;

    public NotebookService() {
        this.storageService = new FileStorageService();
    }

    public NotebookService(FileStorageService storageService) {
        this.storageService = storageService;
    }

    public Notebook createNotebook(String name) {
        return createNotebook(name, null);
    }

    public Notebook createNotebook(String name, String parentId) {
        Notebook notebook = new Notebook(name);
        if (parentId != null) {
            notebook.setParentId(parentId);
        }
        saveNotebook(notebook);
        logger.info("创建笔记本: {} (ID: {})", name, notebook.getId());
        return notebook;
    }

    public Notebook getNotebookById(String id) {
        return storageService.load(id, Notebook.class, FileStorageService.getNotebooksDir());
    }

    public void saveNotebook(Notebook notebook) {
        storageService.save(notebook.getId(), notebook, FileStorageService.getNotebooksDir());
    }

    public void updateNotebook(Notebook notebook) {
        saveNotebook(notebook);
        logger.info("更新笔记本: {} (ID: {})", notebook.getName(), notebook.getId());
    }

    public boolean deleteNotebook(String id) {
        NoteService noteService = new NoteService();
        List<String> noteIds = new ArrayList<>();
        collectNotesInNotebook(id, noteIds, noteService);
        for (String noteId : noteIds) {
            noteService.deleteNote(noteId);
        }
        deleteSubNotebooks(id);
        boolean deleted = storageService.delete(id, FileStorageService.getNotebooksDir());
        if (deleted) {
            logger.info("删除笔记本: ID: {}", id);
        }
        return deleted;
    }

    private void collectNotesInNotebook(String notebookId, List<String> noteIds, NoteService noteService) {
        Notebook notebook = getNotebookById(notebookId);
        if (notebook != null) {
            noteIds.addAll(notebook.getNoteIds());
        }
        List<Notebook> children = getChildNotebooks(notebookId);
        for (Notebook child : children) {
            collectNotesInNotebook(child.getId(), noteIds, noteService);
        }
    }

    private void deleteSubNotebooks(String parentId) {
        List<Notebook> children = getChildNotebooks(parentId);
        for (Notebook child : children) {
            deleteSubNotebooks(child.getId());
            storageService.delete(child.getId(), FileStorageService.getNotebooksDir());
        }
    }

    public List<Notebook> getAllNotebooks() {
        return storageService.loadAll(Notebook.class, FileStorageService.getNotebooksDir());
    }

    public List<Notebook> getRootNotebooks() {
        return getAllNotebooks().stream()
                .filter(n -> n.getParentId() == null)
                .collect(Collectors.toList());
    }

    public List<Notebook> getChildNotebooks(String parentId) {
        return getAllNotebooks().stream()
                .filter(n -> parentId.equals(n.getParentId()))
                .collect(Collectors.toList());
    }

    public void addNoteToNotebook(String notebookId, String noteId) {
        Notebook notebook = getNotebookById(notebookId);
        if (notebook != null) {
            notebook.addNote(noteId);
            saveNotebook(notebook);
            logger.info("添加笔记 {} 到笔记本 {}", noteId, notebookId);
        }
    }

    public void removeNoteFromNotebook(String notebookId, String noteId) {
        Notebook notebook = getNotebookById(notebookId);
        if (notebook != null) {
            notebook.removeNote(noteId);
            saveNotebook(notebook);
            logger.info("从笔记本 {} 移除笔记 {}", notebookId, noteId);
        }
    }

    public void moveNotebook(String notebookId, String newParentId) {
        Notebook notebook = getNotebookById(notebookId);
        if (notebook != null && !notebookId.equals(newParentId)) {
            if (isDescendant(notebookId, newParentId)) {
                logger.warn("无法移动笔记本到其子笔记本中");
                return;
            }
            notebook.setParentId(newParentId);
            saveNotebook(notebook);
            logger.info("移动笔记本 {} 到父笔记本 {}", notebookId, newParentId);
        }
    }

    private boolean isDescendant(String ancestorId, String checkId) {
        if (checkId == null) {
            return false;
        }
        Notebook notebook = getNotebookById(checkId);
        while (notebook != null) {
            if (ancestorId.equals(notebook.getId())) {
                return true;
            }
            String parentId = notebook.getParentId();
            if (parentId == null) {
                break;
            }
            notebook = getNotebookById(parentId);
        }
        return false;
    }

    public List<Notebook> sortNotebooks(List<Notebook> notebooks, SortBy sortBy, boolean ascending) {
        Comparator<Notebook> comparator;
        switch (sortBy) {
            case NAME:
                comparator = Comparator.comparing(Notebook::getName, String.CASE_INSENSITIVE_ORDER);
                break;
            case NOTE_COUNT:
                comparator = Comparator.comparingInt(n -> n.getNoteIds().size());
                break;
            case CREATED_DATE:
                comparator = Comparator.comparing(Notebook::getCreatedAt);
                break;
            case UPDATED_DATE:
                comparator = Comparator.comparing(Notebook::getUpdatedAt);
                break;
            default:
                comparator = Comparator.comparing(Notebook::getName, String.CASE_INSENSITIVE_ORDER);
        }

        if (!ascending) {
            comparator = comparator.reversed();
        }

        return notebooks.stream()
                .sorted(comparator)
                .collect(Collectors.toList());
    }

    public enum SortBy {
        NAME,
        NOTE_COUNT,
        CREATED_DATE,
        UPDATED_DATE
    }
}
