package com.notetaking.service;

import org.commonmark.Extension;
import org.commonmark.ext.gfm.strikethrough.StrikethroughExtension;
import org.commonmark.ext.gfm.tables.TablesExtension;
import org.commonmark.node.Node;
import org.commonmark.parser.Parser;
import org.commonmark.renderer.html.HtmlRenderer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Arrays;
import java.util.List;

public class MarkdownService {
    private static final Logger logger = LoggerFactory.getLogger(MarkdownService.class);

    private final Parser parser;
    private final HtmlRenderer renderer;

    public MarkdownService() {
        List<Extension> extensions = Arrays.asList(
                TablesExtension.create(),
                StrikethroughExtension.create()
        );

        this.parser = Parser.builder()
                .extensions(extensions)
                .build();

        this.renderer = HtmlRenderer.builder()
                .extensions(extensions)
                .escapeHtml(false)
                .build();
    }

    public String toHtml(String markdown) {
        if (markdown == null || markdown.isEmpty()) {
            return "";
        }
        try {
            Node document = parser.parse(markdown);
            return renderer.render(document);
        } catch (Exception e) {
            logger.error("Markdown解析失败", e);
            return "<p>解析错误: " + e.getMessage() + "</p>";
        }
    }

    public String toHtmlWithStyle(String markdown) {
        String htmlContent = toHtml(markdown);
        return wrapWithCss(htmlContent);
    }

    private String wrapWithCss(String content) {
        return "<!DOCTYPE html>\n" +
                "<html>\n" +
                "<head>\n" +
                "    <meta charset=\"UTF-8\">\n" +
                "    <style>\n" +
                "        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; padding: 20px; max-width: 900px; margin: 0 auto; }\n" +
                "        h1, h2, h3, h4, h5, h6 { margin-top: 24px; margin-bottom: 16px; font-weight: 600; line-height: 1.25; }\n" +
                "        h1 { font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }\n" +
                "        h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }\n" +
                "        h3 { font-size: 1.25em; }\n" +
                "        p { margin-top: 0; margin-bottom: 16px; }\n" +
                "        code { font-family: 'SFMono-Regular', Consolas, monospace; background-color: #f6f8fa; padding: 0.2em 0.4em; border-radius: 3px; font-size: 85%; }\n" +
                "        pre { background-color: #f6f8fa; padding: 16px; border-radius: 6px; overflow: auto; margin-bottom: 16px; }\n" +
                "        pre code { background-color: transparent; padding: 0; }\n" +
                "        blockquote { margin: 0; padding: 0 1em; color: #6a737d; border-left: 0.25em solid #dfe2e5; }\n" +
                "        ul, ol { padding-left: 2em; margin-top: 0; margin-bottom: 16px; }\n" +
                "        li { margin-top: 0.25em; }\n" +
                "        table { border-spacing: 0; border-collapse: collapse; width: 100%; margin-bottom: 16px; }\n" +
                "        table th, table td { padding: 6px 13px; border: 1px solid #dfe2e5; }\n" +
                "        table th { font-weight: 600; background-color: #f6f8fa; }\n" +
                "        table tr:nth-child(2n) { background-color: #f6f8fa; }\n" +
                "        hr { height: 0.25em; padding: 0; margin: 24px 0; background-color: #e1e4e8; border: 0; }\n" +
                "        a { color: #0366d6; text-decoration: none; }\n" +
                "        a:hover { text-decoration: underline; }\n" +
                "        img { max-width: 100%; box-sizing: content-box; }\n" +
                "        del { color: #6a737d; }\n" +
                "    </style>\n" +
                "</head>\n" +
                "<body>\n" +
                content +
                "</body>\n" +
                "</html>";
    }

    public String getPlainText(String markdown) {
        if (markdown == null) {
            return "";
        }
        String text = markdown;
        text = text.replaceAll("#+\\s", "");
        text = text.replaceAll("\\*\\*([^*]+)\\*\\*", "$1");
        text = text.replaceAll("\\*([^*]+)\\*", "$1");
        text = text.replaceAll("__([^_]+)__", "$1");
        text = text.replaceAll("_([^_]+)_", "$1");
        text = text.replaceAll("`([^`]+)`", "$1");
        text = text.replaceAll("```[\\s\\S]*?```", "");
        text = text.replaceAll("!\\[[^\\]]*\\]\\([^)]+\\)", "");
        text = text.replaceAll("\\[([^\\]]+)\\]\\([^)]+\\)", "$1");
        text = text.replaceAll("^>\\s", "");
        text = text.replaceAll("^[-*+]\\s", "");
        text = text.replaceAll("^\\d+\\.\\s", "");
        return text.trim();
    }

    public int getWordCount(String markdown) {
        if (markdown == null || markdown.isEmpty()) {
            return 0;
        }
        String text = getPlainText(markdown);
        if (text.isEmpty()) {
            return 0;
        }
        return text.split("\\s+|(?=[\\u4e00-\\u9fff])|(?<=[\\u4e00-\\u9fff])").length;
    }

    public String insertHeading(String level) {
        int hLevel = Math.max(1, Math.min(6, Integer.parseInt(level)));
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < hLevel; i++) {
            sb.append("#");
        }
        sb.append(" ");
        return sb.toString();
    }

    public String insertBold() {
        return "**加粗文字**";
    }

    public String insertItalic() {
        return "*斜体文字*";
    }

    public String insertCode() {
        return "`代码`";
    }

    public String insertCodeBlock() {
        return "```\n代码块\n```";
    }

    public String insertLink() {
        return "[链接文字](链接地址)";
    }

    public String insertImage() {
        return "![图片描述](图片路径)";
    }

    public String insertList() {
        return "- 列表项";
    }

    public String insertNumberedList() {
        return "1. 列表项";
    }

    public String insertQuote() {
        return "> 引用文字";
    }

    public String insertTable() {
        return "| 表头1 | 表头2 |\n| --- | --- |\n| 单元格1 | 单元格2 |";
    }

    public String insertHorizontalRule() {
        return "---";
    }
}
