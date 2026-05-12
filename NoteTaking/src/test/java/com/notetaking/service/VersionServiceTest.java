package com.notetaking.service;

import com.notetaking.model.Note;
import com.notetaking.model.NoteVersion;
import org.junit.Before;
import org.junit.Test;

import static org.junit.Assert.*;

public class VersionServiceTest {

    private VersionService versionService;

    @Before
    public void setUp() {
        versionService = new VersionService();
    }

    @Test
    public void testCreateNoteVersion() {
        Note note = new Note("测试标题", "测试内容");
        NoteVersion version = new NoteVersion(note);

        assertNotNull(version);
        assertNotNull(version.getId());
        assertEquals(note.getId(), version.getNoteId());
        assertEquals(note.getTitle(), version.getTitle());
        assertEquals(note.getContent(), version.getContent());
        assertNotNull(version.getCreatedAt());
    }

    @Test
    public void testVersionNumber() {
        Note note = new Note("测试", "内容");
        NoteVersion version = new NoteVersion(note);
        version.setVersionNumber("v_20240101_120000");

        assertEquals("v_20240101_120000", version.getVersionNumber());
    }

    @Test
    public void testRestoreVersion() {
        Note originalNote = new Note("原始标题", "原始内容");
        NoteVersion version = new NoteVersion(originalNote);

        Note noteToRestore = new Note("新标题", "新内容");
        assertNotEquals(originalNote.getTitle(), noteToRestore.getTitle());
        assertNotEquals(originalNote.getContent(), noteToRestore.getContent());

        versionService.restoreVersion(noteToRestore, version);

        assertEquals(originalNote.getTitle(), noteToRestore.getTitle());
        assertEquals(originalNote.getContent(), noteToRestore.getContent());
    }

    @Test
    public void testCompareVersions() {
        Note note1 = new Note("标题1", "内容1");
        Note note2 = new Note("标题2", "内容2");

        NoteVersion v1 = new NoteVersion(note1);
        v1.setVersionNumber("v1");
        NoteVersion v2 = new NoteVersion(note2);
        v2.setVersionNumber("v2");

        String diff = versionService.compareVersions(v1, v2);

        assertNotNull(diff);
        assertTrue(diff.length() > 0);
    }

    @Test
    public void testDefaultConstructor() {
        NoteVersion version = new NoteVersion();
        assertNotNull(version);
        assertNotNull(version.getId());
        assertNotNull(version.getCreatedAt());
    }

    @Test
    public void testSettersAndGetters() {
        NoteVersion version = new NoteVersion();
        version.setNoteId("test-note-id");
        version.setTitle("测试标题");
        version.setContent("测试内容");
        version.setVersionNumber("v1.0");

        assertEquals("test-note-id", version.getNoteId());
        assertEquals("测试标题", version.getTitle());
        assertEquals("测试内容", version.getContent());
        assertEquals("v1.0", version.getVersionNumber());
    }

    @Test
    public void testVersionDate() {
        NoteVersion version = new NoteVersion();
        assertNotNull(version.getCreatedAt());
    }
}
