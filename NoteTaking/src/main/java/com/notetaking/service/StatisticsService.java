package com.notetaking.service;

import com.notetaking.model.Note;
import com.notetaking.model.NoteStatistics;
import com.notetaking.model.Notebook;
import com.notetaking.model.Tag;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.List;

public class StatisticsService {
    private static final Logger logger = LoggerFactory.getLogger(StatisticsService.class);

    private final NoteService noteService;
    private final NotebookService notebookService;
    private final TagService tagService;

    public StatisticsService() {
        this.noteService = new NoteService();
        this.notebookService = new NotebookService();
        this.tagService = new TagService();
    }

    public StatisticsService(NoteService noteService, NotebookService notebookService, TagService tagService) {
        this.noteService = noteService;
        this.notebookService = notebookService;
        this.tagService = tagService;
    }

    public NoteStatistics getStatistics() {
        List<Note> allNotes = noteService.getAllNotes();
        List<Notebook> allNotebooks = notebookService.getAllNotebooks();
        List<Tag> allTags = tagService.getAllTags();

        NoteStatistics stats = new NoteStatistics();
        stats.setTotalNotes(allNotes.size());
        stats.setTotalNotebooks(allNotebooks.size());
        stats.setTotalTags(allTags.size());
        stats.setTotalWords(noteService.getTotalWordCount());

        int favoriteCount = (int) allNotes.stream()
                .filter(Note::isFavorite)
                .count();
        stats.setFavoriteNotes(favoriteCount);

        int encryptedCount = (int) allNotes.stream()
                .filter(Note::isEncrypted)
                .count();
        stats.setEncryptedNotes(encryptedCount);

        return stats;
    }

    public int getNotesCreatedToday() {
        LocalDate today = LocalDate.now();
        List<Note> allNotes = noteService.getAllNotes();
        return (int) allNotes.stream()
                .filter(note -> note.getCreatedAt().toLocalDate().equals(today))
                .count();
    }

    public int getNotesCreatedThisWeek() {
        LocalDate weekStart = LocalDate.now().minusDays(7);
        List<Note> allNotes = noteService.getAllNotes();
        return (int) allNotes.stream()
                .filter(note -> note.getCreatedAt().toLocalDate().isAfter(weekStart)
                        || note.getCreatedAt().toLocalDate().equals(weekStart))
                .count();
    }

    public int getNotesCreatedThisMonth() {
        LocalDate monthStart = LocalDate.now().withDayOfMonth(1);
        List<Note> allNotes = noteService.getAllNotes();
        return (int) allNotes.stream()
                .filter(note -> note.getCreatedAt().toLocalDate().isAfter(monthStart.minusDays(1)))
                .count();
    }

    public String getMostActiveNotebook() {
        List<Notebook> notebooks = notebookService.getAllNotebooks();
        if (notebooks.isEmpty()) {
            return "无";
        }

        Notebook mostActive = notebooks.stream()
                .max((n1, n2) -> Integer.compare(n1.getNoteIds().size(), n2.getNoteIds().size()))
                .orElse(null);

        return mostActive != null ? mostActive.getName() : "无";
    }

    public String getMostUsedTag() {
        List<Tag> tags = tagService.getAllTags();
        if (tags.isEmpty()) {
            return "无";
        }

        Tag mostUsed = null;
        int maxCount = 0;

        for (Tag tag : tags) {
            int count = tagService.getTagUsageCount(tag.getId());
            if (count > maxCount) {
                maxCount = count;
                mostUsed = tag;
            }
        }

        return mostUsed != null ? mostUsed.getName() + " (" + maxCount + "次)" : "无";
    }

    public double getAverageNoteLength() {
        List<Note> notes = noteService.getAllNotes();
        if (notes.isEmpty()) {
            return 0.0;
        }
        int totalWords = notes.stream().mapToInt(Note::getWordCount).sum();
        return (double) totalWords / notes.size();
    }

    public String generateStatisticsReport() {
        NoteStatistics stats = getStatistics();
        StringBuilder report = new StringBuilder();

        report.append("=== 笔记统计报告 ===\n\n");
        report.append("生成时间: ").append(LocalDateTime.now()).append("\n\n");

        report.append("--- 总览 ---\n");
        report.append("笔记总数: ").append(stats.getTotalNotes()).append("\n");
        report.append("笔记本总数: ").append(stats.getTotalNotebooks()).append("\n");
        report.append("标签总数: ").append(stats.getTotalTags()).append("\n");
        report.append("总字数: ").append(stats.getTotalWords()).append("\n");
        report.append("平均字数: ").append(String.format("%.2f", getAverageNoteLength())).append("\n\n");

        report.append("--- 分类统计 ---\n");
        report.append("收藏笔记: ").append(stats.getFavoriteNotes()).append("\n");
        report.append("加密笔记: ").append(stats.getEncryptedNotes()).append("\n\n");

        report.append("--- 活跃度 ---\n");
        report.append("今日新增: ").append(getNotesCreatedToday()).append(" 篇\n");
        report.append("本周新增: ").append(getNotesCreatedThisWeek()).append(" 篇\n");
        report.append("本月新增: ").append(getNotesCreatedThisMonth()).append(" 篇\n\n");

        report.append("--- 热门 ---\n");
        report.append("最活跃笔记本: ").append(getMostActiveNotebook()).append("\n");
        report.append("最常用标签: ").append(getMostUsedTag()).append("\n");

        return report.toString();
    }
}
