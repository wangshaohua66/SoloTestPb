package com.notetaking.service;

import com.notetaking.model.Note;
import org.junit.Before;
import org.junit.Test;

import static org.junit.Assert.*;

public class MarkdownServiceTest {

    private MarkdownService markdownService;

    @Before
    public void setUp() {
        markdownService = new MarkdownService();
    }

    @Test
    public void testToHtml() {
        String markdown = "# 标题\n\n这是**粗体**和*斜体*。";
        String html = markdownService.toHtml(markdown);

        assertNotNull(html);
        assertTrue(html.contains("<h1>"));
        assertTrue(html.contains("<strong>"));
        assertTrue(html.contains("<em>"));
    }

    @Test
    public void testToHtmlWithEmptyContent() {
        assertEquals("", markdownService.toHtml(null));
        assertEquals("", markdownService.toHtml(""));
    }

    @Test
    public void testToHtmlWithTables() {
        String markdown = "| 列1 | 列2 |\n| --- | --- |\n| 单元格1 | 单元格2 |";
        String html = markdownService.toHtml(markdown);

        assertNotNull(html);
        assertTrue(html.contains("<table>") || html.contains("<thead>") || html.contains("<tbody>"));
    }

    @Test
    public void testToHtmlWithStrikethrough() {
        String markdown = "~~删除线~~";
        String html = markdownService.toHtml(markdown);

        assertNotNull(html);
    }

    @Test
    public void testGetPlainText() {
        String markdown = "# 标题\n\n这是**粗体**和[链接](http://example.com)。";
        String plainText = markdownService.getPlainText(markdown);

        assertNotNull(plainText);
        assertFalse(plainText.contains("#"));
        assertFalse(plainText.contains("**"));
        assertFalse(plainText.contains("http://"));
    }

    @Test
    public void testGetPlainTextWithNull() {
        assertEquals("", markdownService.getPlainText(null));
    }

    @Test
    public void testGetWordCount() {
        String markdown = "Hello World 你好 世界";
        int count = markdownService.getWordCount(markdown);
        assertTrue(count > 0);
    }

    @Test
    public void testGetWordCountWithEmptyContent() {
        assertEquals(0, markdownService.getWordCount(null));
        assertEquals(0, markdownService.getWordCount(""));
    }

    @Test
    public void testInsertHeading() {
        String h1 = markdownService.insertHeading("1");
        String h2 = markdownService.insertHeading("2");
        String h3 = markdownService.insertHeading("3");

        assertEquals("# ", h1);
        assertEquals("## ", h2);
        assertEquals("### ", h3);
    }

    @Test
    public void testInsertBold() {
        assertEquals("**加粗文字**", markdownService.insertBold());
    }

    @Test
    public void testInsertItalic() {
        assertEquals("*斜体文字*", markdownService.insertItalic());
    }

    @Test
    public void testInsertCode() {
        assertEquals("`代码`", markdownService.insertCode());
    }

    @Test
    public void testInsertCodeBlock() {
        String codeBlock = markdownService.insertCodeBlock();
        assertTrue(codeBlock.startsWith("```"));
        assertTrue(codeBlock.endsWith("```"));
    }

    @Test
    public void testInsertLink() {
        String link = markdownService.insertLink();
        assertTrue(link.contains("[") && link.contains("]") && link.contains("(") && link.contains(")"));
    }

    @Test
    public void testInsertList() {
        assertEquals("- 列表项", markdownService.insertList());
    }

    @Test
    public void testInsertNumberedList() {
        assertEquals("1. 列表项", markdownService.insertNumberedList());
    }

    @Test
    public void testInsertQuote() {
        assertEquals("> 引用文字", markdownService.insertQuote());
    }

    @Test
    public void testInsertTable() {
        String table = markdownService.insertTable();
        assertTrue(table.contains("|") && table.contains("---"));
    }

    @Test
    public void testInsertHorizontalRule() {
        assertEquals("---", markdownService.insertHorizontalRule());
    }

    @Test
    public void testToHtmlWithCodeBlock() {
        String markdown = "```java\nSystem.out.println(\"Hello\");\n```";
        String html = markdownService.toHtml(markdown);
        assertNotNull(html);
    }

    @Test
    public void testToHtmlWithList() {
        String markdown = "- 项目1\n- 项目2\n- 项目3";
        String html = markdownService.toHtml(markdown);
        assertNotNull(html);
        assertTrue(html.contains("<ul>") || html.contains("<li>"));
    }

    @Test
    public void testToHtmlWithBlockquote() {
        String markdown = "> 这是引用文本";
        String html = markdownService.toHtml(markdown);
        assertNotNull(html);
        assertTrue(html.contains("<blockquote>"));
    }
}
