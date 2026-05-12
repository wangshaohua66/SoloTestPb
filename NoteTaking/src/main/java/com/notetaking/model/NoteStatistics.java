package com.notetaking.model;

import java.time.LocalDate;

public class NoteStatistics {
    private int totalNotes;
    private int totalNotebooks;
    private int totalTags;
    private int totalWords;
    private int favoriteNotes;
    private int encryptedNotes;
    private LocalDate statisticsDate;

    public NoteStatistics() {
        this.statisticsDate = LocalDate.now();
    }

    public int getTotalNotes() {
        return totalNotes;
    }

    public void setTotalNotes(int totalNotes) {
        this.totalNotes = totalNotes;
    }

    public int getTotalNotebooks() {
        return totalNotebooks;
    }

    public void setTotalNotebooks(int totalNotebooks) {
        this.totalNotebooks = totalNotebooks;
    }

    public int getTotalTags() {
        return totalTags;
    }

    public void setTotalTags(int totalTags) {
        this.totalTags = totalTags;
    }

    public int getTotalWords() {
        return totalWords;
    }

    public void setTotalWords(int totalWords) {
        this.totalWords = totalWords;
    }

    public int getFavoriteNotes() {
        return favoriteNotes;
    }

    public void setFavoriteNotes(int favoriteNotes) {
        this.favoriteNotes = favoriteNotes;
    }

    public int getEncryptedNotes() {
        return encryptedNotes;
    }

    public void setEncryptedNotes(int encryptedNotes) {
        this.encryptedNotes = encryptedNotes;
    }

    public LocalDate getStatisticsDate() {
        return statisticsDate;
    }

    public void setStatisticsDate(LocalDate statisticsDate) {
        this.statisticsDate = statisticsDate;
    }
}
