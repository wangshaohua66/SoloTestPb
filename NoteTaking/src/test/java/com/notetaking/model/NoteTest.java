package com.notetaking.model;

import org.junit.Test;

import static org.junit.Assert.*;

public class NoteTest {

    @Test
    public void testCreateNote() {
        Note note = new Note("测试标题", "测试内容");
        assertEquals("测试标题", note.getTitle());
        assertEquals("测试内容", note.getContent());
        assertNotNull(note.getId());
        assertNotNull(note.getCreatedAt());
        assertNotNull(note.getUpdatedAt());
        assertFalse(note.isFavorite());
        assertFalse(note.isEncrypted());
    }

    @Test
    public void testDefaultConstructor() {
        Note note = new Note();
        assertEquals("未命名笔记", note.getTitle());
        assertEquals("", note.getContent());
        assertNotNull(note.getId());
    }

    @Test
    public void testUpdateContent() {
        Note note = new Note("标题", "内容");
        int initialWordCount = note.getWordCount();
        note.updateContent("新的内容 更长的内容");
        assertEquals("新的内容 更长的内容", note.getContent());
        assertNotEquals(initialWordCount, note.getWordCount());
    }

    @Test
    public void testAddTag() {
        Note note = new Note("标题", "内容");
        String tagId = "test-tag-id";
        note.addTag(tagId);
        assertTrue(note.getTagIds().contains(tagId));
    }

    @Test
    public void testRemoveTag() {
        Note note = new Note("标题", "内容");
        String tagId = "test-tag-id";
        note.addTag(tagId);
        assertTrue(note.getTagIds().contains(tagId));
        note.removeTag(tagId);
        assertFalse(note.getTagIds().contains(tagId));
    }

    @Test
    public void testToggleFavorite() {
        Note note = new Note("标题", "内容");
        assertFalse(note.isFavorite());
        note.setFavorite(true);
        assertTrue(note.isFavorite());
    }

    @Test
    public void testEncrypted() {
        Note note = new Note("标题", "内容");
        assertFalse(note.isEncrypted());
        note.setEncrypted(true);
        assertTrue(note.isEncrypted());
    }

    @Test
    public void testWordCount() {
        Note note = new Note("标题", "Hello World 你好 世界");
        assertTrue(note.getWordCount() > 0);
    }

    @Test
    public void testEqualsAndHashCode() {
        Note note1 = new Note("标题1", "内容1");
        Note note2 = new Note("标题2", "内容2");
        Note note3 = note1;

        assertNotEquals(note1, note2);
        assertEquals(note1, note3);
        assertNotEquals(note1.hashCode(), note2.hashCode());
        assertEquals(note1.hashCode(), note3.hashCode());
    }

    @Test
    public void testNotebookId() {
        Note note = new Note("标题", "内容");
        assertNull(note.getNotebookId());
        String notebookId = "test-notebook-id";
        note.setNotebookId(notebookId);
        assertEquals(notebookId, note.getNotebookId());
    }

    @Test
    public void testLastAccessedAt() {
        Note note = new Note("标题", "内容");
        assertNotNull(note.getLastAccessedAt());
    }
}
