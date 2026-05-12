package com.passwordmanager;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

import java.util.Objects;

public class PasswordManagerApp extends Application {

    @Override
    public void start(Stage primaryStage) throws Exception {
        Parent root = FXMLLoader.load(Objects.requireNonNull(getClass().getResource("/fxml/login.fxml")));

        Scene scene = new Scene(root);
        primaryStage.setScene(scene);
        primaryStage.setTitle("密码管理器");
        primaryStage.setResizable(false);
        primaryStage.setOnCloseRequest(event -> {
            AppContext.getInstance().getDataStorageService().lock();
            System.exit(0);
        });

        AppContext.getInstance().setPrimaryStage(primaryStage);
        primaryStage.show();
    }

    public static void main(String[] args) {
        launch(args);
    }
}
