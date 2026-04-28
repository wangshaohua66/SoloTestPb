package com.passwordmanager.controller;

import com.passwordmanager.model.PasswordEntry;
import com.passwordmanager.model.PasswordHistory;
import com.passwordmanager.service.DataStorageService;
import com.passwordmanager.util.ClipboardUtil;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.*;
import javafx.scene.layout.HBox;
import javafx.stage.Stage;

import java.net.URL;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.ResourceBundle;

public class PasswordHistoryController implements Initializable {

    @FXML
    private Label entryTitleLabel;

    @FXML
    private Label titleLabel;

    @FXML
    private Label usernameLabel;

    @FXML
    private TableView<PasswordHistory> historyTableView;

    @FXML
    private TableColumn<PasswordHistory, String> changedAtColumn;

    @FXML
    private TableColumn<PasswordHistory, PasswordHistory.ActionType> actionTypeColumn;

    @FXML
    private TableColumn<PasswordHistory, String> oldPasswordColumn;

    private PasswordEntry passwordEntry;
    private DataStorageService dataStorageService;
    private ObservableList<PasswordHistory> historyList;

    @Override
    public void initialize(URL location, ResourceBundle resources) {
        historyList = FXCollections.observableArrayList();
        historyTableView.setItems(historyList);

        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        changedAtColumn.setCellFactory(column -> new TableCell<PasswordHistory, String>() {
            @Override
            protected void updateItem(String item, boolean empty) {
                super.updateItem(item, empty);
                if (empty) {
                    setText(null);
                } else {
                    setText(item);
                }
            }
        });

        changedAtColumn.setCellValueFactory(cellData -> {
            PasswordHistory history = cellData.getValue();
            if (history.getChangedAt() != null) {
                return new javafx.beans.property.SimpleStringProperty(
                        history.getChangedAt().format(formatter));
            }
            return new javafx.beans.property.SimpleStringProperty("--");
        });

        actionTypeColumn.setCellValueFactory(cellData -> {
            PasswordHistory history = cellData.getValue();
            return new javafx.beans.property.SimpleObjectProperty<>(history.getActionType());
        });

        actionTypeColumn.setCellFactory(column -> new TableCell<PasswordHistory, PasswordHistory.ActionType>() {
            @Override
            protected void updateItem(PasswordHistory.ActionType item, boolean empty) {
                super.updateItem(item, empty);
                if (empty || item == null) {
                    setText(null);
                } else {
                    setText(item.getDisplayName());
                }
            }
        });

        oldPasswordColumn.setCellFactory(column -> new TableCell<PasswordHistory, String>() {
            private final HBox contentBox = new HBox(5);
            private final Label passwordLabel = new Label();
            private final Button toggleButton = new Button("显示");

            {
                toggleButton.setStyle("-fx-font-size: 10px; -fx-padding: 2 8; -fx-background-color: #3498db; -fx-text-fill: white;");
                passwordLabel.setStyle("-fx-font-family: monospace;");

                toggleButton.setOnAction(event -> {
                    int index = getIndex();
                    if (index >= 0 && index < historyList.size()) {
                        PasswordHistory history = historyList.get(index);
                        String currentText = passwordLabel.getText();

                        if ("********".equals(currentText) || currentText == null) {
                            passwordLabel.setText(history.getOldPassword());
                            toggleButton.setText("隐藏");
                        } else {
                            passwordLabel.setText("********");
                            toggleButton.setText("显示");
                        }
                    }
                });

                contentBox.getChildren().addAll(passwordLabel, toggleButton);
            }

            @Override
            protected void updateItem(String item, boolean empty) {
                super.updateItem(item, empty);
                if (empty || item == null) {
                    setText(null);
                    setGraphic(null);
                } else {
                    passwordLabel.setText("********");
                    toggleButton.setText("显示");
                    setGraphic(contentBox);
                    setText(null);
                }
            }
        });
    }

    public void setPasswordEntry(PasswordEntry entry, DataStorageService storageService) {
        this.passwordEntry = entry;
        this.dataStorageService = storageService;

        if (entry != null) {
            entryTitleLabel.setText("\"" + entry.getTitle() + "\"");
            titleLabel.setText(entry.getTitle() != null ? entry.getTitle() : "--");
            usernameLabel.setText(entry.getUsername() != null ? entry.getUsername() : "--");

            loadHistory();
        }
    }

    private void loadHistory() {
        if (passwordEntry != null && dataStorageService != null) {
            List<PasswordHistory> histories = dataStorageService.getPasswordHistoriesByEntryId(passwordEntry.getId());
            historyList.setAll(histories);
        }
    }

    @FXML
    private void handleCopySelected() {
        PasswordHistory selected = historyTableView.getSelectionModel().getSelectedItem();
        if (selected != null) {
            ClipboardUtil.copyToClipboard(selected.getOldPassword());
            showAlert(Alert.AlertType.INFORMATION, "成功", "密码已复制到剪贴板");
        } else {
            showAlert(Alert.AlertType.WARNING, "提示", "请先选择一条历史记录");
        }
    }

    @FXML
    private void handleClose() {
        Stage stage = (Stage) historyTableView.getScene().getWindow();
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
