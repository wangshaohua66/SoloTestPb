package com.passwordmanager.controller;

import com.passwordmanager.AppContext;
import com.passwordmanager.model.PasswordCategory;
import com.passwordmanager.model.PasswordEntry;
import com.passwordmanager.service.DataStorageService;
import com.passwordmanager.util.ClipboardUtil;
import com.passwordmanager.util.PasswordGenerator;
import com.passwordmanager.util.PasswordStrengthChecker;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.*;
import javafx.scene.input.MouseButton;
import javafx.scene.paint.Color;
import javafx.stage.Stage;

import java.net.URL;
import java.util.List;
import java.util.ResourceBundle;

public class PasswordGeneratorController implements Initializable {

    @FXML
    private TextField passwordTextField;

    @FXML
    private Label strengthValueLabel;

    @FXML
    private Slider lengthSlider;

    @FXML
    private Label lengthLabel;

    @FXML
    private CheckBox uppercaseCheckBox;

    @FXML
    private CheckBox lowercaseCheckBox;

    @FXML
    private CheckBox numbersCheckBox;

    @FXML
    private CheckBox symbolsCheckBox;

    @FXML
    private CheckBox excludeAmbiguousCheckBox;

    @FXML
    private TextField batchCountTextField;

    @FXML
    private ListView<String> batchListView;

    private PasswordGenerator generator;
    private ObservableList<String> generatedPasswords;
    private DataStorageService dataStorageService;

    @Override
    public void initialize(URL location, ResourceBundle resources) {
        dataStorageService = AppContext.getInstance().getDataStorageService();
        generator = new PasswordGenerator();
        generatedPasswords = FXCollections.observableArrayList();
        batchListView.setItems(generatedPasswords);

        lengthSlider.valueProperty().addListener((obs, oldVal, newVal) -> {
            int length = newVal.intValue();
            lengthLabel.setText(String.valueOf(length));
            generator.setLength(length);
            generatePassword();
        });

        uppercaseCheckBox.selectedProperty().addListener((obs, oldVal, newVal) -> {
            generator.setIncludeUppercase(newVal);
            generatePassword();
        });

        lowercaseCheckBox.selectedProperty().addListener((obs, oldVal, newVal) -> {
            generator.setIncludeLowercase(newVal);
            generatePassword();
        });

        numbersCheckBox.selectedProperty().addListener((obs, oldVal, newVal) -> {
            generator.setIncludeNumbers(newVal);
            generatePassword();
        });

        symbolsCheckBox.selectedProperty().addListener((obs, oldVal, newVal) -> {
            generator.setIncludeSymbols(newVal);
            generatePassword();
        });

        excludeAmbiguousCheckBox.selectedProperty().addListener((obs, oldVal, newVal) -> {
            generator.setExcludeAmbiguous(newVal);
            generatePassword();
        });

        setupBatchListViewContextMenu();
        setupBatchListViewDoubleClick();
        generatePassword();
    }

    private void setupBatchListViewContextMenu() {
        ContextMenu contextMenu = new ContextMenu();

        MenuItem saveSelectedItem = new MenuItem("保存选中密码到库");
        saveSelectedItem.setOnAction(e -> handleSaveSelectedToVault());

        MenuItem saveAllItem = new MenuItem("保存所有密码到库");
        saveAllItem.setOnAction(e -> handleSaveAllToVault());

        MenuItem copySelectedItem = new MenuItem("复制选中密码");
        copySelectedItem.setOnAction(e -> handleCopyBatchSelected());

        MenuItem copyAllItem = new MenuItem("复制所有密码（每行一个）");
        copyAllItem.setOnAction(e -> handleCopyAllBatch());

        MenuItem clearItem = new MenuItem("清空列表");
        clearItem.setOnAction(e -> {
            generatedPasswords.clear();
        });

        contextMenu.getItems().addAll(saveSelectedItem, saveAllItem, new SeparatorMenuItem(),
                copySelectedItem, copyAllItem, new SeparatorMenuItem(), clearItem);
        batchListView.setContextMenu(contextMenu);
    }

    private void setupBatchListViewDoubleClick() {
        batchListView.setOnMouseClicked(event -> {
            if (event.getButton() == MouseButton.PRIMARY && event.getClickCount() == 2) {
                handleCopyBatchSelected();
            }
        });
    }

    @FXML
    private void handleGenerate() {
        generatePassword();
    }

    @FXML
    private void handleCopy() {
        String password = passwordTextField.getText();
        if (password != null && !password.isEmpty()) {
            ClipboardUtil.copyToClipboard(password);
            showAlert(Alert.AlertType.INFORMATION, "成功", "密码已复制到剪贴板");
        }
    }

    @FXML
    private void handleBatchGenerate() {
        try {
            int count = Integer.parseInt(batchCountTextField.getText());
            if (count < 1 || count > 100) {
                showAlert(Alert.AlertType.WARNING, "提示", "批量生成数量应在1-100之间");
                return;
            }

            List<String> passwords = generator.generateBatch(count);
            generatedPasswords.setAll(passwords);
        } catch (NumberFormatException e) {
            showAlert(Alert.AlertType.WARNING, "提示", "请输入有效的数字");
        }
    }

    @FXML
    private void handleCopyBatchSelected() {
        String selected = batchListView.getSelectionModel().getSelectedItem();
        if (selected != null) {
            ClipboardUtil.copyToClipboard(selected);
            showAlert(Alert.AlertType.INFORMATION, "成功", "密码已复制到剪贴板");
        } else {
            showAlert(Alert.AlertType.WARNING, "提示", "请先选择一条密码");
        }
    }

    @FXML
    private void handleCopyAllBatch() {
        if (generatedPasswords.isEmpty()) {
            showAlert(Alert.AlertType.WARNING, "提示", "没有密码可复制");
            return;
        }

        StringBuilder sb = new StringBuilder();
        for (String pwd : generatedPasswords) {
            sb.append(pwd).append(System.lineSeparator());
        }
        ClipboardUtil.copyToClipboard(sb.toString().trim());
        showAlert(Alert.AlertType.INFORMATION, "成功", "已复制 " + generatedPasswords.size() + " 个密码");
    }

    @FXML
    private void handleSaveSelectedToVault() {
        String selected = batchListView.getSelectionModel().getSelectedItem();
        if (selected == null) {
            showAlert(Alert.AlertType.WARNING, "提示", "请先选择一条密码");
            return;
        }

        TextInputDialog dialog = new TextInputDialog();
        dialog.setTitle("保存密码到库");
        dialog.setHeaderText("输入标题保存密码（留空使用默认命名）");
        dialog.setContentText("标题:");

        int index = batchListView.getSelectionModel().getSelectedIndex() + 1;
        dialog.getEditor().setText("Generated_" + index);

        java.util.Optional<String> result = dialog.showAndWait();
        result.ifPresent(title -> {
            String finalTitle = title.trim().isEmpty() ? "Generated_" + index : title.trim();

            try {
                PasswordEntry entry = createPasswordEntry(finalTitle, selected);
                dataStorageService.addPasswordEntry(entry);
                showAlert(Alert.AlertType.INFORMATION, "成功", "密码已保存到库，标题: " + finalTitle);
            } catch (Exception e) {
                e.printStackTrace();
                showAlert(Alert.AlertType.ERROR, "错误", "保存失败: " + e.getMessage());
            }
        });
    }

    @FXML
    private void handleSaveAllToVault() {
        if (generatedPasswords.isEmpty()) {
            showAlert(Alert.AlertType.WARNING, "提示", "没有密码可保存");
            return;
        }

        TextInputDialog dialog = new TextInputDialog();
        dialog.setTitle("批量保存密码");
        dialog.setHeaderText("输入标题前缀（留空使用默认 Generated_序号）");
        dialog.setContentText("标题前缀:");
        dialog.getEditor().setText("Generated");

        java.util.Optional<String> result = dialog.showAndWait();
        result.ifPresent(prefix -> {
            String titlePrefix = prefix.trim().isEmpty() ? "Generated" : prefix.trim();
            int savedCount = 0;

            try {
                for (int i = 0; i < generatedPasswords.size(); i++) {
                    String title = titlePrefix + "_" + (i + 1);
                    PasswordEntry entry = createPasswordEntry(title, generatedPasswords.get(i));
                    dataStorageService.addPasswordEntry(entry);
                    savedCount++;
                }
                showAlert(Alert.AlertType.INFORMATION, "成功", "已保存 " + savedCount + " 个密码到库（命名格式: " + titlePrefix + "_序号）");
            } catch (Exception e) {
                e.printStackTrace();
                showAlert(Alert.AlertType.ERROR, "错误", "保存失败: " + e.getMessage() + "（已保存 " + savedCount + " 个）");
            }
        });
    }

    private PasswordEntry createPasswordEntry(String title, String password) {
        PasswordEntry entry = new PasswordEntry();
        entry.setTitle(title);
        entry.setPassword(password);
        entry.setCategory(PasswordCategory.OTHER);
        entry.setPasswordExpiryEnabled(true);
        entry.setExpiryDate(java.time.LocalDate.now().plusDays(90));
        return entry;
    }

    @FXML
    private void handleClose() {
        Stage stage = (Stage) passwordTextField.getScene().getWindow();
        stage.close();
    }

    private void generatePassword() {
        String password = generator.generate();
        passwordTextField.setText(password);
        updateStrengthIndicator(password);
    }

    private void updateStrengthIndicator(String password) {
        PasswordStrengthChecker.Strength strength = PasswordStrengthChecker.checkStrength(password);
        strengthValueLabel.setText(strength.getDisplayName());

        switch (strength) {
            case VERY_WEAK:
                strengthValueLabel.setTextFill(Color.RED);
                break;
            case WEAK:
                strengthValueLabel.setTextFill(Color.ORANGE);
                break;
            case FAIR:
                strengthValueLabel.setTextFill(Color.YELLOW);
                break;
            case STRONG:
                strengthValueLabel.setTextFill(Color.LIGHTGREEN);
                break;
            case VERY_STRONG:
                strengthValueLabel.setTextFill(Color.GREEN);
                break;
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
