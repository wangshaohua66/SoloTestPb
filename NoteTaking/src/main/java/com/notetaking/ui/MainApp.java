package com.notetaking.ui;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.image.Image;
import javafx.stage.Stage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.Objects;

public class MainApp extends Application {
    private static final Logger logger = LoggerFactory.getLogger(MainApp.class);
    private static final String APP_TITLE = "笔记管理";
    private static final double MIN_WIDTH = 1000.0;
    private static final double MIN_HEIGHT = 700.0;

    private Stage primaryStage;

    @Override
    public void start(Stage primaryStage) {
        this.primaryStage = primaryStage;
        this.primaryStage.setTitle(APP_TITLE);
        this.primaryStage.setMinWidth(MIN_WIDTH);
        this.primaryStage.setMinHeight(MIN_HEIGHT);

        try {
            loadMainScene();
        } catch (IOException e) {
            logger.error("无法加载主界面", e);
            System.exit(1);
        }

        this.primaryStage.show();
        logger.info("应用启动成功");
    }

    private void loadMainScene() throws IOException {
        FXMLLoader loader = new FXMLLoader();
        loader.setLocation(MainApp.class.getResource("/fxml/MainView.fxml"));
        Parent root = loader.load();

        Scene scene = new Scene(root);
        scene.getStylesheets().add(Objects.requireNonNull(
                MainApp.class.getResource("/css/style.css")
        ).toExternalForm());

        primaryStage.setScene(scene);

        MainController controller = loader.getController();
        controller.setMainApp(this);
    }

    public Stage getPrimaryStage() {
        return primaryStage;
    }

    public static void main(String[] args) {
        launch(args);
    }
}
