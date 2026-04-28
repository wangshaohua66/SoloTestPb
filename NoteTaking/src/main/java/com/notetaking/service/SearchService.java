package com.notetaking.service;

import com.notetaking.model.Note;
import com.notetaking.model.SearchCriteria;
import com.notetaking.model.SearchHistory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDateTime;
import java.util.*;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

public class SearchService {
    private static final Logger logger = LoggerFactory.getLogger(SearchService.class);
    private static final int MAX_SEARCH_HISTORY_LIMIT = 50;

    private final NoteService noteService;
    private final FileStorageService storageService;

    public SearchService() {
        this.noteService = new NoteService();
        this.storageService = new FileStorageService();
    }

    public SearchService(NoteService noteService, FileStorageService storageService) {
        this.noteService = noteService;
        this.storageService = storageService;
    }

    public List<Note> search(String keyword) {
        return search(keyword, SearchHistory.SearchType.FULL_TEXT);
    }

    public List<Note> search(String keyword, SearchHistory.SearchType searchType) {
        if (keyword == null || keyword.trim().isEmpty()) {
            return new ArrayList<>();
        }

        List<Note> allNotes = noteService.getAllNotes();
        List<Note> results = new ArrayList<>();
        String lowerKeyword = keyword.toLowerCase();

        for (Note note : allNotes) {
            if (note.isEncrypted()) {
                continue;
            }
            boolean match = false;
            switch (searchType) {
                case TITLE:
                    match = note.getTitle().toLowerCase().contains(lowerKeyword);
                    break;
                case FULL_TEXT:
                default:
                    match = note.getTitle().toLowerCase().contains(lowerKeyword)
                            || note.getContent().toLowerCase().contains(lowerKeyword);
                    break;
            }
            if (match) {
                results.add(note);
            }
        }

        saveSearchHistory(keyword, searchType, results.size());
        logger.info("搜索: '{}', 类型: {}, 结果数: {}", keyword, searchType, results.size());

        return results;
    }

    public List<Note> searchByTag(String tagId) {
        if (tagId == null || tagId.isEmpty()) {
            return new ArrayList<>();
        }
        List<Note> results = noteService.getNotesByTag(tagId);
        saveSearchHistory("tag:" + tagId, SearchHistory.SearchType.TAG, results.size());
        return results;
    }

    public List<Note> advancedSearch(SearchCriteria criteria) {
        List<Note> allNotes = noteService.getAllNotes();
        List<Note> results = new ArrayList<>();

        for (Note note : allNotes) {
            if (matchesCriteria(note, criteria)) {
                results.add(note);
            }
        }

        StringBuilder queryBuilder = new StringBuilder();
        if (criteria.getKeyword() != null) queryBuilder.append(criteria.getKeyword()).append(" ");
        if (criteria.getTitle() != null) queryBuilder.append("title:").append(criteria.getTitle()).append(" ");

        saveSearchHistory(queryBuilder.toString().trim(), SearchHistory.SearchType.ADVANCED, results.size());
        logger.info("高级搜索, 结果数: {}", results.size());

        return results;
    }

    private boolean matchesCriteria(Note note, SearchCriteria criteria) {
        if (note.isEncrypted()) {
            return false;
        }

        if (criteria.getKeyword() != null && !criteria.getKeyword().isEmpty()) {
            String keyword = criteria.getKeyword().toLowerCase();
            if (!note.getTitle().toLowerCase().contains(keyword)
                    && !note.getContent().toLowerCase().contains(keyword)) {
                return false;
            }
        }

        if (criteria.getTitle() != null && !criteria.getTitle().isEmpty()) {
            if (!note.getTitle().toLowerCase().contains(criteria.getTitle().toLowerCase())) {
                return false;
            }
        }

        if (criteria.getTagId() != null) {
            if (!note.getTagIds().contains(criteria.getTagId())) {
                return false;
            }
        }

        if (criteria.getNotebookId() != null) {
            if (!criteria.getNotebookId().equals(note.getNotebookId())) {
                return false;
            }
        }

        if (criteria.getStartDate() != null) {
            if (note.getCreatedAt().isBefore(criteria.getStartDate())) {
                return false;
            }
        }

        if (criteria.getEndDate() != null) {
            if (note.getCreatedAt().isAfter(criteria.getEndDate())) {
                return false;
            }
        }

        if (criteria.getIsFavorite() != null) {
            if (note.isFavorite() != criteria.getIsFavorite()) {
                return false;
            }
        }

        if (criteria.getIsEncrypted() != null) {
            if (note.isEncrypted() != criteria.getIsEncrypted()) {
                return false;
            }
        }

        return true;
    }

    public Map<String, List<Integer>> buildIndex() {
        Map<String, List<Integer>> index = new HashMap<>();
        List<Note> notes = noteService.getAllNotes();

        for (Note note : notes) {
            if (note.isEncrypted()) {
                continue;
            }

            Set<String> words = extractWords(note.getTitle() + " " + note.getContent());
            for (String word : words) {
                if (word.length() < 2) {
                    continue;
                }
                index.computeIfAbsent(word.toLowerCase(), k -> new ArrayList<>())
                        .add(note.hashCode());
            }
        }

        logger.info("索引构建完成，共 {} 个词", index.size());
        return index;
    }

    private Set<String> extractWords(String text) {
        Set<String> words = new HashSet<>();
        Pattern pattern = Pattern.compile("[\\w\\u4e00-\\u9fff]+");
        java.util.regex.Matcher matcher = pattern.matcher(text.toLowerCase());
        while (matcher.find()) {
            words.add(matcher.group());
        }
        return words;
    }

    private void saveSearchHistory(String query, SearchHistory.SearchType type, int resultCount) {
        List<SearchHistory> history = getSearchHistory();
        history.add(0, new SearchHistory(query, type, resultCount));

        if (history.size() > MAX_SEARCH_HISTORY_LIMIT) {
            history = history.subList(0, MAX_SEARCH_HISTORY_LIMIT);
        }

        storageService.saveList(history, FileStorageService.getSearchHistoryFile());
    }

    public List<SearchHistory> getSearchHistory() {
        return storageService.loadList(SearchHistory.class, FileStorageService.getSearchHistoryFile());
    }

    public void clearSearchHistory() {
        storageService.saveList(new ArrayList<>(), FileStorageService.getSearchHistoryFile());
        logger.info("搜索历史已清除");
    }

    public List<Note> highlightSearchResults(List<Note> notes, String keyword) {
        return notes;
    }
}
