package com.passwordmanager.controller;

import com.passwordmanager.AppContext;
import com.passwordmanager.model.PasswordCategory;
import com.passwordmanager.model.PasswordEntry;
import com.passwordmanager.service.DataStorageService;
import com.passwordmanager.util.PasswordGenerator;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.*;
import javafx.stage.Stage;

import java.net.URL;
import java.time.LocalDate;
import java.util.ResourceBundle;

public class PasswordDialogController implements Initializable {

    @FXML
    private TextField titleTextField;

    @FXML
    private TextField usernameTextField;

    @FXML
    private PasswordField passwordField;

    @FXML
    private TextField urlTextField;

    @FXML
    private ComboBox<String> categoryComboBox;

    @FXML
    private TextArea notesTextArea;

    @FXML
    private CheckBox favoriteCheckBox;

    @FXML
    private CheckBox expiryEnabledCheckBox;

    @FXML
    private Label expiryLabel;

    @FXML
    private DatePicker expiryDatePicker;

    @FXML
    private ComboBox<String> expiryDaysComboBox;

    private PasswordEntry passwordEntry;
    private DataStorageService dataStorageService;
    private boolean isEditMode = false;
    private boolean showPassword = false;

    @Override
    public void initialize(URL location, ResourceBundle resources) {
        dataStorageService = AppContext.getInstance().getDataStorageService();
        initializeCategoryComboBox();
        updateExpiryControlsState();

        expiryDaysComboBox.getSelectionModel().selectedItemProperty().addListener((obs, oldVal, newVal) -> {
            if (newVal != null) {
                int days = parseDaysFromSelection(newVal);
                if (days > 0) {
                    expiryDatePicker.setValue(LocalDate.now().plusDays(days));
                }
            }
        });

        expiryDatePicker.valueProperty().addListener((obs, oldVal, newVal) -> {
            if (newVal != null) {
                expiryDaysComboBox.getSelectionModel().clearSelection();
            }
        });
    }

    private int parseDaysFromSelection(String selection) {
        if (selection == null) return 0;
        if (selection.contains("7")) return 7;
        if (selection.contains("30")) return 30;
        if (selection.contains("60")) return 60;
        if (selection.contains("90")) return 90;
        if (selection.contains("180")) return 180;
        if (selection.contains("365")) return 365;
        return 0;
    }

    private void initializeCategoryComboBox() {
        for (PasswordCategory category : PasswordCategory.values()) {
            categoryComboBox.getItems().add(category.getDisplayName());
        }
        categoryComboBox.getSelectionModel().selectFirst();
    }

    public void setPasswordEntry(PasswordEntry entry) {
        this.passwordEntry = entry;
        if (entry != null) {
            isEditMode = true;
            populateFields();
        }
    }

    private void populateFields() {
        titleTextField.setText(passwordEntry.getTitle());
        usernameTextField.setText(passwordEntry.getUsername());
        passwordField.setText(passwordEntry.getPassword());
        urlTextField.setText(passwordEntry.getUrl());
        notesTextArea.setText(passwordEntry.getNotes());
        favoriteCheckBox.setSelected(passwordEntry.isFavorite());

        if (passwordEntry.getCategory() != null) {
            categoryComboBox.getSelectionModel().select(passwordEntry.getCategory().getDisplayName());
        }

        expiryEnabledCheckBox.setSelected(passwordEntry.isPasswordExpiryEnabled());
        if (passwordEntry.getExpiryDate() != null) {
            expiryDatePicker.setValue(passwordEntry.getExpiryDate());
        }

        updateExpiryControlsState();
    }

    @FXML
    private void handleExpiryToggle() {
        updateExpiryControlsState();
    }

    private void updateExpiryControlsState() {
        boolean enabled = expiryEnabledCheckBox.isSelected();
        expiryLabel.setDisable(!enabled);
        expiryDatePicker.setDisable(!enabled);
        expiryDaysComboBox.setDisable(!enabled);
    }

    @FXML
    private void handleGeneratePassword() {
        PasswordGenerator generator = new PasswordGenerator();
        generator.setLength(16);
        generator.setIncludeUppercase(true);
        generator.setIncludeLowercase(true);
        generator.setIncludeNumbers(true);
        generator.setIncludeSymbols(true);
        String password = generator.generate();
        passwordField.setText(password);
    }

    @FXML
    private void handleTogglePasswordVisibility() {
        showPassword = !showPassword;
    }

    @FXML
    private void handleSave() {
        String title = titleTextField.getText().trim();
        String password = passwordField.getText();

        if (title.isEmpty()) {
            showAlert(Alert.AlertType.WARNING, "提示", "请输入标题");
            return;
        }

        if (password.isEmpty()) {
            showAlert(Alert.AlertType.WARNING, "提示", "请输入密码");
            return;
        }

        try {
            PasswordCategory category = PasswordCategory.fromDisplayName(
                    categoryComboBox.getSelectionModel().getSelectedItem()
            );

            boolean expiryEnabled = expiryEnabledCheckBox.isSelected();
            LocalDate expiryDate = expiryDatePicker.getValue();

            if (isEditMode && passwordEntry != null) {
                String oldPassword = passwordEntry.getPassword();

                passwordEntry.setTitle(title);
                passwordEntry.setUsername(usernameTextField.getText());
                passwordEntry.setPassword(password);
                passwordEntry.setUrl(urlTextField.getText());
                passwordEntry.setNotes(notesTextArea.getText());
                passwordEntry.setCategory(category);
                passwordEntry.setFavorite(favoriteCheckBox.isSelected());
                passwordEntry.setPasswordExpiryEnabled(expiryEnabled);
                passwordEntry.setExpiryDate(expiryEnabled ? expiryDate : null);
                passwordEntry.updateTimestamp();

                dataStorageService.updatePasswordEntry(passwordEntry, oldPassword);
            } else {
                PasswordEntry newEntry = new PasswordEntry();
                newEntry.setTitle(title);
                newEntry.setUsername(usernameTextField.getText());
                newEntry.setPassword(password);
                newEntry.setUrl(urlTextField.getText());
                newEntry.setNotes(notesTextArea.getText());
                newEntry.setCategory(category);
                newEntry.setFavorite(favoriteCheckBox.isSelected());
                newEntry.setPasswordExpiryEnabled(expiryEnabled);
                newEntry.setExpiryDate(expiryEnabled ? expiryDate : null);

                dataStorageService.addPasswordEntry(newEntry);
            }

            closeDialog();
        } catch (Exception e) {
            e.printStackTrace();
            showAlert(Alert.AlertType.ERROR, "错误", "保存失败: " + e.getMessage());
        }
    }

    @FXML
    private void handleCancel() {
        closeDialog();
    }

    private void closeDialog() {
        Stage stage = (Stage) titleTextField.getScene().getWindow();
        stage.close();
    }

    private void showAlert(Alert.AlertType type, String title, String content) {
        Alert alert = new Alert(type);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(content);
        alert.showAndWait();
    }
}
