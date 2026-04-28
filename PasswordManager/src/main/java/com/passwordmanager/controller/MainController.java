package com.passwordmanager.controller;

import com.passwordmanager.AppContext;
import com.passwordmanager.model.PasswordCategory;
import com.passwordmanager.model.PasswordEntry;
import com.passwordmanager.service.DataStorageService;
import com.passwordmanager.util.ClipboardUtil;
import javafx.application.Platform;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.fxml.Initializable;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.input.*;
import javafx.scene.paint.Color;
import javafx.stage.FileChooser;
import javafx.stage.Modality;
import javafx.stage.Stage;

import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Optional;
import java.util.ResourceBundle;
import java.util.Timer;
import java.util.TimerTask;

public class MainController implements Initializable {

    @FXML
    private TableView<PasswordEntry> passwordTableView;

    @FXML
    private TableColumn<PasswordEntry, String> titleColumn;

    @FXML
    private TableColumn<PasswordEntry, String> usernameColumn;

    @FXML
    private TableColumn<PasswordEntry, String> passwordColumn;

    @FXML
    private TableColumn<PasswordEntry, PasswordCategory> categoryColumn;

    @FXML
    private TableColumn<PasswordEntry, String> urlColumn;

    @FXML
    private TableColumn<PasswordEntry, Boolean> favoriteColumn;

    @FXML
    private TextField searchTextField;

    @FXML
    private ComboBox<String> categoryComboBox;

    @FXML
    private Label statusLabel;

    @FXML
    private MenuItem menuAdd;

    @FXML
    private MenuItem menuEdit;

    @FXML
    private MenuItem menuDelete;

    @FXML
    private MenuItem menuCopyUsername;

    @FXML
    private MenuItem menuCopyPassword;

    @FXML
    private MenuItem menuHistory;

    @FXML
    private Button addButton;

    @FXML
    private Button editButton;

    @FXML
    private Button deleteButton;

    @FXML
    private Button copyUsernameButton;

    @FXML
    private Button copyPasswordButton;

    private DataStorageService dataStorageService;
    private ObservableList<PasswordEntry> passwordList;
    private PasswordEntry selectedEntry;
    private Timer expiryCheckTimer;

    @Override
    public void initialize(URL location, ResourceBundle resources) {
        dataStorageService = AppContext.getInstance().getDataStorageService();
        passwordList = FXCollections.observableArrayList();

        initializeTableView();
        initializeCategoryComboBox();
        initializeAccelerators();
        initializeAutoLock();
        loadPasswords();
        startExpiryCheckTimer();

        passwordTableView.getSelectionModel().selectedItemProperty().addListener((obs, oldSelection, newSelection) -> {
            selectedEntry = newSelection;
            updateButtonStates();
            AppContext.getInstance().updateUserActivity();
        });

        passwordTableView.setOnMouseClicked(event -> {
            AppContext.getInstance().updateUserActivity();
            if (event.getClickCount() == 2 && selectedEntry != null) {
                handleEdit();
            }
        });

        searchTextField.setOnKeyReleased(event -> {
            AppContext.getInstance().updateUserActivity();
            handleSearch();
        });
    }

    private void initializeAutoLock() {
        if (dataStorageService.getAppData() != null && dataStorageService.getAppData().getSettings() != null) {
            int autoLockTime = dataStorageService.getAppData().getSettings().getAutoLockTimeMinutes();
            AppContext.getInstance().setAutoLockTimeMinutes(autoLockTime);
        }

        AppContext.getInstance().setOnLockCallback(v -> {
            Platform.runLater(() -> {
                stopExpiryCheckTimer();
                handleLock();
            });
        });

        AppContext.getInstance().startAutoLockTimer();
    }

    private void initializeAccelerators() {
        Scene scene = passwordTableView.getScene();
        if (scene != null) {
            setupSceneAccelerators(scene);
        } else {
            passwordTableView.sceneProperty().addListener((obs, oldScene, newScene) -> {
                if (newScene != null) {
                    setupSceneAccelerators(newScene);
                }
            });
        }

        passwordTableView.addEventFilter(KeyEvent.KEY_PRESSED, event -> {
            AppContext.getInstance().updateUserActivity();

            if (new KeyCodeCombination(KeyCode.DELETE).match(event)) {
                handleDelete();
                event.consume();
            } else if (new KeyCodeCombination(KeyCode.C, KeyCombination.SHORTCUT_DOWN).match(event)) {
                if (selectedEntry != null) {
                    handleCopyPassword();
                    event.consume();
                }
            } else if (new KeyCodeCombination(KeyCode.U, KeyCombination.SHORTCUT_DOWN).match(event)) {
                if (selectedEntry != null) {
                    handleCopyUsername();
                    event.consume();
                }
            } else if (new KeyCodeCombination(KeyCode.N, KeyCombination.SHORTCUT_DOWN).match(event)) {
                handleAdd();
                event.consume();
            } else if (new KeyCodeCombination(KeyCode.E, KeyCombination.SHORTCUT_DOWN).match(event)) {
                if (selectedEntry != null) {
                    handleEdit();
                    event.consume();
                }
            } else if (new KeyCodeCombination(KeyCode.F, KeyCombination.SHORTCUT_DOWN).match(event)) {
                searchTextField.requestFocus();
                event.consume();
            } else if (new KeyCodeCombination(KeyCode.L, KeyCombination.SHORTCUT_DOWN).match(event)) {
                handleLock();
                event.consume();
            }
        });
    }

    private void setupSceneAccelerators(Scene scene) {
        scene.addEventFilter(MouseEvent.MOUSE_PRESSED, event -> {
            AppContext.getInstance().updateUserActivity();
        });

        scene.addEventFilter(KeyEvent.KEY_PRESSED, event -> {
            AppContext.getInstance().updateUserActivity();
        });
    }

    private void updateButtonStates() {
        boolean hasSelection = selectedEntry != null;
        if (editButton != null) editButton.setDisable(!hasSelection);
        if (deleteButton != null) deleteButton.setDisable(!hasSelection);
        if (copyUsernameButton != null) copyUsernameButton.setDisable(!hasSelection);
        if (copyPasswordButton != null) copyPasswordButton.setDisable(!hasSelection);
    }

    private void initializeTableView() {
        titleColumn.setCellValueFactory(new PropertyValueFactory<>("title"));
        usernameColumn.setCellValueFactory(new PropertyValueFactory<>("username"));
        passwordColumn.setCellValueFactory(new PropertyValueFactory<>("password"));
        passwordColumn.setCellFactory(column -> new TableCell<PasswordEntry, String>() {
            @Override
            protected void updateItem(String item, boolean empty) {
                super.updateItem(item, empty);
                if (empty || item == null) {
                    setText(null);
                } else {
                    setText("********");
                }
            }
        });

        categoryColumn.setCellValueFactory(new PropertyValueFactory<>("category"));
        categoryColumn.setCellFactory(column -> new TableCell<PasswordEntry, PasswordCategory>() {
            @Override
            protected void updateItem(PasswordCategory item, boolean empty) {
                super.updateItem(item, empty);
                if (empty || item == null) {
                    setText(null);
                } else {
                    setText(item.getDisplayName());
                }
            }
        });

        urlColumn.setCellValueFactory(new PropertyValueFactory<>("url"));

        favoriteColumn.setCellValueFactory(new PropertyValueFactory<>("favorite"));
        favoriteColumn.setCellFactory(column -> new TableCell<PasswordEntry, Boolean>() {
            @Override
            protected void updateItem(Boolean item, boolean empty) {
                super.updateItem(item, empty);
                if (empty || item == null) {
                    setText(null);
                } else {
                    setText(item ? "★" : "");
                }
            }
        });

        passwordTableView.setRowFactory(tv -> new TableRow<PasswordEntry>() {
            @Override
            protected void updateItem(PasswordEntry item, boolean empty) {
                super.updateItem(item, empty);
                if (item != null) {
                    if (item.isPasswordExpired()) {
                        setStyle("-fx-background-color: #ffcccc;");
                    } else if (item.isPasswordExpiringSoon()) {
                        setStyle("-fx-background-color: #fff9c4;");
                    } else {
                        setStyle("");
                    }
                } else {
                    setStyle("");
                }
            }
        });

        passwordTableView.setItems(passwordList);
    }

    private void startExpiryCheckTimer() {
        expiryCheckTimer = new Timer("ExpiryCheckTimer", true);
        expiryCheckTimer.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                Platform.runLater(() -> checkExpiredPasswords());
            }
        }, 5000, 60000);
    }

    private void stopExpiryCheckTimer() {
        if (expiryCheckTimer != null) {
            expiryCheckTimer.cancel();
            expiryCheckTimer = null;
        }
    }

    private void checkExpiredPasswords() {
        if (dataStorageService.getAppData() == null) return;

        long expiredCount = dataStorageService.getAppData().getPasswordEntries().stream()
                .filter(PasswordEntry::isPasswordExpired)
                .count();

        long expiringSoonCount = dataStorageService.getAppData().getPasswordEntries().stream()
                .filter(PasswordEntry::isPasswordExpiringSoon)
                .count();

        if (expiredCount > 0 || expiringSoonCount > 0) {
            StringBuilder message = new StringBuilder();
            if (expiredCount > 0) {
                message.append("⚠️ 有 ").append(expiredCount).append(" 个密码已过期！\n");
            }
            if (expiringSoonCount > 0) {
                message.append("⚠️ 有 ").append(expiringSoonCount).append(" 个密码即将过期（7天内）\n");
            }
            message.append("\n建议尽快更新这些密码。");

            if (expiredCount > 0) {
                showAlert(Alert.AlertType.WARNING, "密码过期提醒", message.toString());
            }
        }

        passwordTableView.refresh();
    }

    private void initializeCategoryComboBox() {
        categoryComboBox.getItems().add("全部");
        categoryComboBox.getItems().add("收藏夹");
        categoryComboBox.getItems().add("已过期");
        categoryComboBox.getItems().add("即将过期");
        for (PasswordCategory category : PasswordCategory.values()) {
            categoryComboBox.getItems().add(category.getDisplayName());
        }
        categoryComboBox.getSelectionModel().selectFirst();
    }

    private void loadPasswords() {
        if (dataStorageService.getAppData() != null && dataStorageService.getAppData().getPasswordEntries() != null) {
            passwordList.setAll(dataStorageService.getAppData().getPasswordEntries());
            updateStatus();
        }
    }

    private void updateStatus() {
        long expiredCount = passwordList.stream().filter(PasswordEntry::isPasswordExpired).count();
        long expiringCount = passwordList.stream().filter(PasswordEntry::isPasswordExpiringSoon).count();

        StringBuilder status = new StringBuilder();
        status.append("共有 ").append(passwordList.size()).append(" 条密码记录");

        if (expiredCount > 0) {
            status.append(" | ").append(expiredCount).append(" 条已过期");
        }
        if (expiringCount > 0) {
            status.append(" | ").append(expiringCount).append(" 条即将过期");
        }

        statusLabel.setText(status.toString());
    }

    @FXML
    private void handleSearch() {
        String keyword = searchTextField.getText().trim();
        String selectedCategory = categoryComboBox.getSelectionModel().getSelectedItem();

        List<PasswordEntry> entries;

        if ("收藏夹".equals(selectedCategory)) {
            entries = dataStorageService.getFavoritePasswords();
        } else if ("已过期".equals(selectedCategory)) {
            entries = dataStorageService.getAppData().getPasswordEntries();
            entries.removeIf(e -> !e.isPasswordExpired());
        } else if ("即将过期".equals(selectedCategory)) {
            entries = dataStorageService.getAppData().getPasswordEntries();
            entries.removeIf(e -> !e.isPasswordExpiringSoon());
        } else if (!"全部".equals(selectedCategory)) {
            PasswordCategory category = PasswordCategory.fromDisplayName(selectedCategory);
            entries = dataStorageService.getPasswordsByCategory(category);
        } else if (!keyword.isEmpty()) {
            entries = dataStorageService.searchPasswords(keyword);
        } else {
            entries = dataStorageService.getAppData().getPasswordEntries();
        }

        if (!keyword.isEmpty() && !"全部".equals(selectedCategory)) {
            entries.removeIf(entry -> {
                boolean matchesKeyword = entry.getTitle() != null && entry.getTitle().toLowerCase().contains(keyword.toLowerCase())
                        || entry.getUsername() != null && entry.getUsername().toLowerCase().contains(keyword.toLowerCase())
                        || entry.getUrl() != null && entry.getUrl().toLowerCase().contains(keyword.toLowerCase())
                        || entry.getNotes() != null && entry.getNotes().toLowerCase().contains(keyword.toLowerCase());
                return !matchesKeyword;
            });
        }

        passwordList.setAll(entries);
        updateStatus();
    }

    @FXML
    private void handleCategoryChange() {
        handleSearch();
    }

    @FXML
    private void handleAdd() {
        openPasswordDialog(null);
    }

    @FXML
    private void handleEdit() {
        if (selectedEntry == null) {
            showAlert(Alert.AlertType.WARNING, "提示", "请先选择一条密码记录");
            return;
        }
        openPasswordDialog(selectedEntry);
    }

    @FXML
    private void handleDelete() {
        if (selectedEntry == null) {
            showAlert(Alert.AlertType.WARNING, "提示", "请先选择一条密码记录");
            return;
        }

        Alert confirm = new Alert(Alert.AlertType.CONFIRMATION);
        confirm.setTitle("确认删除");
        confirm.setHeaderText(null);
        confirm.setContentText("确定要删除密码记录 \"" + selectedEntry.getTitle() + "\" 吗？");

        Optional<ButtonType> result = confirm.showAndWait();
        if (result.isPresent() && result.get() == ButtonType.OK) {
            try {
                dataStorageService.deletePasswordEntry(selectedEntry.getId());
                loadPasswords();
                showAlert(Alert.AlertType.INFORMATION, "成功", "密码记录已删除");
            } catch (Exception e) {
                e.printStackTrace();
                showAlert(Alert.AlertType.ERROR, "错误", "删除失败: " + e.getMessage());
            }
        }
    }

    @FXML
    private void handleHistory() {
        if (selectedEntry == null) {
            showAlert(Alert.AlertType.WARNING, "提示", "请先选择一条密码记录");
            return;
        }
        openPasswordHistoryDialog(selectedEntry);
    }

    @FXML
    private void handleCopyUsername() {
        if (selectedEntry == null) {
            showAlert(Alert.AlertType.WARNING, "提示", "请先选择一条密码记录");
            return;
        }
        if (selectedEntry.getUsername() != null && !selectedEntry.getUsername().isEmpty()) {
            ClipboardUtil.copyToClipboard(selectedEntry.getUsername());
            showAlert(Alert.AlertType.INFORMATION, "成功", "用户名已复制到剪贴板");
        }
    }

    @FXML
    private void handleCopyPassword() {
        if (selectedEntry == null) {
            showAlert(Alert.AlertType.WARNING, "提示", "请先选择一条密码记录");
            return;
        }
        if (selectedEntry.getPassword() != null && !selectedEntry.getPassword().isEmpty()) {
            ClipboardUtil.copyToClipboard(selectedEntry.getPassword());
            showAlert(Alert.AlertType.INFORMATION, "成功", "密码已复制到剪贴板");
        }
    }

    @FXML
    private void handlePasswordGenerator() {
        try {
            Stage stage = new Stage();
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/fxml/password-generator.fxml"));
            Parent root = loader.load();

            Scene scene = new Scene(root);
            stage.setScene(scene);
            stage.setTitle("密码生成器");
            stage.initModality(Modality.APPLICATION_MODAL);
            stage.setResizable(false);
            stage.showAndWait();
        } catch (IOException e) {
            e.printStackTrace();
            showAlert(Alert.AlertType.ERROR, "错误", "打开密码生成器失败");
        }
    }

    @FXML
    private void handlePasswordCheck() {
        TextInputDialog dialog = new TextInputDialog();
        dialog.setTitle("密码强度检测");
        dialog.setHeaderText("输入密码进行强度检测");
        dialog.setContentText("密码:");

        Optional<String> result = dialog.showAndWait();
        result.ifPresent(password -> {
            String strength = com.passwordmanager.util.PasswordStrengthChecker.getStrengthDisplay(password);
            int score = com.passwordmanager.util.PasswordStrengthChecker.getScore(password);
            int entropy = com.passwordmanager.util.PasswordStrengthChecker.getEntropy(password);

            StringBuilder message = new StringBuilder();
            message.append("密码强度: ").append(strength).append("\n");
            message.append("强度等级: ").append(score).append("/5\n");
            message.append("密码熵: ").append(entropy).append(" 位\n\n");

            if (com.passwordmanager.util.PasswordStrengthChecker.isWeak(password)) {
                message.append("⚠️ 检测到弱密码，建议使用更复杂的密码\n");
            }
            if (com.passwordmanager.util.PasswordStrengthChecker.containsRepeatedChars(password)) {
                message.append("⚠️ 包含重复字符序列\n");
            }
            if (com.passwordmanager.util.PasswordStrengthChecker.containsSequentialChars(password)) {
                message.append("⚠️ 包含连续字符序列\n");
            }
            if (com.passwordmanager.util.PasswordStrengthChecker.isCommonPassword(password)) {
                message.append("⚠️ 检测到常见密码，非常不安全\n");
            }

            showAlert(Alert.AlertType.INFORMATION, "检测结果", message.toString());
        });
    }

    @FXML
    private void handleImport() {
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("导入密码数据");
        fileChooser.getExtensionFilters().add(
                new FileChooser.ExtensionFilter("JSON文件", "*.json")
        );

        File file = fileChooser.showOpenDialog(AppContext.getInstance().getPrimaryStage());
        if (file != null) {
            try {
                int count = dataStorageService.importFromFile(file.getAbsolutePath());
                loadPasswords();
                showAlert(Alert.AlertType.INFORMATION, "成功", "成功导入 " + count + " 条密码记录");
            } catch (Exception e) {
                e.printStackTrace();
                showAlert(Alert.AlertType.ERROR, "错误", "导入失败: " + e.getMessage());
            }
        }
    }

    @FXML
    private void handleExport() {
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("导出密码数据");
        fileChooser.getExtensionFilters().add(
                new FileChooser.ExtensionFilter("JSON文件", "*.json")
        );
        fileChooser.setInitialFileName("passwords_" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss")) + ".json");

        File file = fileChooser.showSaveDialog(AppContext.getInstance().getPrimaryStage());
        if (file != null) {
            try {
                dataStorageService.exportToFile(file.getAbsolutePath());
                showAlert(Alert.AlertType.INFORMATION, "成功", "密码数据已导出到: " + file.getAbsolutePath());
            } catch (Exception e) {
                e.printStackTrace();
                showAlert(Alert.AlertType.ERROR, "错误", "导出失败: " + e.getMessage());
            }
        }
    }

    @FXML
    private void handleBackup() {
        try {
            String backupPath = dataStorageService.createBackup();
            showAlert(Alert.AlertType.INFORMATION, "成功", "备份已创建: " + backupPath);
        } catch (Exception e) {
            e.printStackTrace();
            showAlert(Alert.AlertType.ERROR, "错误", "创建备份失败: " + e.getMessage());
        }
    }

    @FXML
    private void handleRestore() {
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("选择备份文件恢复");
        fileChooser.getExtensionFilters().add(
                new FileChooser.ExtensionFilter("加密备份文件", "*.enc")
        );
        fileChooser.setInitialDirectory(new File(System.getProperty("user.home") + "/.passwordmanager/backups"));

        File file = fileChooser.showOpenDialog(AppContext.getInstance().getPrimaryStage());
        if (file != null) {
            Alert confirm = new Alert(Alert.AlertType.CONFIRMATION);
            confirm.setTitle("确认恢复");
            confirm.setHeaderText(null);
            confirm.setContentText("恢复备份将覆盖当前所有数据。确定要继续吗？");

            Optional<ButtonType> result = confirm.showAndWait();
            if (result.isPresent() && result.get() == ButtonType.OK) {
                try {
                    dataStorageService.restoreFromBackup(file.getAbsolutePath());
                    showAlert(Alert.AlertType.INFORMATION, "成功", "备份已恢复，请重新登录");
                    handleLock();
                } catch (Exception e) {
                    e.printStackTrace();
                    showAlert(Alert.AlertType.ERROR, "错误", "恢复失败: " + e.getMessage());
                }
            }
        }
    }

    @FXML
    private void handleSettings() {
        showAutoLockSettingsDialog();
    }

    private void showAutoLockSettingsDialog() {
        Dialog<ButtonType> dialog = new Dialog<>();
        dialog.setTitle("设置");
        dialog.setHeaderText("自动锁定设置");

        ComboBox<Integer> autoLockComboBox = new ComboBox<>();
        autoLockComboBox.getItems().addAll(0, 1, 5, 10, 30, 60);
        autoLockComboBox.setCellFactory(param -> new ListCell<Integer>() {
            @Override
            protected void updateItem(Integer item, boolean empty) {
                super.updateItem(item, empty);
                if (empty) {
                    setText(null);
                } else if (item == 0) {
                    setText("从不自动锁定");
                } else {
                    setText(item + " 分钟后自动锁定");
                }
            }
        });
        autoLockComboBox.setButtonCell(autoLockComboBox.getCellFactory().call(null));

        int currentTime = AppContext.getInstance().getAutoLockTimeMinutes();
        autoLockComboBox.setValue(currentTime > 0 ? currentTime : 0);

        javafx.scene.layout.VBox content = new javafx.scene.layout.VBox(10);
        content.setStyle("-fx-padding: 20;");
        content.getChildren().addAll(
                new Label("自动锁定时间:"),
                autoLockComboBox
        );

        dialog.getDialogPane().setContent(content);
        dialog.getDialogPane().getButtonTypes().addAll(ButtonType.OK, ButtonType.CANCEL);

        Optional<ButtonType> result = dialog.showAndWait();
        if (result.isPresent() && result.get() == ButtonType.OK) {
            int selectedTime = autoLockComboBox.getValue();
            AppContext.getInstance().setAutoLockTimeMinutes(selectedTime);
            if (selectedTime == 0) {
                AppContext.getInstance().stopAutoLockTimer();
                showAlert(Alert.AlertType.INFORMATION, "成功", "已禁用自动锁定");
            } else {
                showAlert(Alert.AlertType.INFORMATION, "成功", "自动锁定时间已设置为 " + selectedTime + " 分钟");
            }
        }
    }

    @FXML
    private void handleChangeMasterPassword() {
        Dialog<ButtonType> dialog = new Dialog<>();
        dialog.setTitle("修改主密码");
        dialog.setHeaderText("请输入原密码和新密码");

        PasswordField oldPasswordField = new PasswordField();
        oldPasswordField.setPromptText("原密码");

        PasswordField newPasswordField = new PasswordField();
        newPasswordField.setPromptText("新密码");

        PasswordField confirmPasswordField = new PasswordField();
        confirmPasswordField.setPromptText("确认新密码");

        javafx.scene.layout.VBox content = new javafx.scene.layout.VBox(10);
        content.getChildren().addAll(
                new Label("原密码:"), oldPasswordField,
                new Label("新密码:"), newPasswordField,
                new Label("确认新密码:"), confirmPasswordField
        );
        content.setStyle("-fx-padding: 20;");

        dialog.getDialogPane().setContent(content);
        dialog.getDialogPane().getButtonTypes().addAll(ButtonType.OK, ButtonType.CANCEL);

        Optional<ButtonType> result = dialog.showAndWait();
        if (result.isPresent() && result.get() == ButtonType.OK) {
            String oldPassword = oldPasswordField.getText();
            String newPassword = newPasswordField.getText();
            String confirmPassword = confirmPasswordField.getText();

            if (oldPassword.isEmpty() || newPassword.isEmpty() || confirmPassword.isEmpty()) {
                showAlert(Alert.AlertType.ERROR, "错误", "所有字段都不能为空");
                return;
            }

            if (!newPassword.equals(confirmPassword)) {
                showAlert(Alert.AlertType.ERROR, "错误", "两次输入的新密码不一致");
                return;
            }

            if (newPassword.length() < 6) {
                showAlert(Alert.AlertType.ERROR, "错误", "新密码至少需要6个字符");
                return;
            }

            try {
                dataStorageService.changeMasterPassword(oldPassword.toCharArray(), newPassword.toCharArray());
                showAlert(Alert.AlertType.INFORMATION, "成功", "主密码已修改，请重新登录");
                handleLock();
            } catch (Exception e) {
                e.printStackTrace();
                showAlert(Alert.AlertType.ERROR, "错误", e.getMessage());
            }
        }
    }

    @FXML
    private void handleLock() {
        AppContext.getInstance().stopAutoLockTimer();
        stopExpiryCheckTimer();
        dataStorageService.lock();

        try {
            Stage currentStage = AppContext.getInstance().getPrimaryStage();
            Stage loginStage = new Stage();

            FXMLLoader loader = new FXMLLoader(getClass().getResource("/fxml/login.fxml"));
            Parent root = loader.load();

            Scene scene = new Scene(root);
            loginStage.setScene(scene);
            loginStage.setTitle("密码管理器 - 登录");
            loginStage.setResizable(false);

            currentStage.close();
            loginStage.show();
        } catch (IOException e) {
            e.printStackTrace();
            showAlert(Alert.AlertType.ERROR, "错误", "锁定失败: " + e.getMessage());
        }
    }

    @FXML
    private void handleExit() {
        AppContext.getInstance().stopAutoLockTimer();
        stopExpiryCheckTimer();
        dataStorageService.lock();
        System.exit(0);
    }

    private void openPasswordDialog(PasswordEntry entry) {
        try {
            Stage stage = new Stage();
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/fxml/password-dialog.fxml"));
            Parent root = loader.load();

            PasswordDialogController controller = loader.getController();
            controller.setPasswordEntry(entry);

            Scene scene = new Scene(root);
            stage.setScene(scene);
            stage.setTitle(entry == null ? "添加密码" : "编辑密码");
            stage.initModality(Modality.APPLICATION_MODAL);
            stage.setResizable(false);
            stage.showAndWait();

            loadPasswords();
        } catch (IOException e) {
            e.printStackTrace();
            showAlert(Alert.AlertType.ERROR, "错误", "打开对话框失败");
        }
    }

    private void openPasswordHistoryDialog(PasswordEntry entry) {
        try {
            Stage stage = new Stage();
            FXMLLoader loader = new FXMLLoader(getClass().getResource("/fxml/password-history.fxml"));
            Parent root = loader.load();

            PasswordHistoryController controller = loader.getController();
            controller.setPasswordEntry(entry, dataStorageService);

            Scene scene = new Scene(root);
            stage.setScene(scene);
            stage.setTitle("密码历史 - " + entry.getTitle());
            stage.initModality(Modality.APPLICATION_MODAL);
            stage.setResizable(false);
            stage.showAndWait();
        } catch (IOException e) {
            e.printStackTrace();
            showAlert(Alert.AlertType.ERROR, "错误", "打开密码历史对话框失败");
        }
    }

    private void showAlert(Alert.AlertType type, String title, String content) {
        Alert alert = new Alert(type);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(content);
        alert.showAndWait();
    }
}
