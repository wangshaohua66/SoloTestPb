package com.notetaking;

import com.notetaking.model.Note;
import com.notetaking.model.Notebook;
import com.notetaking.model.Tag;
import com.notetaking.service.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.List;

public class CommandLineApp {
    private static final Logger logger = LoggerFactory.getLogger(CommandLineApp.class);

    private final NoteService noteService;
    private final NotebookService notebookService;
    private final TagService tagService;
    private final MarkdownService markdownService;
    private final SearchService searchService;
    private final EncryptionService encryptionService;
    private final ExportService exportService;
    private final StatisticsService statisticsService;
    private final BufferedReader reader;

    public CommandLineApp() {
        this.noteService = new NoteService();
        this.notebookService = new NotebookService();
        this.tagService = new TagService();
        this.markdownService = new MarkdownService();
        this.searchService = new SearchService();
        this.encryptionService = new EncryptionService();
        this.exportService = new ExportService();
        this.statisticsService = new StatisticsService();
        this.reader = new BufferedReader(new InputStreamReader(System.in));
    }

    public void run() {
        System.out.println("========================================");
        System.out.println("      本地笔记管理应用 (命令行模式)");
        System.out.println("========================================");
        System.out.println();

        try {
            while (true) {
                printMenu();
                String input = reader.readLine();
                if (input == null) {
                    break;
                }
                input = input.trim();

                switch (input) {
                    case "1":
                        createNote();
                        break;
                    case "2":
                        listNotes();
                        break;
                    case "3":
                        viewNote();
                        break;
                    case "4":
                        editNote();
                        break;
                    case "5":
                        deleteNote();
                        break;
                    case "6":
                        searchNotes();
                        break;
                    case "7":
                        testMarkdown();
                        break;
                    case "8":
                        testEncryption();
                        break;
                    case "9":
                        showStatistics();
                        break;
                    case "10":
                        createNotebook();
                        break;
                    case "11":
                        listNotebooks();
                        break;
                    case "12":
                        createTag();
                        break;
                    case "13":
                        listTags();
                        break;
                    case "14":
                        runTests();
                        break;
                    case "0":
                    case "q":
                    case "quit":
                        System.out.println("再见！");
                        return;
                    default:
                        System.out.println("无效的选择，请重试。");
                }
                System.out.println();
            }
        } catch (Exception e) {
            logger.error("应用运行出错", e);
            System.out.println("错误: " + e.getMessage());
        }
    }

    private void printMenu() {
        System.out.println("=== 主菜单 ===");
        System.out.println("笔记管理:");
        System.out.println("  1. 创建笔记");
        System.out.println("  2. 列出所有笔记");
        System.out.println("  3. 查看笔记");
        System.out.println("  4. 编辑笔记");
        System.out.println("  5. 删除笔记");
        System.out.println("  6. 搜索笔记");
        System.out.println();
        System.out.println("功能测试:");
        System.out.println("  7. 测试Markdown解析");
        System.out.println("  8. 测试加密功能");
        System.out.println("  9. 显示统计信息");
        System.out.println();
        System.out.println("组织管理:");
        System.out.println(" 10. 创建笔记本");
        System.out.println(" 11. 列出所有笔记本");
        System.out.println(" 12. 创建标签");
        System.out.println(" 13. 列出所有标签");
        System.out.println();
        System.out.println(" 14. 运行自动测试");
        System.out.println("  0. 退出");
        System.out.print("请选择: ");
    }

    private void createNote() throws Exception {
        System.out.print("输入笔记标题: ");
        String title = reader.readLine();
        if (title == null || title.trim().isEmpty()) {
            title = "未命名笔记";
        }

        System.out.println("输入笔记内容 (输入空行结束):");
        StringBuilder content = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null && !line.trim().isEmpty()) {
            content.append(line).append("\n");
        }

        Note note = noteService.createNote(title, content.toString().trim());
        System.out.println("笔记已创建! ID: " + note.getId());
        logger.info("创建笔记: {} ({})", title, note.getId());
    }

    private void listNotes() {
        List<Note> notes = noteService.getAllNotes();
        if (notes.isEmpty()) {
            System.out.println("没有笔记。");
            return;
        }

        System.out.println("=== 笔记列表 ===");
        System.out.println();
        for (Note note : notes) {
            String favorite = note.isFavorite() ? "★ " : "";
            String encrypted = note.isEncrypted() ? "[加密]" : "";
            System.out.printf("[%s] %s%s%s%n", note.getId().substring(0, 8), favorite, note.getTitle(), encrypted);
            System.out.printf("    创建: %s, 更新: %s, 字数: %d%n",
                    note.getCreatedAt().format(java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm")),
                    note.getUpdatedAt().format(java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm")),
                    note.getWordCount());
            System.out.println();
        }
    }

    private void viewNote() throws Exception {
        System.out.print("输入笔记ID (或前8位字符): ");
        String idPrefix = reader.readLine();
        if (idPrefix == null || idPrefix.trim().isEmpty()) {
            return;
        }
        idPrefix = idPrefix.trim();

        Note foundNote = null;
        List<Note> notes = noteService.getAllNotes();
        for (Note note : notes) {
            if (note.getId().equals(idPrefix) || note.getId().startsWith(idPrefix)) {
                foundNote = note;
                break;
            }
        }

        if (foundNote == null) {
            System.out.println("找不到笔记。");
            return;
        }

        System.out.println("========================================");
        System.out.println("标题: " + foundNote.getTitle());
        System.out.println("ID: " + foundNote.getId());
        System.out.println("收藏: " + (foundNote.isFavorite() ? "是" : "否"));
        System.out.println("加密: " + (foundNote.isEncrypted() ? "是" : "否"));
        System.out.println("========================================");
        System.out.println("内容:");
        System.out.println(foundNote.getContent());
        System.out.println("========================================");

        System.out.print("查看HTML预览? (y/n): ");
        String choice = reader.readLine();
        if (choice != null && choice.trim().equalsIgnoreCase("y")) {
            String html = markdownService.toHtmlWithStyle(foundNote.getContent());
            System.out.println("\n--- HTML预览 ---");
            System.out.println(html);
        }
    }

    private void editNote() throws Exception {
        System.out.print("输入要编辑的笔记ID (或前8位字符): ");
        String idPrefix = reader.readLine();
        if (idPrefix == null || idPrefix.trim().isEmpty()) {
            return;
        }
        idPrefix = idPrefix.trim();

        Note foundNote = null;
        List<Note> notes = noteService.getAllNotes();
        for (Note note : notes) {
            if (note.getId().equals(idPrefix) || note.getId().startsWith(idPrefix)) {
                foundNote = note;
                break;
            }
        }

        if (foundNote == null) {
            System.out.println("找不到笔记。");
            return;
        }

        System.out.println("当前标题: " + foundNote.getTitle());
        System.out.print("新标题 (留空保持不变): ");
        String newTitle = reader.readLine();
        if (newTitle != null && !newTitle.trim().isEmpty()) {
            foundNote.setTitle(newTitle.trim());
        }

        System.out.println("当前内容:");
        System.out.println(foundNote.getContent());
        System.out.println();
        System.out.println("输入新内容 (输入空行结束，留空保持不变):");

        StringBuilder newContent = new StringBuilder();
        String line;
        boolean hasContent = false;
        while ((line = reader.readLine()) != null && !line.trim().isEmpty()) {
            newContent.append(line).append("\n");
            hasContent = true;
        }

        if (hasContent) {
            foundNote.setContent(newContent.toString().trim());
        }

        noteService.updateNote(foundNote);
        System.out.println("笔记已更新!");
    }

    private void deleteNote() throws Exception {
        System.out.print("输入要删除的笔记ID (或前8位字符): ");
        String idPrefix = reader.readLine();
        if (idPrefix == null || idPrefix.trim().isEmpty()) {
            return;
        }
        idPrefix = idPrefix.trim();

        Note foundNote = null;
        List<Note> notes = noteService.getAllNotes();
        for (Note note : notes) {
            if (note.getId().equals(idPrefix) || note.getId().startsWith(idPrefix)) {
                foundNote = note;
                break;
            }
        }

        if (foundNote == null) {
            System.out.println("找不到笔记。");
            return;
        }

        System.out.print("确定要删除笔记 \"" + foundNote.getTitle() + "\"? (y/n): ");
        String choice = reader.readLine();
        if (choice != null && choice.trim().equalsIgnoreCase("y")) {
            boolean deleted = noteService.deleteNote(foundNote.getId());
            if (deleted) {
                System.out.println("笔记已删除。");
            } else {
                System.out.println("删除失败。");
            }
        } else {
            System.out.println("取消删除。");
        }
    }

    private void searchNotes() throws Exception {
        System.out.print("输入搜索关键词: ");
        String keyword = reader.readLine();
        if (keyword == null || keyword.trim().isEmpty()) {
            return;
        }

        List<Note> results = searchService.search(keyword.trim());
        if (results.isEmpty()) {
            System.out.println("没有找到匹配的笔记。");
            return;
        }

        System.out.println("找到 " + results.size() + " 篇笔记:");
        for (Note note : results) {
            System.out.printf("[%s] %s%n", note.getId().substring(0, 8), note.getTitle());
        }
    }

    private void testMarkdown() throws Exception {
        System.out.println("=== Markdown解析测试 ===");
        System.out.println();

        String testMarkdown = "# 测试标题\n\n" +
                "这是**粗体**和*斜体*文本。\n\n" +
                "## 二级标题\n\n" +
                "- 列表项1\n" +
                "- 列表项2\n" +
                "- 列表项3\n\n" +
                "| 列1 | 列2 | 列3 |\n" +
                "| --- | --- | --- |\n" +
                "| A | B | C |\n" +
                "| D | E | F |\n\n" +
                "> 这是引用文本\n\n" +
                "```java\n" +
                "public class Hello {\n" +
                "    public static void main(String[] args) {\n" +
                "        System.out.println(\"Hello!\");\n" +
                "    }\n" +
                "}\n" +
                "```\n";

        System.out.println("--- 原始Markdown ---");
        System.out.println(testMarkdown);
        System.out.println();

        String html = markdownService.toHtmlWithStyle(testMarkdown);
        System.out.println("--- 生成的HTML ---");
        System.out.println(html);
        System.out.println();

        String plainText = markdownService.getPlainText(testMarkdown);
        System.out.println("--- 纯文本提取 ---");
        System.out.println(plainText);
        System.out.println();

        int wordCount = markdownService.getWordCount(testMarkdown);
        System.out.println("字数统计: " + wordCount + " 字");
    }

    private void testEncryption() throws Exception {
        System.out.println("=== 加密功能测试 ===");
        System.out.println();

        String plainText = "这是一段需要加密的敏感文本。包含特殊字符: !@#$%^&*()";
        String password = "testPassword123";
        String wrongPassword = "wrongPassword";

        System.out.println("原始文本: " + plainText);
        System.out.println("密码: " + password);
        System.out.println();

        String encrypted = encryptionService.encrypt(plainText, password);
        System.out.println("加密后: " + encrypted);
        System.out.println();

        System.out.print("用正确密码解密: ");
        try {
            String decrypted = encryptionService.decrypt(encrypted, password);
            System.out.println("成功: " + decrypted);
            System.out.println("验证: " + (plainText.equals(decrypted) ? "通过" : "失败"));
        } catch (Exception e) {
            System.out.println("失败: " + e.getMessage());
        }
        System.out.println();

        System.out.print("用错误密码解密: ");
        try {
            encryptionService.decrypt(encrypted, wrongPassword);
            System.out.println("不应该成功!");
        } catch (Exception e) {
            System.out.println("预期行为: " + e.getMessage());
        }
        System.out.println();

        System.out.println("密码验证测试:");
        String hash = encryptionService.hashPassword(password);
        System.out.println("密码哈希: " + hash);
        System.out.println("正确密码验证: " + encryptionService.verifyPassword(password, hash));
        System.out.println("错误密码验证: " + encryptionService.verifyPassword(wrongPassword, hash));
    }

    private void showStatistics() {
        System.out.println("=== 统计信息 ===");
        System.out.println();

        String report = statisticsService.generateStatisticsReport();
        System.out.println(report);
    }

    private void createNotebook() throws Exception {
        System.out.print("输入笔记本名称: ");
        String name = reader.readLine();
        if (name == null || name.trim().isEmpty()) {
            System.out.println("名称不能为空。");
            return;
        }

        System.out.print("输入描述 (可选): ");
        String desc = reader.readLine();

        Notebook notebook = notebookService.createNotebook(name.trim());
        if (desc != null && !desc.trim().isEmpty()) {
            notebook.setDescription(desc.trim());
            notebookService.updateNotebook(notebook);
        }

        System.out.println("笔记本已创建! ID: " + notebook.getId());
    }

    private void listNotebooks() {
        List<Notebook> notebooks = notebookService.getAllNotebooks();
        if (notebooks.isEmpty()) {
            System.out.println("没有笔记本。");
            return;
        }

        System.out.println("=== 笔记本列表 ===");
        for (Notebook nb : notebooks) {
            String parent = nb.getParentId() != null ? " (子笔记本)" : "";
            System.out.printf("[%s] %s%s - %d篇笔记%n",
                    nb.getId().substring(0, 8), nb.getName(), parent, nb.getNoteIds().size());
            if (nb.getDescription() != null && !nb.getDescription().isEmpty()) {
                System.out.println("    描述: " + nb.getDescription());
            }
        }
    }

    private void createTag() throws Exception {
        System.out.print("输入标签名称: ");
        String name = reader.readLine();
        if (name == null || name.trim().isEmpty()) {
            System.out.println("名称不能为空。");
            return;
        }

        System.out.print("输入颜色 (格式: #RRGGBB，可选): ");
        String color = reader.readLine();

        Tag tag;
        if (color != null && !color.trim().isEmpty() && color.startsWith("#")) {
            tag = tagService.createTag(name.trim(), color.trim());
        } else {
            tag = tagService.createTag(name.trim());
        }

        System.out.println("标签已创建! ID: " + tag.getId());
    }

    private void listTags() {
        List<Tag> tags = tagService.getAllTags();
        if (tags.isEmpty()) {
            System.out.println("没有标签。");
            return;
        }

        System.out.println("=== 标签列表 ===");
        for (Tag tag : tags) {
            int count = tagService.getTagUsageCount(tag.getId());
            System.out.printf("[%s] %s (颜色: %s, 使用: %d次)%n",
                    tag.getId().substring(0, 8), tag.getName(), tag.getColor(), count);
        }
    }

    private void runTests() {
        System.out.println("=== 运行自动测试 ===");
        System.out.println();

        int passed = 0;
        int failed = 0;

        System.out.print("1. 测试笔记创建... ");
        try {
            Note note = noteService.createNote("测试笔记_" + System.currentTimeMillis(), "测试内容");
            System.out.println("通过 (ID: " + note.getId() + ")");
            passed++;

            System.out.print("2. 测试笔记保存... ");
            note.setTitle("更新后的标题");
            noteService.updateNote(note);
            Note loaded = noteService.getNoteById(note.getId());
            if (loaded != null && "更新后的标题".equals(loaded.getTitle())) {
                System.out.println("通过");
                passed++;
            } else {
                System.out.println("失败");
                failed++;
            }

            System.out.print("3. 测试笔记删除... ");
            boolean deleted = noteService.deleteNote(note.getId());
            if (deleted) {
                System.out.println("通过");
                passed++;
            } else {
                System.out.println("失败");
                failed++;
            }
        } catch (Exception e) {
            System.out.println("错误: " + e.getMessage());
            failed++;
        }

        System.out.print("4. 测试Markdown解析... ");
        try {
            String html = markdownService.toHtml("# 测试");
            if (html != null && html.contains("h1")) {
                System.out.println("通过");
                passed++;
            } else {
                System.out.println("失败");
                failed++;
            }
        } catch (Exception e) {
            System.out.println("错误: " + e.getMessage());
            failed++;
        }

        System.out.print("5. 测试加密/解密... ");
        try {
            String text = "测试文本";
            String password = "test123";
            String encrypted = encryptionService.encrypt(text, password);
            String decrypted = encryptionService.decrypt(encrypted, password);
            if (text.equals(decrypted)) {
                System.out.println("通过");
                passed++;
            } else {
                System.out.println("失败");
                failed++;
            }
        } catch (Exception e) {
            System.out.println("错误: " + e.getMessage());
            failed++;
        }

        System.out.print("6. 测试笔记本创建... ");
        try {
            Notebook nb = notebookService.createNotebook("测试笔记本_" + System.currentTimeMillis());
            System.out.println("通过 (ID: " + nb.getId().substring(0, 8) + ")");
            passed++;
        } catch (Exception e) {
            System.out.println("错误: " + e.getMessage());
            failed++;
        }

        System.out.print("7. 测试标签创建... ");
        try {
            Tag tag = tagService.createTag("测试标签_" + System.currentTimeMillis());
            System.out.println("通过 (ID: " + tag.getId().substring(0, 8) + ")");
            passed++;
        } catch (Exception e) {
            System.out.println("错误: " + e.getMessage());
            failed++;
        }

        System.out.print("8. 测试搜索功能... ");
        try {
            List<Note> results = searchService.search("不存在的关键词_xyz_123");
            System.out.println("通过 (空结果: " + (results.isEmpty() ? "是" : "否") + ")");
            passed++;
        } catch (Exception e) {
            System.out.println("错误: " + e.getMessage());
            failed++;
        }

        System.out.println();
        System.out.println("=== 测试结果 ===");
        System.out.println("通过: " + passed);
        System.out.println("失败: " + failed);
        System.out.println("总计: " + (passed + failed));
    }

    public static void main(String[] args) {
        System.out.println("启动命令行笔记管理应用...");
        CommandLineApp app = new CommandLineApp();
        app.run();
    }
}
