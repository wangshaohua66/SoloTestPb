package com.colorpicker;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.image.Image;
import javafx.stage.Stage;

import java.io.IOException;
import java.util.Objects;

public class MainApp extends Application {

    private static Stage primaryStage;
    private static Scene mainScene;

    @Override
    public void start(Stage stage) throws IOException {
        primaryStage = stage;
        loadMainScene();
        
        stage.setTitle("ColorPicker - 颜色选择器");
        stage.setResizable(true);
        stage.setMinWidth(900);
        stage.setMinHeight(700);
        
        try {
            stage.getIcons().add(new Image(
                    Objects.requireNonNull(getClass().getResourceAsStream("/icons/app_icon.png"))
            ));
        } catch (Exception e) {
        }
        
        stage.show();
    }

    private void loadMainScene() throws IOException {
        Parent root = FXMLLoader.load(
                Objects.requireNonNull(getClass().getResource("/fxml/MainView.fxml"))
        );
        mainScene = new Scene(root, 900, 700);
        mainScene.getStylesheets().add(
                Objects.requireNonNull(getClass().getResource("/css/style.css")).toExternalForm()
        );
        primaryStage.setScene(mainScene);
    }

    public static Stage getPrimaryStage() {
        return primaryStage;
    }

    public static Scene getMainScene() {
        return mainScene;
    }

    public static void main(String[] args) {
        launch();
    }
}
