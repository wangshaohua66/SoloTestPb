package com.notetaking.ui;

import com.notetaking.model.Note;
import com.notetaking.model.Notebook;
import com.notetaking.model.SearchHistory;
import com.notetaking.model.Tag;
import com.notetaking.service.*;
import javafx.application.Platform;
import javafx.beans.value.ObservableValue;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.concurrent.Task;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.geometry.Insets;
import javafx.scene.control.*;
import javafx.scene.input.*;
import javafx.scene.layout.*;
import javafx.scene.web.WebEngine;
import javafx.scene.web.WebView;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.net.URL;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.stream.Collectors;

public class MainController implements Initializable {
    private static final Logger logger = LoggerFactory.getLogger(MainController.class);
    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");

    private MainApp mainApp;

    private final NoteService noteService;
    private final NotebookService notebookService;
    private final TagService tagService;
    private final MarkdownService markdownService;
    private final SearchService searchService;
    private final ExportService exportService;
    private final VersionService versionService;
    private final TemplateService templateService;
    private final StatisticsService statisticsService;

    private Note currentNote;
    private boolean isNoteModified = false;
    private final ExecutorService executorService = Executors.newSingleThreadExecutor();

    private ContextMenu notebookContextMenu;
    private ContextMenu noteContextMenu;
    private ContextMenu tagContextMenu;

    private ObservableList<NoteListItem> noteListItems;
    private ObservableList<TagItem> tagItems;
    private Set<String> selectedNoteIds;
    private boolean isMultipleSelectionMode;

    @FXML private TreeView<NotebookTreeItem> notebookTreeView;
    @FXML private ListView<TagItem> tagListView;
    @FXML private ListView<NoteListItem> noteListView;
    @FXML private SplitPane mainSplitPane;
    @FXML private SplitPane editorSplitPane;
    @FXML private VBox leftPanel;
    @FXML private VBox editorArea;
    @FXML private VBox previewArea;

    @FXML private TextField noteTitleField;
    @FXML private TextArea markdownTextArea;
    @FXML private WebView previewWebView;
    private WebEngine previewEngine;

    @FXML private Label statusLabel;
    @FXML private Label wordCountLabel;

    @FXML private MenuItem newNoteMenuItem;
    @FXML private MenuItem saveNoteMenuItem;
    @FXML private MenuItem deleteNoteMenuItem;
    @FXML private MenuItem exportPdfMenuItem;
    @FXML private MenuItem exportHtmlMenuItem;
    @FXML private MenuItem exportWordMenuItem;

    @FXML private ComboBox<String> searchHistoryComboBox;

    public MainController() {
        FileStorageService sharedStorageService = new FileStorageService();
        VersionService sharedVersionService = new VersionService(sharedStorageService);
        this.noteService = new NoteService(sharedStorageService, sharedVersionService);
        this.notebookService = new NotebookService(sharedStorageService);
        this.tagService = new TagService(sharedStorageService);
        this.markdownService = new MarkdownService();
        this.searchService = new SearchService(noteService, sharedStorageService);
        this.exportService = new ExportService(markdownService);
        this.versionService = sharedVersionService;
        this.templateService = new TemplateService(sharedStorageService);
        this.statisticsService = new StatisticsService(noteService, notebookService, tagService);
        this.selectedNoteIds = new HashSet<>();
        this.isMultipleSelectionMode = false;
    }

    @Override
    public void initialize(URL location, ResourceBundle resources) {
        logger.info("初始化主控制器");

        noteListItems = FXCollections.observableArrayList();
        tagItems = FXCollections.observableArrayList();

        initializePreviewWebView();
        initializeNoteListView();
        initializeTagListView();
        initializeNotebookTree();
        initializeContextMenus();
        initializeSearchHistory();
        initializeEventHandlers();
        loadInitialData();
    }

    private void initializePreviewWebView() {
        previewEngine = previewWebView.getEngine();
        previewEngine.loadContent("<html><body style='font-family: sans-serif; padding: 20px;'><h3>选择或创建一个笔记开始编辑</h3></body></html>");
    }

    private void initializeNoteListView() {
        noteListView.setItems(noteListItems);
        noteListView.getSelectionModel().setSelectionMode(SelectionMode.MULTIPLE);
        noteListView.setCellFactory(param -> new ListCell<NoteListItem>() {
            @Override
            protected void updateItem(NoteListItem item, boolean empty) {
                super.updateItem(item, empty);
                if (empty || item == null) {
                    setText(null);
                    setGraphic(null);
                } else {
                    VBox box = new VBox(5);
                    box.setPadding(new Insets(8, 12, 8, 12));

                    HBox headerBox = new HBox(8);
                    Label titleLabel = new Label(item.getTitle());
                    titleLabel.setStyle("-fx-font-weight: bold; -fx-font-size: 14px;");

                    if (item.isFavorite()) {
                        Label starLabel = new Label("★");
                        starLabel.setStyle("-fx-text-fill: #FFD700;");
                        headerBox.getChildren().add(starLabel);
                    }
                    if (item.isEncrypted()) {
                        Label lockLabel = new Label("🔒");
                        headerBox.getChildren().add(lockLabel);
                    }
                    headerBox.getChildren().add(titleLabel);
                    HBox.setHgrow(titleLabel, Priority.ALWAYS);

                    Label previewLabel = new Label(item.getPreview());
                    previewLabel.setStyle("-fx-font-size: 12px; -fx-text-fill: #666;");

                    HBox infoBox = new HBox(15);
                    Label dateLabel = new Label(item.getUpdatedAt());
                    dateLabel.setStyle("-fx-font-size: 11px; -fx-text-fill: #999;");
                    Label wordCountLabel = new Label(item.getWordCount() + "字");
                    wordCountLabel.setStyle("-fx-font-size: 11px; -fx-text-fill: #999;");

                    infoBox.getChildren().addAll(dateLabel, wordCountLabel);

                    box.getChildren().addAll(headerBox, previewLabel, infoBox);
                    setGraphic(box);

                    setOnContextMenuRequested(event -> {
                        if (!isEmpty()) {
                            noteListView.getSelectionModel().select(getIndex());
                            noteContextMenu.show(this, event.getScreenX(), event.getScreenY());
                        }
                    });
                }
            }
        });
    }

    private void initializeTagListView() {
        tagListView.setItems(tagItems);
        tagListView.setCellFactory(param -> new ListCell<TagItem>() {
            @Override
            protected void updateItem(TagItem item, boolean empty) {
                super.updateItem(item, empty);
                if (empty || item == null) {
                    setText(null);
                    setGraphic(null);
                } else {
                    HBox box = new HBox(8);
                    box.setPadding(new Insets(5, 10, 5, 10));

                    Region colorIndicator = new Region();
                    colorIndicator.setMinSize(12, 12);
                    colorIndicator.setMaxSize(12, 12);
                    colorIndicator.setStyle("-fx-background-color: " + item.getColor() + "; -fx-background-radius: 6px;");

                    Label nameLabel = new Label(item.getName() + " (" + item.getCount() + ")");
                    nameLabel.setStyle("-fx-font-size: 13px;");

                    box.getChildren().addAll(colorIndicator, nameLabel);
                    setGraphic(box);

                    setOnContextMenuRequested(event -> {
                        if (!isEmpty()) {
                            tagListView.getSelectionModel().select(getIndex());
                            tagContextMenu.show(this, event.getScreenX(), event.getScreenY());
                        }
                    });
                }
            }
        });
    }

    private void initializeNotebookTree() {
        TreeItem<NotebookTreeItem> rootItem = new TreeItem<>(new NotebookTreeItem(null, "所有笔记"));
        rootItem.setExpanded(true);
        notebookTreeView.setRoot(rootItem);
        notebookTreeView.setShowRoot(true);

        notebookTreeView.setCellFactory(param -> new TreeCell<NotebookTreeItem>() {
            @Override
            protected void updateItem(NotebookTreeItem item, boolean empty) {
                super.updateItem(item, empty);
                if (empty || item == null) {
                    setText(null);
                    setGraphic(null);
                } else {
                    setText(item.getName());

                    setOnContextMenuRequested(event -> {
                        if (!isEmpty() && item.getId() != null) {
                            notebookTreeView.getSelectionModel().select(getIndex());
                            notebookContextMenu.show(this, event.getScreenX(), event.getScreenY());
                        }
                    });
                }
            }
        });
    }

    private void initializeContextMenus() {
        notebookContextMenu = new ContextMenu();
        MenuItem newNotebookItem = new MenuItem("新建笔记本");
        MenuItem newSubNotebookItem = new MenuItem("新建子笔记本");
        MenuItem renameNotebookItem = new MenuItem("重命名");
        MenuItem deleteNotebookItem = new MenuItem("删除");
        newNotebookItem.setOnAction(e -> handleCreateNotebook(null));
        newSubNotebookItem.setOnAction(e -> handleCreateSubNotebook());
        renameNotebookItem.setOnAction(e -> handleRenameNotebook());
        deleteNotebookItem.setOnAction(e -> handleDeleteNotebook());
        notebookContextMenu.getItems().addAll(newNotebookItem, newSubNotebookItem,
                new SeparatorMenuItem(), renameNotebookItem, deleteNotebookItem);

        noteContextMenu = new ContextMenu();
        MenuItem newNoteItem = new MenuItem("新建笔记");
        MenuItem editNoteItem = new MenuItem("编辑");
        MenuItem deleteNoteItem = new MenuItem("删除");
        MenuItem moveNoteItem = new MenuItem("移动到...");
        MenuItem addTagItem = new MenuItem("添加标签");
        MenuItem favoriteItem = new MenuItem("切换收藏");
        MenuItem exportNoteItem = new MenuItem("导出");
        MenuItem showVersionsItem = new MenuItem("版本历史");
        newNoteItem.setOnAction(e -> handleNewNote());
        editNoteItem.setOnAction(e -> editSelectedNote());
        deleteNoteItem.setOnAction(e -> handleDeleteSelectedNotes());
        moveNoteItem.setOnAction(e -> handleMoveNotes());
        addTagItem.setOnAction(e -> handleAddTagToNotes());
        favoriteItem.setOnAction(e -> handleToggleFavorite());
        exportNoteItem.setOnAction(e -> handleExportSelectedNotes());
        showVersionsItem.setOnAction(e -> handleShowVersions());
        noteContextMenu.getItems().addAll(newNoteItem, editNoteItem,
                new SeparatorMenuItem(), deleteNoteItem, moveNoteItem, addTagItem, favoriteItem,
                new SeparatorMenuItem(), exportNoteItem, showVersionsItem);

        tagContextMenu = new ContextMenu();
        MenuItem renameTagItem = new MenuItem("重命名");
        MenuItem deleteTagItem = new MenuItem("删除");
        MenuItem changeTagColorItem = new MenuItem("更改颜色");
        renameTagItem.setOnAction(e -> handleRenameTag());
        deleteTagItem.setOnAction(e -> handleDeleteTag());
        changeTagColorItem.setOnAction(e -> handleChangeTagColor());
        tagContextMenu.getItems().addAll(renameTagItem, changeTagColorItem,
                new SeparatorMenuItem(), deleteTagItem);
    }

    private void initializeSearchHistory() {
        searchHistoryComboBox.setItems(FXCollections.observableArrayList());
        searchHistoryComboBox.setEditable(true);
        searchHistoryComboBox.setPromptText("搜索笔记...");

        loadSearchHistory();

        searchHistoryComboBox.valueProperty().addListener(
                (obs, oldVal, newVal) -> {
                    if (newVal != null && !newVal.trim().isEmpty()) {
                        performSearch(newVal.trim());
                    } else {
                        loadAllNotes();
                    }
                }
        );
    }

    private void loadSearchHistory() {
        List<SearchHistory> history = searchService.getSearchHistory();
        ObservableList<String> historyItems = FXCollections.observableArrayList();
        for (SearchHistory item : history) {
            if (item.getQuery() != null && !item.getQuery().trim().isEmpty()) {
                historyItems.add(item.getQuery());
            }
        }
        searchHistoryComboBox.setItems(historyItems);
    }

    private void initializeEventHandlers() {
        if (newNoteMenuItem != null) {
            newNoteMenuItem.setAccelerator(new KeyCodeCombination(KeyCode.N, KeyCombination.CONTROL_DOWN));
        }
        if (saveNoteMenuItem != null) {
            saveNoteMenuItem.setAccelerator(new KeyCodeCombination(KeyCode.S, KeyCombination.CONTROL_DOWN));
        }

        noteListView.getSelectionModel().selectedItemProperty().addListener(
                (obs, oldVal, newVal) -> {
                    ObservableList<NoteListItem> selected = noteListView.getSelectionModel().getSelectedItems();
                    if (selected.size() == 1 && newVal != null) {
                        loadNote(newVal.getNoteId());
                    } else if (selected.size() > 1) {
                        statusLabel.setText("已选择 " + selected.size() + " 篇笔记");
                    }
                }
        );

        markdownTextArea.textProperty().addListener(
                (obs, oldVal, newVal) -> {
                    if (currentNote != null) {
                        isNoteModified = true;
                        updatePreviewAsync(newVal);
                        updateWordCount(newVal);
                    }
                }
        );

        noteTitleField.textProperty().addListener(
                (obs, oldVal, newVal) -> {
                    if (currentNote != null) {
                        isNoteModified = true;
                    }
                }
        );

        tagListView.getSelectionModel().selectedItemProperty().addListener(
                (obs, oldVal, newVal) -> {
                    if (newVal != null) {
                        loadNotesByTag(newVal.getTagId());
                    }
                }
        );

        notebookTreeView.getSelectionModel().selectedItemProperty().addListener(
                (obs, oldVal, newVal) -> {
                    if (newVal != null) {
                        loadNotesByNotebook(newVal);
                    }
                }
        );

        markdownTextArea.setOnKeyPressed(event -> {
            if (event.isControlDown() && event.getCode() == KeyCode.S) {
                handleSaveNote();
                event.consume();
            } else if (event.isControlDown() && event.getCode() == KeyCode.B) {
                insertMarkdown("**", "**");
                event.consume();
            } else if (event.isControlDown() && event.getCode() == KeyCode.I) {
                insertMarkdown("*", "*");
                event.consume();
            } else if (event.isControlDown() && event.getCode() == KeyCode.K) {
                insertMarkdown("[", "](url)");
                event.consume();
            }
        });
    }

    private void insertMarkdown(String before, String after) {
        int selectionStart = markdownTextArea.getSelection().getStart();
        int selectionEnd = markdownTextArea.getSelection().getEnd();
        String selectedText = markdownTextArea.getSelectedText();
        if (selectedText == null) selectedText = "";

        String newText = before + selectedText + after;
        markdownTextArea.replaceSelection(newText);

        int caretPosition = selectionStart + before.length() + selectedText.length();
        markdownTextArea.positionCaret(caretPosition);
    }

    private void updatePreviewAsync(String markdown) {
        Task<String> renderTask = new Task<String>() {
            @Override
            protected String call() throws Exception {
                return markdownService.toHtmlWithStyle(markdown);
            }
        };

        renderTask.setOnSucceeded(event -> {
            Platform.runLater(() -> {
                String html = renderTask.getValue();
                previewEngine.loadContent(html);
            });
        });

        executorService.submit(renderTask);
    }

    private void updateWordCount(String text) {
        int count = markdownService.getWordCount(text);
        wordCountLabel.setText(count + " 字");
    }

    private void loadInitialData() {
        loadAllNotebooks();
        loadAllTags();
        loadAllNotes();
        loadSearchHistory();
    }

    private void loadAllNotebooks() {
        TreeItem<NotebookTreeItem> root = notebookTreeView.getRoot();
        root.getChildren().clear();

        List<Notebook> rootNotebooks = notebookService.getRootNotebooks();
        for (Notebook notebook : rootNotebooks) {
            TreeItem<NotebookTreeItem> item = createNotebookTreeItem(notebook);
            root.getChildren().add(item);
        }

        logger.debug("已加载 {} 个笔记本", rootNotebooks.size());
    }

    private TreeItem<NotebookTreeItem> createNotebookTreeItem(Notebook notebook) {
        NotebookTreeItem treeItem = new NotebookTreeItem(notebook.getId(), notebook.getName());
        TreeItem<NotebookTreeItem> item = new TreeItem<>(treeItem);

        List<Notebook> children = notebookService.getChildNotebooks(notebook.getId());
        for (Notebook child : children) {
            item.getChildren().add(createNotebookTreeItem(child));
        }

        return item;
    }

    private void loadAllTags() {
        tagItems.clear();
        List<Tag> tags = tagService.getAllTags();
        for (Tag tag : tags) {
            int count = tagService.getTagUsageCount(tag.getId());
            tagItems.add(new TagItem(tag.getId(), tag.getName(), tag.getColor(), count));
        }
        logger.debug("已加载 {} 个标签", tags.size());
    }

    private void loadAllNotes() {
        noteListItems.clear();
        List<Note> notes = noteService.getAllNotes();
        for (Note note : notes) {
            noteListItems.add(createNoteListItem(note));
        }
        statusLabel.setText("共 " + notes.size() + " 篇笔记");
    }

    private void loadNotesByTag(String tagId) {
        noteListItems.clear();
        List<Note> notes = noteService.getNotesByTag(tagId);
        for (Note note : notes) {
            noteListItems.add(createNoteListItem(note));
        }
        statusLabel.setText("标签筛选: " + notes.size() + " 篇笔记");
    }

    private void loadNotesByNotebook(TreeItem<NotebookTreeItem> selectedItem) {
        if (selectedItem.getValue() == null || selectedItem.getValue().getId() == null) {
            loadAllNotes();
            return;
        }

        String notebookId = selectedItem.getValue().getId();
        noteListItems.clear();
        List<Note> notes = noteService.getNotesByNotebook(notebookId);
        for (Note note : notes) {
            noteListItems.add(createNoteListItem(note));
        }
        statusLabel.setText("笔记本: " + notes.size() + " 篇笔记");
    }

    private NoteListItem createNoteListItem(Note note) {
        String preview = note.getContent();
        if (preview.length() > 80) {
            preview = preview.substring(0, 80) + "...";
        }
        preview = preview.replace("\n", " ").replace("#", "");

        return new NoteListItem(
                note.getId(),
                note.getTitle(),
                preview,
                note.getUpdatedAt().format(DATE_FORMATTER),
                note.isFavorite(),
                note.isEncrypted(),
                note.getWordCount()
        );
    }

    private void loadNote(String noteId) {
        if (currentNote != null && isNoteModified) {
            saveCurrentNote();
        }

        Note note = noteService.getNoteById(noteId);
        if (note == null) {
            return;
        }

        currentNote = note;
        noteTitleField.setText(note.getTitle());
        markdownTextArea.setText(note.getContent());
        updatePreviewAsync(note.getContent());
        updateWordCount(note.getContent());
        isNoteModified = false;

        statusLabel.setText("正在编辑: " + note.getTitle());
        logger.debug("已加载笔记: {}", note.getTitle());
    }

    private void saveCurrentNote() {
        if (currentNote == null) {
            return;
        }

        currentNote.setTitle(noteTitleField.getText());
        currentNote.setContent(markdownTextArea.getText());
        noteService.updateNote(currentNote);
        isNoteModified = false;

        int selectedIndex = noteListView.getSelectionModel().getSelectedIndex();
        if (selectedIndex >= 0) {
            noteListItems.set(selectedIndex, createNoteListItem(currentNote));
        }

        statusLabel.setText("已保存: " + currentNote.getTitle());
        logger.debug("已保存笔记: {}", currentNote.getTitle());
    }

    private void editSelectedNote() {
        NoteListItem selected = noteListView.getSelectionModel().getSelectedItem();
        if (selected != null) {
            loadNote(selected.getNoteId());
        }
    }

    @FXML
    private void handleNewNote() {
        if (currentNote != null && isNoteModified) {
            saveCurrentNote();
        }

        Note newNote = noteService.createNote("未命名笔记", "");
        currentNote = newNote;
        noteTitleField.setText(newNote.getTitle());
        markdownTextArea.setText(newNote.getContent());
        updatePreviewAsync("");
        updateWordCount("");
        isNoteModified = true;

        noteListItems.add(0, createNoteListItem(newNote));
        noteListView.getSelectionModel().select(0);
        noteTitleField.requestFocus();
        noteTitleField.selectAll();

        statusLabel.setText("新建笔记");
    }

    @FXML
    private void handleSaveNote() {
        saveCurrentNote();
    }

    @FXML
    private void handleDeleteNote() {
        if (currentNote == null) {
            showAlert("请先选择一个笔记", Alert.AlertType.WARNING);
            return;
        }

        Alert alert = new Alert(Alert.AlertType.CONFIRMATION);
        alert.setTitle("确认删除");
        alert.setHeaderText("删除笔记");
        alert.setContentText("确定要删除笔记 \"" + currentNote.getTitle() + "\" 吗？");

        Optional<ButtonType> result = alert.showAndWait();
        if (result.isPresent() && result.get() == ButtonType.OK) {
            String noteId = currentNote.getId();
            noteService.deleteNote(noteId);

            noteListItems.removeIf(item -> item.getNoteId().equals(noteId));
            currentNote = null;
            noteTitleField.clear();
            markdownTextArea.clear();
            previewEngine.loadContent("<html><body style='font-family: sans-serif; padding: 20px;'><h3>选择或创建一个笔记开始编辑</h3></body></html>");
            wordCountLabel.setText("0 字");
            isNoteModified = false;

            statusLabel.setText("已删除笔记");
            logger.info("已删除笔记: {}", noteId);
        }
    }

    private void handleDeleteSelectedNotes() {
        ObservableList<NoteListItem> selected = noteListView.getSelectionModel().getSelectedItems();
        if (selected.isEmpty()) {
            return;
        }

        Alert alert = new Alert(Alert.AlertType.CONFIRMATION);
        alert.setTitle("确认删除");
        alert.setHeaderText("批量删除");
        alert.setContentText("确定要删除选中的 " + selected.size() + " 篇笔记吗？");

        Optional<ButtonType> result = alert.showAndWait();
        if (result.isPresent() && result.get() == ButtonType.OK) {
            for (NoteListItem item : selected) {
                noteService.deleteNote(item.getNoteId());
                noteListItems.remove(item);
            }

            currentNote = null;
            noteTitleField.clear();
            markdownTextArea.clear();
            isNoteModified = false;

            statusLabel.setText("已删除 " + selected.size() + " 篇笔记");
        }
    }

    private void handleMoveNotes() {
        ObservableList<NoteListItem> selected = noteListView.getSelectionModel().getSelectedItems();
        if (selected.isEmpty()) {
            return;
        }

        List<Notebook> notebooks = notebookService.getAllNotebooks();
        if (notebooks.isEmpty()) {
            showAlert("没有可用的笔记本，请先创建", Alert.AlertType.WARNING);
            return;
        }

        List<String> choices = new ArrayList<>();
        choices.add("根目录");
        for (Notebook nb : notebooks) {
            choices.add(nb.getName());
        }

        ChoiceDialog<String> dialog = new ChoiceDialog<>("根目录", choices);
        dialog.setTitle("移动笔记");
        dialog.setHeaderText("选择目标笔记本");
        dialog.setContentText("目标:");

        Optional<String> result = dialog.showAndWait();
        if (result.isPresent()) {
            String targetName = result.get();
            String targetId = null;

            if (!"根目录".equals(targetName)) {
                for (Notebook nb : notebooks) {
                    if (nb.getName().equals(targetName)) {
                        targetId = nb.getId();
                        break;
                    }
                }
            }

            for (NoteListItem item : selected) {
                Note note = noteService.getNoteById(item.getNoteId());
                if (note != null) {
                    note.setNotebookId(targetId);
                    noteService.updateNote(note);
                }
            }

            loadAllNotes();
            statusLabel.setText("已移动 " + selected.size() + " 篇笔记");
        }
    }

    private void handleAddTagToNotes() {
        ObservableList<NoteListItem> selected = noteListView.getSelectionModel().getSelectedItems();
        if (selected.isEmpty()) {
            return;
        }

        List<Tag> tags = tagService.getAllTags();
        List<String> tagNames = new ArrayList<>();
        for (Tag tag : tags) {
            tagNames.add(tag.getName());
        }
        tagNames.add("创建新标签...");

        ChoiceDialog<String> dialog = new ChoiceDialog<>(tagNames.get(0), tagNames);
        dialog.setTitle("添加标签");
        dialog.setHeaderText("选择或创建标签");
        dialog.setContentText("标签:");

        Optional<String> result = dialog.showAndWait();
        if (result.isPresent()) {
            String tagName = result.get();
            Tag tag;

            if ("创建新标签...".equals(tagName)) {
                TextInputDialog textDialog = new TextInputDialog();
                textDialog.setTitle("创建标签");
                textDialog.setHeaderText("输入新标签名称");
                textDialog.setContentText("名称:");
                Optional<String> newTagResult = textDialog.showAndWait();
                if (newTagResult.isPresent() && !newTagResult.get().trim().isEmpty()) {
                    tag = tagService.createTag(newTagResult.get().trim());
                } else {
                    return;
                }
            } else {
                tag = tagService.getTagByName(tagName);
            }

            if (tag != null) {
                for (NoteListItem item : selected) {
                    noteService.addTagToNote(item.getNoteId(), tag.getId());
                }
                loadAllTags();
                statusLabel.setText("已为 " + selected.size() + " 篇笔记添加标签");
            }
        }
    }

    private void handleToggleFavorite() {
        ObservableList<NoteListItem> selected = noteListView.getSelectionModel().getSelectedItems();
        for (NoteListItem item : selected) {
            noteService.toggleFavorite(item.getNoteId());
        }
        refreshNoteList();
        statusLabel.setText("已切换收藏状态");
    }

    private void refreshNoteList() {
        int selectedIndex = noteListView.getSelectionModel().getSelectedIndex();
        loadAllNotes();
        if (selectedIndex >= 0 && selectedIndex < noteListItems.size()) {
            noteListView.getSelectionModel().select(selectedIndex);
        }
    }

    private void handleExportSelectedNotes() {
        ObservableList<NoteListItem> selected = noteListView.getSelectionModel().getSelectedItems();
        if (selected.isEmpty()) {
            showAlert("请先选择笔记", Alert.AlertType.WARNING);
            return;
        }

        List<String> choices = Arrays.asList("PDF", "HTML", "Word", "Markdown", "纯文本");
        ChoiceDialog<String> dialog = new ChoiceDialog<>("PDF", choices);
        dialog.setTitle("批量导出");
        dialog.setHeaderText("选择导出格式");
        dialog.setContentText("格式:");

        Optional<String> result = dialog.showAndWait();
        if (result.isPresent()) {
            String formatStr = result.get();
            ExportService.ExportFormat format;

            switch (formatStr) {
                case "PDF":
                    format = ExportService.ExportFormat.PDF;
                    break;
                case "HTML":
                    format = ExportService.ExportFormat.HTML;
                    break;
                case "Word":
                    format = ExportService.ExportFormat.WORD;
                    break;
                case "Markdown":
                    format = ExportService.ExportFormat.MARKDOWN;
                    break;
                default:
                    format = ExportService.ExportFormat.PLAIN_TEXT;
            }

            String userHome = System.getProperty("user.home");
            String outputDir = userHome + "/Desktop/NoteExports";

            List<ExportService.ExportItem> items = new ArrayList<>();
            for (NoteListItem item : selected) {
                Note note = noteService.getNoteById(item.getNoteId());
                if (note != null) {
                    items.add(new ExportService.ExportItem(note.getTitle(), note.getContent()));
                }
            }

            boolean success = exportService.batchExport(items, format, outputDir);

            if (success) {
                showAlert("导出成功！文件已保存到: " + outputDir, Alert.AlertType.INFORMATION);
                statusLabel.setText("已导出 " + selected.size() + " 篇笔记");
            } else {
                showAlert("导出失败，请检查日志", Alert.AlertType.ERROR);
            }
        }
    }

    private void handleShowVersions() {
        NoteListItem selected = noteListView.getSelectionModel().getSelectedItem();
        if (selected == null) {
            return;
        }

        List<com.notetaking.model.NoteVersion> versions = versionService.getVersions(selected.getNoteId());
        if (versions.isEmpty()) {
            showAlert("该笔记没有历史版本", Alert.AlertType.INFORMATION);
            return;
        }

        List<String> versionItems = new ArrayList<>();
        for (int i = 0; i < versions.size(); i++) {
            com.notetaking.model.NoteVersion v = versions.get(i);
            versionItems.add((i + 1) + ". " + v.getCreatedAt().format(DATE_FORMATTER) +
                    " - " + v.getTitle());
        }

        ChoiceDialog<String> dialog = new ChoiceDialog<>(versionItems.get(0), versionItems);
        dialog.setTitle("版本历史");
        dialog.setHeaderText("选择要恢复的版本");
        dialog.setContentText("版本:");

        Optional<String> result = dialog.showAndWait();
        if (result.isPresent()) {
            int selectedIndex = versionItems.indexOf(result.get());
            if (selectedIndex >= 0 && selectedIndex < versions.size()) {
                com.notetaking.model.NoteVersion version = versions.get(selectedIndex);

                Alert confirmAlert = new Alert(Alert.AlertType.CONFIRMATION);
                confirmAlert.setTitle("确认恢复");
                confirmAlert.setHeaderText("恢复到历史版本");
                confirmAlert.setContentText("确定要恢复到版本: " + version.getCreatedAt().format(DATE_FORMATTER) + " 吗？\n当前内容将被覆盖。");

                Optional<ButtonType> confirmResult = confirmAlert.showAndWait();
                if (confirmResult.isPresent() && confirmResult.get() == ButtonType.OK) {
                    Note note = noteService.getNoteById(selected.getNoteId());
                    if (note != null) {
                        note.setTitle(version.getTitle());
                        note.setContent(version.getContent());
                        noteService.updateNote(note);

                        noteTitleField.setText(version.getTitle());
                        markdownTextArea.setText(version.getContent());
                        updatePreviewAsync(version.getContent());

                        refreshNoteList();
                        statusLabel.setText("已恢复到历史版本");
                    }
                }
            }
        }
    }

    @FXML
    private void handleExportPdf() {
        if (currentNote == null) {
            showAlert("请先选择一个笔记", Alert.AlertType.WARNING);
            return;
        }
        exportCurrentNote(ExportService.ExportFormat.PDF);
    }

    @FXML
    private void handleExportHtml() {
        if (currentNote == null) {
            showAlert("请先选择一个笔记", Alert.AlertType.WARNING);
            return;
        }
        exportCurrentNote(ExportService.ExportFormat.HTML);
    }

    @FXML
    private void handleExportWord() {
        if (currentNote == null) {
            showAlert("请先选择一个笔记", Alert.AlertType.WARNING);
            return;
        }
        exportCurrentNote(ExportService.ExportFormat.WORD);
    }

    @FXML
    private void handleExportMarkdown() {
        if (currentNote == null) {
            showAlert("请先选择一个笔记", Alert.AlertType.WARNING);
            return;
        }
        exportCurrentNote(ExportService.ExportFormat.MARKDOWN);
    }

    private void exportCurrentNote(ExportService.ExportFormat format) {
        String defaultFileName = currentNote.getTitle().replaceAll("[\\\\/:*?\"<>|]", "_") + "." + format.getExtension();
        String userHome = System.getProperty("user.home");
        String outputPath = userHome + "/Desktop/" + defaultFileName;

        boolean success = false;
        String title = currentNote.getTitle();
        String content = currentNote.getContent();

        switch (format) {
            case PDF:
                success = exportService.exportToPdf(title, content, outputPath);
                break;
            case HTML:
                success = exportService.exportToHtml(title, content, outputPath);
                break;
            case WORD:
                success = exportService.exportToWord(title, content, outputPath);
                break;
            case MARKDOWN:
                success = exportService.exportToMarkdown(title, content, outputPath);
                break;
            case PLAIN_TEXT:
                success = exportService.exportToPlainText(title, content, outputPath);
                break;
        }

        if (success) {
            showAlert("导出成功！文件已保存到: " + outputPath, Alert.AlertType.INFORMATION);
            statusLabel.setText("已导出: " + format.getExtension().toUpperCase());
        } else {
            showAlert("导出失败，请检查日志", Alert.AlertType.ERROR);
        }
    }

    private void performSearch(String keyword) {
        List<Note> results = searchService.search(keyword);
        noteListItems.clear();
        for (Note note : results) {
            noteListItems.add(createNoteListItem(note));
        }
        loadSearchHistory();
        statusLabel.setText("搜索结果: " + results.size() + " 篇笔记");
    }

    private void handleCreateNotebook(String parentId) {
        TextInputDialog dialog = new TextInputDialog();
        dialog.setTitle("创建笔记本");
        dialog.setHeaderText("输入笔记本名称");
        dialog.setContentText("名称:");

        Optional<String> result = dialog.showAndWait();
        if (result.isPresent() && !result.get().trim().isEmpty()) {
            Notebook notebook = notebookService.createNotebook(result.get().trim(), parentId);
            loadAllNotebooks();
            statusLabel.setText("已创建笔记本: " + notebook.getName());
        }
    }

    private void handleCreateSubNotebook() {
        TreeItem<NotebookTreeItem> selected = notebookTreeView.getSelectionModel().getSelectedItem();
        if (selected != null && selected.getValue() != null && selected.getValue().getId() != null) {
            handleCreateNotebook(selected.getValue().getId());
        }
    }

    private void handleRenameNotebook() {
        TreeItem<NotebookTreeItem> selected = notebookTreeView.getSelectionModel().getSelectedItem();
        if (selected == null || selected.getValue() == null || selected.getValue().getId() == null) {
            return;
        }

        TextInputDialog dialog = new TextInputDialog(selected.getValue().getName());
        dialog.setTitle("重命名笔记本");
        dialog.setHeaderText("输入新名称");
        dialog.setContentText("名称:");

        Optional<String> result = dialog.showAndWait();
        if (result.isPresent() && !result.get().trim().isEmpty()) {
            Notebook notebook = notebookService.getNotebookById(selected.getValue().getId());
            if (notebook != null) {
                notebook.setName(result.get().trim());
                notebookService.updateNotebook(notebook);
                loadAllNotebooks();
                statusLabel.setText("已重命名笔记本");
            }
        }
    }

    private void handleDeleteNotebook() {
        TreeItem<NotebookTreeItem> selected = notebookTreeView.getSelectionModel().getSelectedItem();
        if (selected == null || selected.getValue() == null || selected.getValue().getId() == null) {
            return;
        }

        Alert alert = new Alert(Alert.AlertType.CONFIRMATION);
        alert.setTitle("确认删除");
        alert.setHeaderText("删除笔记本");
        alert.setContentText("确定要删除笔记本 \"" + selected.getValue().getName() + "\" 吗？\n这将同时删除其中的所有笔记和子笔记本。");

        Optional<ButtonType> result = alert.showAndWait();
        if (result.isPresent() && result.get() == ButtonType.OK) {
            notebookService.deleteNotebook(selected.getValue().getId());
            loadAllNotebooks();
            loadAllNotes();
            statusLabel.setText("已删除笔记本");
        }
    }

    private void handleRenameTag() {
        TagItem selected = tagListView.getSelectionModel().getSelectedItem();
        if (selected == null) {
            return;
        }

        TextInputDialog dialog = new TextInputDialog(selected.getName());
        dialog.setTitle("重命名标签");
        dialog.setHeaderText("输入新名称");
        dialog.setContentText("名称:");

        Optional<String> result = dialog.showAndWait();
        if (result.isPresent() && !result.get().trim().isEmpty()) {
            Tag tag = tagService.getTagById(selected.getTagId());
            if (tag != null) {
                tag.setName(result.get().trim());
                tagService.updateTag(tag);
                loadAllTags();
                statusLabel.setText("已重命名标签");
            }
        }
    }

    private void handleDeleteTag() {
        TagItem selected = tagListView.getSelectionModel().getSelectedItem();
        if (selected == null) {
            return;
        }

        Alert alert = new Alert(Alert.AlertType.CONFIRMATION);
        alert.setTitle("确认删除");
        alert.setHeaderText("删除标签");
        alert.setContentText("确定要删除标签 \"" + selected.getName() + "\" 吗？");

        Optional<ButtonType> result = alert.showAndWait();
        if (result.isPresent() && result.get() == ButtonType.OK) {
            tagService.deleteTag(selected.getTagId());
            loadAllTags();
            statusLabel.setText("已删除标签");
        }
    }

    private void handleChangeTagColor() {
        TagItem selected = tagListView.getSelectionModel().getSelectedItem();
        if (selected == null) {
            return;
        }

        List<String> colors = Arrays.asList(
                "#6B7280", "#EF4444", "#F59E0B", "#10B981", "#3B82F6",
                "#8B5CF6", "#EC4899", "#F97316", "#14B8A6", "#6366F1"
        );

        ChoiceDialog<String> dialog = new ChoiceDialog<>(selected.getColor(), colors);
        dialog.setTitle("选择颜色");
        dialog.setHeaderText("选择标签颜色");
        dialog.setContentText("颜色:");

        Optional<String> result = dialog.showAndWait();
        if (result.isPresent()) {
            Tag tag = tagService.getTagById(selected.getTagId());
            if (tag != null) {
                tag.setColor(result.get());
                tagService.updateTag(tag);
                loadAllTags();
                statusLabel.setText("已更改标签颜色");
            }
        }
    }

    @FXML
    private void handleShowStatistics() {
        String report = statisticsService.generateStatisticsReport();
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle("统计信息");
        alert.setHeaderText("笔记统计报告");
        alert.setContentText(report);
        alert.getDialogPane().setPrefWidth(450);
        alert.showAndWait();
    }

    @FXML
    private void handleAbout() {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle("关于");
        alert.setHeaderText("笔记管理应用");
        alert.setContentText("版本: 1.0.0\n\n一个功能完整的本地笔记管理应用\n支持Markdown、搜索、导出、加密等功能");
        alert.showAndWait();
    }

    @FXML
    private void handleExit() {
        if (currentNote != null && isNoteModified) {
            saveCurrentNote();
        }
        executorService.shutdown();
        Platform.exit();
    }

    private void showAlert(String message, Alert.AlertType type) {
        Alert alert = new Alert(type);
        alert.setContentText(message);
        alert.showAndWait();
    }

    public void setMainApp(MainApp mainApp) {
        this.mainApp = mainApp;
    }

    public static class NoteListItem {
        private final String noteId;
        private final String title;
        private final String preview;
        private final String updatedAt;
        private final boolean favorite;
        private final boolean encrypted;
        private final int wordCount;

        public NoteListItem(String noteId, String title, String preview, String updatedAt,
                            boolean favorite, boolean encrypted, int wordCount) {
            this.noteId = noteId;
            this.title = title;
            this.preview = preview;
            this.updatedAt = updatedAt;
            this.favorite = favorite;
            this.encrypted = encrypted;
            this.wordCount = wordCount;
        }

        public String getNoteId() { return noteId; }
        public String getTitle() { return title; }
        public String getPreview() { return preview; }
        public String getUpdatedAt() { return updatedAt; }
        public boolean isFavorite() { return favorite; }
        public boolean isEncrypted() { return encrypted; }
        public int getWordCount() { return wordCount; }
    }

    public static class TagItem {
        private final String tagId;
        private final String name;
        private final String color;
        private final int count;

        public TagItem(String tagId, String name, String color, int count) {
            this.tagId = tagId;
            this.name = name;
            this.color = color;
            this.count = count;
        }

        public String getTagId() { return tagId; }
        public String getName() { return name; }
        public String getColor() { return color; }
        public int getCount() { return count; }
    }

    public static class NotebookTreeItem {
        private final String id;
        private final String name;

        public NotebookTreeItem(String id, String name) {
            this.id = id;
            this.name = name;
        }

        public String getId() { return id; }
        public String getName() { return name; }

        @Override
        public String toString() {
            return name;
        }
    }
}
