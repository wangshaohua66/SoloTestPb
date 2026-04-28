package com.notetaking.model;

import org.junit.Test;

import static org.junit.Assert.*;

public class TagTest {

    @Test
    public void testCreateTag() {
        Tag tag = new Tag("工作");
        assertEquals("工作", tag.getName());
        assertNotNull(tag.getId());
        assertNotNull(tag.getCreatedAt());
        assertEquals("#6B7280", tag.getColor());
    }

    @Test
    public void testDefaultConstructor() {
        Tag tag = new Tag();
        assertNotNull(tag.getId());
        assertNotNull(tag.getCreatedAt());
    }

    @Test
    public void testSetName() {
        Tag tag = new Tag("旧名称");
        assertEquals("旧名称", tag.getName());
        tag.setName("新名称");
        assertEquals("新名称", tag.getName());
    }

    @Test
    public void testSetColor() {
        Tag tag = new Tag("标签");
        assertEquals("#6B7280", tag.getColor());
        tag.setColor("#FF0000");
        assertEquals("#FF0000", tag.getColor());
    }

    @Test
    public void testEqualsAndHashCode() {
        Tag tag1 = new Tag("标签1");
        Tag tag2 = new Tag("标签2");
        Tag tag3 = tag1;

        assertNotEquals(tag1, tag2);
        assertEquals(tag1, tag3);
        assertNotEquals(tag1.hashCode(), tag2.hashCode());
        assertEquals(tag1.hashCode(), tag3.hashCode());
    }

    @Test
    public void testUpdatedAt() {
        Tag tag = new Tag("标签");
        assertNotNull(tag.getUpdatedAt());
        tag.setName("新名称");
        assertNotNull(tag.getUpdatedAt());
    }
}
