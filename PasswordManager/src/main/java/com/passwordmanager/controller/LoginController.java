package com.passwordmanager.controller;

import com.passwordmanager.AppContext;
import com.passwordmanager.service.DataStorageService;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.fxml.Initializable;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Button;
import javafx.scene.control.Label;
import javafx.scene.control.PasswordField;
import javafx.scene.input.KeyEvent;
import javafx.scene.input.MouseEvent;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;

import java.io.IOException;
import java.net.URL;
import java.util.ResourceBundle;

public class LoginController implements Initializable {

    @FXML
    private PasswordField setupPasswordField;

    @FXML
    private PasswordField confirmPasswordField;

    @FXML
    private PasswordField masterPasswordField;

    @FXML
    private VBox setupPasswordVBox;

    @FXML
    private VBox loginPasswordVBox;

    @FXML
    private Label welcomeLabel;

    @FXML
    private Label errorLabel;

    @FXML
    private Button loginButton;

    private DataStorageService dataStorageService;

    @Override
    public void initialize(URL location, ResourceBundle resources) {
        dataStorageService = AppContext.getInstance().getDataStorageService();

        if (dataStorageService.isFirstTimeSetup()) {
            showSetupMode();
        } else {
            showLoginMode();
        }

        setupUserActivityListener();
    }

    private void setupUserActivityListener() {
        Scene scene = loginButton.getScene();
        if (scene != null) {
            addActivityListenersToScene(scene);
        } else {
            loginButton.sceneProperty().addListener((obs, oldScene, newScene) -> {
                if (newScene != null) {
                    addActivityListenersToScene(newScene);
                }
            });
        }
    }

    private void addActivityListenersToScene(Scene scene) {
        scene.addEventFilter(MouseEvent.MOUSE_PRESSED, event -> {
            AppContext.getInstance().updateUserActivity();
        });

        scene.addEventFilter(KeyEvent.KEY_PRESSED, event -> {
            AppContext.getInstance().updateUserActivity();
        });
    }

    private void showSetupMode() {
        setupPasswordVBox.setVisible(true);
        loginPasswordVBox.setVisible(false);
        welcomeLabel.setText("首次使用，请设置主密码");
        loginButton.setText("设置密码");
    }

    private void showLoginMode() {
        setupPasswordVBox.setVisible(false);
        loginPasswordVBox.setVisible(true);
        welcomeLabel.setText("请输入主密码");
        loginButton.setText("登录");
    }

    @FXML
    private void handleLogin() {
        try {
            if (dataStorageService.isFirstTimeSetup()) {
                handleSetupPassword();
            } else {
                handleVerifyPassword();
            }
        } catch (Exception e) {
            e.printStackTrace();
            showError("操作失败: " + e.getMessage());
        }
    }

    private void handleSetupPassword() throws Exception {
        String password = setupPasswordField.getText();
        String confirmPassword = confirmPasswordField.getText();

        if (password == null || password.isEmpty()) {
            showError("请输入主密码");
            return;
        }

        if (password.length() < 6) {
            showError("主密码至少需要6个字符");
            return;
        }

        if (!password.equals(confirmPassword)) {
            showError("两次输入的密码不一致");
            return;
        }

        boolean success = dataStorageService.createMasterPassword(password.toCharArray());

        if (success) {
            clearPasswordFields();
            openMainWindow();
        } else {
            showError("设置主密码失败");
        }
    }

    private void handleVerifyPassword() throws Exception {
        String password = masterPasswordField.getText();

        if (password == null || password.isEmpty()) {
            showError("请输入主密码");
            return;
        }

        boolean success = dataStorageService.verifyMasterPassword(password.toCharArray());

        if (success) {
            clearPasswordFields();
            openMainWindow();
        } else {
            showError("密码错误，请重试");
        }
    }

    private void openMainWindow() {
        try {
            Stage currentStage = (Stage) loginButton.getScene().getWindow();
            Stage mainStage = new Stage();

            FXMLLoader loader = new FXMLLoader(getClass().getResource("/fxml/main.fxml"));
            Parent root = loader.load();

            Scene scene = new Scene(root);
            mainStage.setScene(scene);
            mainStage.setTitle("密码管理器");
            mainStage.setResizable(true);
            mainStage.setOnCloseRequest(event -> {
                dataStorageService.lock();
            });

            AppContext.getInstance().setPrimaryStage(mainStage);

            currentStage.close();
            mainStage.show();
        } catch (IOException e) {
            e.printStackTrace();
            showError("打开主窗口失败: " + e.getMessage());
        }
    }

    private void showError(String message) {
        errorLabel.setText(message);
        errorLabel.setVisible(true);
    }

    private void clearPasswordFields() {
        if (setupPasswordField != null) {
            setupPasswordField.clear();
        }
        if (confirmPasswordField != null) {
            confirmPasswordField.clear();
        }
        if (masterPasswordField != null) {
            masterPasswordField.clear();
        }
    }
}
