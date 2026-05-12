package com.notetaking.model;

import java.time.LocalDateTime;
import java.util.UUID;

public class SearchHistory {
    private String id;
    private String query;
    private SearchType searchType;
    private LocalDateTime searchedAt;
    private int resultCount;

    public enum SearchType {
        FULL_TEXT,
        TITLE,
        TAG,
        ADVANCED
    }

    public SearchHistory() {
        this.id = UUID.randomUUID().toString();
        this.searchedAt = LocalDateTime.now();
    }

    public SearchHistory(String query, SearchType searchType, int resultCount) {
        this();
        this.query = query;
        this.searchType = searchType;
        this.resultCount = resultCount;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getQuery() {
        return query;
    }

    public void setQuery(String query) {
        this.query = query;
    }

    public SearchType getSearchType() {
        return searchType;
    }

    public void setSearchType(SearchType searchType) {
        this.searchType = searchType;
    }

    public LocalDateTime getSearchedAt() {
        return searchedAt;
    }

    public void setSearchedAt(LocalDateTime searchedAt) {
        this.searchedAt = searchedAt;
    }

    public int getResultCount() {
        return resultCount;
    }

    public void setResultCount(int resultCount) {
        this.resultCount = resultCount;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        SearchHistory that = (SearchHistory) o;
        return id.equals(that.id);
    }

    @Override
    public int hashCode() {
        return id.hashCode();
    }
}
