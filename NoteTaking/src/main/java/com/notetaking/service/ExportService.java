package com.notetaking.service;

import com.itextpdf.kernel.pdf.PdfDocument;
import com.itextpdf.kernel.pdf.PdfWriter;
import com.itextpdf.layout.Document;
import com.itextpdf.layout.element.Paragraph;
import com.itextpdf.layout.element.Text;
import com.itextpdf.layout.property.TextAlignment;
import org.apache.poi.xwpf.usermodel.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

public class ExportService {
    private static final Logger logger = LoggerFactory.getLogger(ExportService.class);

    private final MarkdownService markdownService;

    public ExportService() {
        this.markdownService = new MarkdownService();
    }

    public ExportService(MarkdownService markdownService) {
        this.markdownService = markdownService;
    }

    public boolean exportToHtml(String title, String content, String outputPath) {
        try {
            String html = markdownService.toHtmlWithStyle(content);
            Path path = Paths.get(outputPath);
            Files.write(path, html.getBytes(StandardCharsets.UTF_8));
            logger.info("导出HTML成功: {}", outputPath);
            return true;
        } catch (IOException e) {
            logger.error("导出HTML失败: {}", outputPath, e);
            return false;
        }
    }

    public boolean exportToMarkdown(String title, String content, String outputPath) {
        try {
            String markdown = "# " + title + "\n\n" + content;
            Path path = Paths.get(outputPath);
            Files.write(path, markdown.getBytes(StandardCharsets.UTF_8));
            logger.info("导出Markdown成功: {}", outputPath);
            return true;
        } catch (IOException e) {
            logger.error("导出Markdown失败: {}", outputPath, e);
            return false;
        }
    }

    public boolean exportToPlainText(String title, String content, String outputPath) {
        try {
            String plainText = title + "\n\n" + markdownService.getPlainText(content);
            Path path = Paths.get(outputPath);
            Files.write(path, plainText.getBytes(StandardCharsets.UTF_8));
            logger.info("导出纯文本成功: {}", outputPath);
            return true;
        } catch (IOException e) {
            logger.error("导出纯文本失败: {}", outputPath, e);
            return false;
        }
    }

    public boolean exportToPdf(String title, String content, String outputPath) {
        try {
            PdfWriter writer = new PdfWriter(outputPath);
            PdfDocument pdfDoc = new PdfDocument(writer);
            Document document = new Document(pdfDoc);

            Paragraph titlePara = new Paragraph(title)
                    .setFontSize(20)
                    .setBold()
                    .setTextAlignment(TextAlignment.CENTER);
            document.add(titlePara);

            Paragraph separator = new Paragraph("\n");
            document.add(separator);

            String[] lines = content.split("\n");
            for (String line : lines) {
                if (line.startsWith("# ")) {
                    Paragraph p = new Paragraph(line.substring(2))
                            .setFontSize(16)
                            .setBold();
                    document.add(p);
                } else if (line.startsWith("## ")) {
                    Paragraph p = new Paragraph(line.substring(3))
                            .setFontSize(14)
                            .setBold();
                    document.add(p);
                } else if (line.startsWith("### ")) {
                    Paragraph p = new Paragraph(line.substring(4))
                            .setFontSize(12)
                            .setBold();
                    document.add(p);
                } else if (line.startsWith("- ") || line.startsWith("* ")) {
                    Paragraph p = new Paragraph("• " + line.substring(2));
                    document.add(p);
                } else if (line.startsWith("> ")) {
                    Paragraph p = new Paragraph(line.substring(2))
                            .setItalic();
                    document.add(p);
                } else if (line.startsWith("```")) {
                    continue;
                } else if (line.trim().isEmpty()) {
                    document.add(new Paragraph(" "));
                } else {
                    Paragraph p = new Paragraph(line);
                    document.add(p);
                }
            }

            document.close();
            logger.info("导出PDF成功: {}", outputPath);
            return true;
        } catch (Exception e) {
            logger.error("导出PDF失败: {}", outputPath, e);
            return false;
        }
    }

    public boolean exportToWord(String title, String content, String outputPath) {
        try {
            XWPFDocument document = new XWPFDocument();

            XWPFParagraph titlePara = document.createParagraph();
            titlePara.setAlignment(ParagraphAlignment.CENTER);
            XWPFRun titleRun = titlePara.createRun();
            titleRun.setText(title);
            titleRun.setFontSize(20);
            titleRun.setBold(true);
            titleRun.addBreak();

            document.createParagraph();

            String[] lines = content.split("\n");
            for (String line : lines) {
                XWPFParagraph para = document.createParagraph();
                XWPFRun run = para.createRun();

                if (line.startsWith("# ")) {
                    para.setAlignment(ParagraphAlignment.LEFT);
                    run.setText(line.substring(2));
                    run.setFontSize(18);
                    run.setBold(true);
                } else if (line.startsWith("## ")) {
                    run.setText(line.substring(3));
                    run.setFontSize(16);
                    run.setBold(true);
                } else if (line.startsWith("### ")) {
                    run.setText(line.substring(4));
                    run.setFontSize(14);
                    run.setBold(true);
                } else if (line.startsWith("- ") || line.startsWith("* ")) {
                    para.setIndentationLeft(400);
                    run.setText("• " + line.substring(2));
                } else if (line.startsWith("> ")) {
                    para.setIndentationLeft(400);
                    run.setText(line.substring(2));
                    run.setItalic(true);
                } else if (line.startsWith("```")) {
                    continue;
                } else {
                    run.setText(line);
                }
            }

            try (FileOutputStream out = new FileOutputStream(outputPath)) {
                document.write(out);
            }
            document.close();

            logger.info("导出Word成功: {}", outputPath);
            return true;
        } catch (Exception e) {
            logger.error("导出Word失败: {}", outputPath, e);
            return false;
        }
    }

    public boolean batchExport(List<ExportItem> items, ExportFormat format, String outputDir) {
        try {
            Files.createDirectories(Paths.get(outputDir));

            for (ExportItem item : items) {
                String fileName = sanitizeFileName(item.getTitle()) + "." + format.getExtension();
                String outputPath = Paths.get(outputDir, fileName).toString();

                boolean success = false;
                switch (format) {
                    case PDF:
                        success = exportToPdf(item.getTitle(), item.getContent(), outputPath);
                        break;
                    case HTML:
                        success = exportToHtml(item.getTitle(), item.getContent(), outputPath);
                        break;
                    case WORD:
                        success = exportToWord(item.getTitle(), item.getContent(), outputPath);
                        break;
                    case MARKDOWN:
                        success = exportToMarkdown(item.getTitle(), item.getContent(), outputPath);
                        break;
                    case PLAIN_TEXT:
                        success = exportToPlainText(item.getTitle(), item.getContent(), outputPath);
                        break;
                }

                if (!success) {
                    logger.warn("批量导出失败: {}", item.getTitle());
                }
            }

            logger.info("批量导出完成: 共 {} 个文件", items.size());
            return true;
        } catch (Exception e) {
            logger.error("批量导出失败", e);
            return false;
        }
    }

    private String sanitizeFileName(String name) {
        if (name == null || name.isEmpty()) {
            return "untitled";
        }
        return name.replaceAll("[\\\\/:*?\"<>|]", "_");
    }

    public enum ExportFormat {
        PDF("pdf"),
        HTML("html"),
        WORD("docx"),
        MARKDOWN("md"),
        PLAIN_TEXT("txt");

        private final String extension;

        ExportFormat(String extension) {
            this.extension = extension;
        }

        public String getExtension() {
            return extension;
        }
    }

    public static class ExportItem {
        private String title;
        private String content;

        public ExportItem(String title, String content) {
            this.title = title;
            this.content = content;
        }

        public String getTitle() {
            return title;
        }

        public String getContent() {
            return content;
        }
    }
}
