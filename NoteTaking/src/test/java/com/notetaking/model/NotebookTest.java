package com.notetaking.model;

import org.junit.Test;

import static org.junit.Assert.*;

public class NotebookTest {

    @Test
    public void testCreateNotebook() {
        Notebook notebook = new Notebook("工作笔记");
        assertEquals("工作笔记", notebook.getName());
        assertNotNull(notebook.getId());
        assertNotNull(notebook.getCreatedAt());
        assertNotNull(notebook.getNoteIds());
        assertTrue(notebook.getNoteIds().isEmpty());
    }

    @Test
    public void testDefaultConstructor() {
        Notebook notebook = new Notebook();
        assertNotNull(notebook.getId());
        assertNotNull(notebook.getNoteIds());
    }

    @Test
    public void testAddNote() {
        Notebook notebook = new Notebook("笔记本");
        String noteId1 = "note-id-1";
        String noteId2 = "note-id-2";

        notebook.addNote(noteId1);
        assertEquals(1, notebook.getNoteIds().size());
        assertTrue(notebook.getNoteIds().contains(noteId1));

        notebook.addNote(noteId2);
        assertEquals(2, notebook.getNoteIds().size());
        assertTrue(notebook.getNoteIds().contains(noteId2));
    }

    @Test
    public void testAddDuplicateNote() {
        Notebook notebook = new Notebook("笔记本");
        String noteId = "note-id-1";

        notebook.addNote(noteId);
        notebook.addNote(noteId);
        assertEquals(1, notebook.getNoteIds().size());
    }

    @Test
    public void testRemoveNote() {
        Notebook notebook = new Notebook("笔记本");
        String noteId = "note-id-1";

        notebook.addNote(noteId);
        assertEquals(1, notebook.getNoteIds().size());

        notebook.removeNote(noteId);
        assertEquals(0, notebook.getNoteIds().size());
        assertFalse(notebook.getNoteIds().contains(noteId));
    }

    @Test
    public void testParentId() {
        Notebook notebook = new Notebook("子笔记本");
        assertNull(notebook.getParentId());

        String parentId = "parent-notebook-id";
        notebook.setParentId(parentId);
        assertEquals(parentId, notebook.getParentId());
    }

    @Test
    public void testDescription() {
        Notebook notebook = new Notebook("笔记本");
        assertNull(notebook.getDescription());

        notebook.setDescription("这是一个测试笔记本");
        assertEquals("这是一个测试笔记本", notebook.getDescription());
    }

    @Test
    public void testEqualsAndHashCode() {
        Notebook nb1 = new Notebook("笔记本1");
        Notebook nb2 = new Notebook("笔记本2");
        Notebook nb3 = nb1;

        assertNotEquals(nb1, nb2);
        assertEquals(nb1, nb3);
        assertNotEquals(nb1.hashCode(), nb2.hashCode());
        assertEquals(nb1.hashCode(), nb3.hashCode());
    }

    @Test
    public void testUpdatedAt() {
        Notebook notebook = new Notebook("笔记本");
        assertNotNull(notebook.getUpdatedAt());
        notebook.setName("新名称");
        assertNotNull(notebook.getUpdatedAt());
    }
}
