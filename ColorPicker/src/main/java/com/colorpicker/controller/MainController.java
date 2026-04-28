package com.colorpicker.controller;

import com.colorpicker.component.ColorWheel;
import com.colorpicker.component.Magnifier;
import com.colorpicker.model.ColorModel;
import com.colorpicker.model.HSV;
import com.colorpicker.model.RGBConverter;
import com.colorpicker.util.*;
import javafx.application.Platform;
import javafx.beans.value.ChangeListener;
import javafx.embed.swing.SwingFXUtils;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.control.*;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.*;
import javafx.scene.paint.Color;
import javafx.scene.shape.Rectangle;
import javafx.scene.input.Clipboard;
import javafx.scene.input.ClipboardContent;
import javafx.stage.FileChooser;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.ResourceBundle;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class MainController implements Initializable {

    @FXML
    private TabPane mainTabPane;

    @FXML
    private StackPane colorWheelContainer;

    @FXML
    private Rectangle colorPreviewRect;

    @FXML
    private Label colorHexLabel, colorNameLabel, colorHexValueLabel;
    @FXML
    private Label colorRgbValueLabel, colorHsvValueLabel;

    @FXML
    private Slider redSlider, greenSlider, blueSlider, alphaSlider;

    @FXML
    private TextField redField, greenField, blueField, alphaField;

    @FXML
    private Slider hueSlider, saturationSlider, valueSlider;

    @FXML
    private TextField hueField, saturationField, valueField;

    @FXML
    private TextField hexField, colorNameSearchField;

    @FXML
    private ComboBox<String> harmonyCombo;

    @FXML
    private HBox harmonyColorsBox;

    @FXML
    private ColorPicker foregroundPicker, backgroundPicker;

    @FXML
    private Label contrastRatioLabel, wcagLevelLabel;

    @FXML
    private Label normalTextAA, normalTextAAA, largeTextAA, largeTextAAA;

    @FXML
    private StackPane contrastPreview;

    @FXML
    private Label contrastTextNormal, contrastTextLarge;

    @FXML
    private Button startPickerBtn, clearHistoryBtn;

    @FXML
    private Label pickerStatusLabel, pickerCoordsLabel;

    @FXML
    private Rectangle pickerPreviewRect;

    @FXML
    private Label pickerHexLabel, pickerRgbLabel;

    @FXML
    private StackPane magnifierContainer;

    @FXML
    private ComboBox<Integer> zoomCombo;

    @FXML
    private CheckBox showGridCheckBox, showCrosshairCheckBox;

    @FXML
    private ListView<HBox> historyListView;

    @FXML
    private ListView<HBox> favoritesListView;

    @FXML
    private TextField searchField;

    @FXML
    private ComboBox<String> exportFormatCombo;

    @FXML
    private TextArea exportTextArea;

    @FXML
    private ColorPicker gradStartPicker, gradEndPicker;

    @FXML
    private Slider gradStepsSlider;

    @FXML
    private HBox gradientPreviewBox;

    @FXML
    private TextArea cssGradientTextArea;

    @FXML
    private Button openImageBtn, extractColorsBtn;

    @FXML
    private Label imageInfoLabel;

    @FXML
    private StackPane imagePreviewContainer;

    @FXML
    private ComboBox<Integer> extractColorCountCombo;

    @FXML
    private CheckBox extractByHueCheckBox;

    @FXML
    private HBox dominantColorsBox;

    @FXML
    private VBox hueGroupContainer;

    @FXML
    private TabPane extractResultTabPane;

    private ColorModel currentColor;
    private ColorModel lastPickedColor;
    private ColorManager colorManager;
    private ScreenPicker screenPicker;
    private ColorWheel colorWheel;
    private Magnifier magnifier;
    private ScheduledExecutorService pickerExecutor;
    private boolean isPickerRunning = false;
    private BufferedImage loadedImage;
    private ImageView imageView;

    private boolean isUpdatingFromWheel = false;
    private boolean isUpdatingFromSliders = false;
    
    private static final boolean IS_MAC = System.getProperty("os.name").toLowerCase().contains("mac");
    private static final boolean IS_WINDOWS = System.getProperty("os.name").toLowerCase().contains("win");
    private static final boolean IS_LINUX = System.getProperty("os.name").toLowerCase().contains("nux") ||
                                              System.getProperty("os.name").toLowerCase().contains("nix") ||
                                              System.getProperty("os.name").toLowerCase().contains("aix");

    @Override
    public void initialize(URL url, ResourceBundle resourceBundle) {
        currentColor = new ColorModel(100, 150, 200);
        colorManager = new ColorManager();
        screenPicker = new ScreenPicker();

        initializeColorWheel();
        initializeMagnifier();
        initializeSliders();
        initializeColorInputs();
        initializeHarmony();
        initializeContrast();
        initializePicker();
        initializeFavorites();
        initializeGradient();
        initializeExport();
        initializeImageExtractor();

        updateUIFromColor();
        
        Platform.runLater(this::setupGlobalHotkeys);
    }
    
    private void setupGlobalHotkeys() {
        if (com.colorpicker.MainApp.getMainScene() != null) {
            com.colorpicker.MainApp.getMainScene().setOnKeyPressed(e -> {
                boolean isModifierDown = IS_MAC ? e.isMetaDown() : e.isControlDown();
                
                if (isModifierDown && e.isShiftDown() && e.getCode() == javafx.scene.input.KeyCode.C) {
                    toggleScreenPicker();
                }
                
                if (e.getCode() == javafx.scene.input.KeyCode.SPACE) {
                    if (isPickerRunning) {
                        confirmCurrentPick();
                    }
                }
                
                if (e.getCode() == javafx.scene.input.KeyCode.ESCAPE) {
                    if (isPickerRunning) {
                        stopScreenPicker();
                    }
                }
            });
        }
    }

    private void initializeColorWheel() {
        colorWheel = new ColorWheel(340, 240);
        colorWheel.setColor(currentColor);
        colorWheel.addColorChangeListener(color -> {
            if (!isUpdatingFromSliders) {
                isUpdatingFromWheel = true;
                currentColor = color;
                updateUIFromColor();
                isUpdatingFromWheel = false;
            }
        });
        colorWheelContainer.getChildren().add(colorWheel);
    }

    private void initializeMagnifier() {
        magnifier = new Magnifier(200, 200);
        magnifierContainer.getChildren().add(magnifier);
        
        zoomCombo.getItems().addAll(2, 4, 6, 8, 10, 12, 16);
        zoomCombo.setValue(8);
        zoomCombo.setOnAction(e -> magnifier.setZoomFactor(zoomCombo.getValue()));
        
        showGridCheckBox.selectedProperty().addListener((obs, old, newVal) -> 
            magnifier.setShowGrid(newVal));
        showCrosshairCheckBox.selectedProperty().addListener((obs, old, newVal) -> 
            magnifier.setShowCrosshair(newVal));
        
        magnifierContainer.setOnScroll(e -> {
            int delta = e.getDeltaY() > 0 ? 2 : -2;
            int currentZoom = zoomCombo.getValue();
            int newZoom = Math.max(2, Math.min(16, currentZoom + delta));
            zoomCombo.setValue(newZoom);
            magnifier.setZoomFactor(newZoom);
        });
        
        magnifierContainer.setOnMouseClicked(e -> {
            if (isPickerRunning) {
                confirmCurrentPick();
            }
        });
    }

    private void initializeSliders() {
        redSlider.valueProperty().addListener((obs, old, newVal) -> {
            if (!isUpdatingFromWheel) {
                int value = newVal.intValue();
                redField.setText(String.valueOf(value));
                updateColorFromRGB();
            }
        });

        greenSlider.valueProperty().addListener((obs, old, newVal) -> {
            if (!isUpdatingFromWheel) {
                int value = newVal.intValue();
                greenField.setText(String.valueOf(value));
                updateColorFromRGB();
            }
        });

        blueSlider.valueProperty().addListener((obs, old, newVal) -> {
            if (!isUpdatingFromWheel) {
                int value = newVal.intValue();
                blueField.setText(String.valueOf(value));
                updateColorFromRGB();
            }
        });

        alphaSlider.valueProperty().addListener((obs, old, newVal) -> {
            if (!isUpdatingFromWheel) {
                double value = newVal.doubleValue();
                alphaField.setText(String.format("%.2f", value));
                updateColorFromRGB();
            }
        });

        hueSlider.valueProperty().addListener((obs, old, newVal) -> {
            if (!isUpdatingFromWheel) {
                double value = newVal.doubleValue();
                hueField.setText(String.format("%.0f", value));
                updateColorFromHSV();
            }
        });

        saturationSlider.valueProperty().addListener((obs, old, newVal) -> {
            if (!isUpdatingFromWheel) {
                double value = newVal.doubleValue() / 100.0;
                saturationField.setText(String.format("%.0f%%", newVal.doubleValue()));
                updateColorFromHSV();
            }
        });

        valueSlider.valueProperty().addListener((obs, old, newVal) -> {
            if (!isUpdatingFromWheel) {
                double value = newVal.doubleValue() / 100.0;
                valueField.setText(String.format("%.0f%%", newVal.doubleValue()));
                updateColorFromHSV();
            }
        });
    }

    private void initializeColorInputs() {
        redField.textProperty().addListener((obs, old, newVal) -> {
            if (!isUpdatingFromWheel) {
                try {
                    int val = Integer.parseInt(newVal);
                    if (val >= 0 && val <= 255) {
                        redSlider.setValue(val);
                    }
                } catch (NumberFormatException e) {
                }
            }
        });

        greenField.textProperty().addListener((obs, old, newVal) -> {
            if (!isUpdatingFromWheel) {
                try {
                    int val = Integer.parseInt(newVal);
                    if (val >= 0 && val <= 255) {
                        greenSlider.setValue(val);
                    }
                } catch (NumberFormatException e) {
                }
            }
        });

        blueField.textProperty().addListener((obs, old, newVal) -> {
            if (!isUpdatingFromWheel) {
                try {
                    int val = Integer.parseInt(newVal);
                    if (val >= 0 && val <= 255) {
                        blueSlider.setValue(val);
                    }
                } catch (NumberFormatException e) {
                }
            }
        });

        alphaField.textProperty().addListener((obs, old, newVal) -> {
            if (!isUpdatingFromWheel) {
                try {
                    double val = Double.parseDouble(newVal);
                    if (val >= 0 && val <= 1.0) {
                        alphaSlider.setValue(val);
                    }
                } catch (NumberFormatException e) {
                }
            }
        });

        hexField.setOnAction(e -> {
            try {
                ColorModel color = ColorModel.fromHEX(hexField.getText());
                currentColor = color;
                updateUIFromColor();
            } catch (Exception ex) {
                showAlert("无效的HEX颜色", "请输入有效的HEX颜色值");
            }
        });
    }

    @FXML
    private void searchColorName() {
        String searchText = colorNameSearchField.getText().trim();
        if (searchText.isEmpty()) {
            return;
        }

        ColorModel color = ColorNameRegistry.getColorByName(searchText);
        if (color != null) {
            currentColor = color;
            updateUIFromColor();
            showInfo("找到颜色: " + searchText);
        } else {
            List<ColorNameRegistry.ColorNameResult> similar = ColorNameRegistry.findSimilarColors(currentColor, 5);
            if (!similar.isEmpty()) {
                StringBuilder sb = new StringBuilder("未找到该颜色。相近颜色:\n");
                for (int i = 0; i < Math.min(3, similar.size()); i++) {
                    sb.append(i + 1).append(". ").append(similar.get(i).getName()).append("\n");
                }
                showAlert("颜色未找到", sb.toString());
            } else {
                showAlert("颜色未找到", "未找到匹配的颜色名称");
            }
        }
    }

    private void initializeHarmony() {
        harmonyCombo.getItems().addAll(
                "互补色 (Complementary)",
                "类似色 (Analogous)",
                "三角 (Triadic)",
                "四角 (Tetradic)",
                "分裂互补 (Split Complementary)",
                "单色 (Monochromatic)"
        );
        harmonyCombo.setValue("互补色 (Complementary)");

        harmonyCombo.setOnAction(e -> updateHarmonyColors());
    }

    private void initializeContrast() {
        foregroundPicker.setValue(Color.RED);
        backgroundPicker.setValue(Color.WHITE);

        ChangeListener<Color> contrastListener = (obs, old, newVal) -> updateContrast();
        foregroundPicker.valueProperty().addListener(contrastListener);
        backgroundPicker.valueProperty().addListener(contrastListener);

        updateContrast();
    }

    private void initializePicker() {
        startPickerBtn.setOnAction(e -> toggleScreenPicker());
        
        pickerPreviewRect.setOnMouseClicked(e -> {
            if (isPickerRunning) {
                confirmCurrentPick();
            }
        });
        
        pickerPreviewRect.setStyle("-fx-cursor: hand;");
    }

    private void initializeFavorites() {
        searchField.textProperty().addListener((obs, old, newVal) -> updateSearchResults());
    }

    private void initializeGradient() {
        gradStartPicker.setValue(Color.RED);
        gradEndPicker.setValue(Color.BLUE);
        gradStepsSlider.setValue(10);

        ChangeListener<Color> gradListener = (obs, old, newVal) -> updateGradient();
        gradStartPicker.valueProperty().addListener(gradListener);
        gradEndPicker.valueProperty().addListener(gradListener);
        gradStepsSlider.valueProperty().addListener((obs, old, newVal) -> updateGradient());

        updateGradient();
    }

    private void initializeExport() {
        exportFormatCombo.getItems().addAll("CSS", "SASS", "LESS", "JSON", "Android", "iOS");
        exportFormatCombo.setValue("CSS");

        exportFormatCombo.setOnAction(e -> updateExportText());
    }

    private void initializeImageExtractor() {
        extractColorCountCombo.getItems().addAll(3, 4, 5, 6, 8, 10, 12);
        extractColorCountCombo.setValue(5);
        
        imageView = new ImageView();
        imageView.setFitHeight(250);
        imageView.setPreserveRatio(true);
        imagePreviewContainer.getChildren().add(imageView);
    }

    @FXML
    private void openImageFile() {
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("选择图片");
        fileChooser.getExtensionFilters().addAll(
            new FileChooser.ExtensionFilter("图片文件", "*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp"),
            new FileChooser.ExtensionFilter("所有文件", "*.*")
        );
        
        File selectedFile = fileChooser.showOpenDialog(null);
        if (selectedFile != null) {
            try {
                loadedImage = ImageIO.read(selectedFile);
                Image fxImage = SwingFXUtils.toFXImage(loadedImage, null);
                imageView.setImage(fxImage);
                imageInfoLabel.setText(selectedFile.getName() + " - " + loadedImage.getWidth() + "x" + loadedImage.getHeight());
            } catch (IOException e) {
                showAlert("加载失败", "无法加载图片: " + e.getMessage());
            }
        }
    }

    @FXML
    private void extractColorsFromImage() {
        if (loadedImage == null) {
            showAlert("提示", "请先打开一张图片");
            return;
        }
        
        int colorCount = extractColorCountCombo.getValue();
        
        List<ColorModel> dominantColors = ImageColorExtractor.extractDominantColors(loadedImage, colorCount);
        updateDominantColorsDisplay(dominantColors);
        
        if (extractByHueCheckBox.isSelected()) {
            Map<String, List<ColorModel>> hueGroups = ImageColorExtractor.extractByHue(loadedImage);
            updateHueGroupsDisplay(hueGroups);
        }
    }

    private void updateDominantColorsDisplay(List<ColorModel> colors) {
        dominantColorsBox.getChildren().clear();
        
        for (ColorModel color : colors) {
            VBox colorBox = new VBox(5);
            colorBox.setAlignment(Pos.CENTER);
            
            Rectangle rect = new Rectangle(60, 60);
            rect.setFill(FXColorConverter.toFXColor(color));
            rect.setStroke(Color.GRAY);
            rect.setArcWidth(5);
            rect.setArcHeight(5);
            
            Label hexLabel = new Label(color.toHEX().toHexString());
            hexLabel.setStyle("-fx-font-family: 'Monaco', monospace; -fx-font-size: 10px;");
            
            Tooltip tooltip = new Tooltip(
                "HEX: " + color.toHEX().toHexString() + "\n" +
                "RGB: " + color.getRed() + ", " + color.getGreen() + ", " + color.getBlue()
            );
            Tooltip.install(rect, tooltip);
            
            rect.setOnMouseClicked(e -> {
                currentColor = color;
                updateUIFromColor();
            });
            
            colorBox.getChildren().addAll(rect, hexLabel);
            dominantColorsBox.getChildren().add(colorBox);
        }
    }

    private void updateHueGroupsDisplay(Map<String, List<ColorModel>> hueGroups) {
        hueGroupContainer.getChildren().clear();
        
        for (Map.Entry<String, List<ColorModel>> entry : hueGroups.entrySet()) {
            String category = entry.getKey();
            List<ColorModel> colors = entry.getValue();
            
            if (colors.isEmpty()) continue;
            
            VBox groupBox = new VBox(5);
            groupBox.setPadding(new Insets(5));
            
            Label categoryLabel = new Label(category);
            categoryLabel.setStyle("-fx-font-weight: bold; -fx-font-size: 12px;");
            
            HBox colorsBox = new HBox(5);
            for (int i = 0; i < Math.min(5, colors.size()); i++) {
                ColorModel color = colors.get(i);
                Rectangle rect = new Rectangle(30, 30);
                rect.setFill(FXColorConverter.toFXColor(color));
                rect.setStroke(Color.LIGHTGRAY);
                rect.setArcWidth(3);
                rect.setArcHeight(3);
                
                Tooltip tooltip = new Tooltip(color.toHEX().toHexString());
                Tooltip.install(rect, tooltip);
                
                final int idx = i;
                rect.setOnMouseClicked(e -> {
                    currentColor = colors.get(idx);
                    updateUIFromColor();
                });
                
                colorsBox.getChildren().add(rect);
            }
            
            groupBox.getChildren().addAll(categoryLabel, colorsBox);
            hueGroupContainer.getChildren().add(groupBox);
        }
    }

    private void updateUIFromColor() {
        isUpdatingFromSliders = true;
        
        redSlider.setValue(currentColor.getRed());
        greenSlider.setValue(currentColor.getGreen());
        blueSlider.setValue(currentColor.getBlue());
        alphaSlider.setValue(currentColor.getAlpha());

        redField.setText(String.valueOf(currentColor.getRed()));
        greenField.setText(String.valueOf(currentColor.getGreen()));
        blueField.setText(String.valueOf(currentColor.getBlue()));
        alphaField.setText(String.format("%.2f", currentColor.getAlpha()));

        HSV hsv = currentColor.toHSV();
        hueSlider.setValue(hsv.getHue());
        saturationSlider.setValue(hsv.getSaturation() * 100);
        valueSlider.setValue(hsv.getValue() * 100);

        hueField.setText(String.format("%.0f", hsv.getHue()));
        saturationField.setText(String.format("%.0f%%", hsv.getSaturation() * 100));
        valueField.setText(String.format("%.0f%%", hsv.getValue() * 100));

        String hexStr = currentColor.toHEX().toHexString();
        hexField.setText(hexStr);
        colorHexLabel.setText(hexStr);
        colorHexValueLabel.setText(hexStr);

        colorRgbValueLabel.setText(String.format("(%d, %d, %d)",
                currentColor.getRed(), currentColor.getGreen(), currentColor.getBlue()));
        
        colorHsvValueLabel.setText(String.format("(%.0f, %.0f%%, %.0f%%)",
                hsv.getHue(), hsv.getSaturation() * 100, hsv.getValue() * 100));

        ColorNameRegistry.ColorNameResult nameResult = ColorNameRegistry.findClosestColor(currentColor);
        if (nameResult != null) {
            if (nameResult.isExactMatch()) {
                colorNameLabel.setText(nameResult.getName());
                colorNameLabel.setStyle("-fx-font-weight: bold; -fx-text-fill: green;");
            } else {
                colorNameLabel.setText("近似: " + nameResult.getName() + 
                    " (距离: " + String.format("%.1f", nameResult.getDistance()) + ")");
                colorNameLabel.setStyle("-fx-font-weight: normal; -fx-text-fill: #666666;");
            }
        } else {
            colorNameLabel.setText("--");
            colorNameLabel.setStyle("");
        }

        colorPreviewRect.setFill(FXColorConverter.toFXColor(currentColor));

        if (colorWheel != null && !isUpdatingFromWheel) {
            colorWheel.setColor(currentColor);
        }

        updateHarmonyColors();
        
        isUpdatingFromSliders = false;
    }

    private void updateColorFromRGB() {
        if (!isUpdatingFromSliders) {
            isUpdatingFromSliders = true;
            currentColor = new ColorModel(
                    (int) redSlider.getValue(),
                    (int) greenSlider.getValue(),
                    (int) blueSlider.getValue(),
                    alphaSlider.getValue()
            );

            HSV hsv = currentColor.toHSV();
            hueSlider.setValue(hsv.getHue());
            saturationSlider.setValue(hsv.getSaturation() * 100);
            valueSlider.setValue(hsv.getValue() * 100);

            hexField.setText(currentColor.toHEX().toHexString());
            colorPreviewRect.setFill(FXColorConverter.toFXColor(currentColor));

            if (colorWheel != null) {
                colorWheel.setColor(currentColor);
            }

            updateHarmonyColors();
            isUpdatingFromSliders = false;
        }
    }

    private void updateColorFromHSV() {
        if (!isUpdatingFromSliders) {
            isUpdatingFromSliders = true;
            currentColor = ColorModel.fromHSV(
                    hueSlider.getValue(),
                    saturationSlider.getValue() / 100.0,
                    valueSlider.getValue() / 100.0,
                    alphaSlider.getValue()
            );

            redSlider.setValue(currentColor.getRed());
            greenSlider.setValue(currentColor.getGreen());
            blueSlider.setValue(currentColor.getBlue());

            hexField.setText(currentColor.toHEX().toHexString());
            colorPreviewRect.setFill(FXColorConverter.toFXColor(currentColor));

            if (colorWheel != null) {
                colorWheel.setColor(currentColor);
            }

            updateHarmonyColors();
            isUpdatingFromSliders = false;
        }
    }

    private void updateHarmonyColors() {
        harmonyColorsBox.getChildren().clear();

        String selected = harmonyCombo.getValue();
        List<ColorModel> colors;

        if (selected.contains("互补")) {
            colors = ColorHarmony.getComplementaryColors(currentColor);
        } else if (selected.contains("类似")) {
            colors = ColorHarmony.getAnalogousColors(currentColor);
        } else if (selected.contains("三角")) {
            colors = ColorHarmony.getTriadicColors(currentColor);
        } else if (selected.contains("四角")) {
            colors = ColorHarmony.getTetradicColors(currentColor);
        } else if (selected.contains("分裂")) {
            colors = ColorHarmony.getSplitComplementaryColors(currentColor);
        } else {
            colors = ColorHarmony.getMonochromaticColors(currentColor);
        }

        for (ColorModel color : colors) {
            Rectangle rect = new Rectangle(50, 50);
            rect.setFill(FXColorConverter.toFXColor(color));
            rect.setStroke(Color.GRAY);
            rect.setArcWidth(5);
            rect.setArcHeight(5);

            Tooltip tooltip = new Tooltip(color.toHEX().toHexString() + 
                "\nRGB: " + color.getRed() + "," + color.getGreen() + "," + color.getBlue());
            Tooltip.install(rect, tooltip);

            rect.setOnMouseClicked(e -> {
                currentColor = color;
                updateUIFromColor();
            });

            harmonyColorsBox.getChildren().add(rect);
        }
    }

    private void updateContrast() {
        ColorModel fg = FXColorConverter.fromFXColor(foregroundPicker.getValue());
        ColorModel bg = FXColorConverter.fromFXColor(backgroundPicker.getValue());

        double ratio = ColorContrast.calculateContrastRatio(fg, bg);
        ColorContrast.WCAGLevel level = ColorContrast.getWCAGLevel(ratio, false);

        contrastRatioLabel.setText(String.format("对比度: %.2f:1", ratio));
        wcagLevelLabel.setText("WCAG等级: " + level.getLabel());

        boolean normalAA = ColorContrast.isAccessible(ratio, false, false);
        boolean normalAAA = ColorContrast.isAccessible(ratio, true, false);
        boolean largeAA = ColorContrast.isAccessible(ratio, false, true);
        boolean largeAAA = ColorContrast.isAccessible(ratio, true, true);

        normalTextAA.setText("AA: " + (normalAA ? "通过 ✓" : "不通过 ✗"));
        normalTextAA.setStyle("-fx-font-weight: bold; -fx-text-fill: " + (normalAA ? "green" : "red"));
        
        normalTextAAA.setText("AAA: " + (normalAAA ? "通过 ✓" : "不通过 ✗"));
        normalTextAAA.setStyle("-fx-font-weight: bold; -fx-text-fill: " + (normalAAA ? "green" : "red"));
        
        largeTextAA.setText("AA: " + (largeAA ? "通过 ✓" : "不通过 ✗"));
        largeTextAA.setStyle("-fx-font-weight: bold; -fx-text-fill: " + (largeAA ? "green" : "red"));
        
        largeTextAAA.setText("AAA: " + (largeAAA ? "通过 ✓" : "不通过 ✗"));
        largeTextAAA.setStyle("-fx-font-weight: bold; -fx-text-fill: " + (largeAAA ? "green" : "red"));

        contrastPreview.setStyle("-fx-background-color: " + toCssColor(backgroundPicker.getValue()) + "; -fx-border-color: gray;");
        contrastTextNormal.setTextFill(foregroundPicker.getValue());
        contrastTextLarge.setTextFill(foregroundPicker.getValue());
    }

    private String toCssColor(Color color) {
        return String.format("rgba(%d, %d, %d, %.2f)",
                (int) (color.getRed() * 255),
                (int) (color.getGreen() * 255),
                (int) (color.getBlue() * 255),
                color.getOpacity());
    }

    private void toggleScreenPicker() {
        if (isPickerRunning) {
            stopScreenPicker();
        } else {
            startScreenPicker();
        }
    }

    private void startScreenPicker() {
        isPickerRunning = true;
        startPickerBtn.setText("停止取色");
        pickerStatusLabel.setText("正在取色... 按空格确认");

        pickerExecutor = Executors.newSingleThreadScheduledExecutor();
        pickerExecutor.scheduleAtFixedRate(() -> {
            try {
                java.awt.Point location = screenPicker.getMousePosition();
                ColorModel color = screenPicker.pickColorAt(location.x, location.y);
                lastPickedColor = color;

                Platform.runLater(() -> {
                    pickerCoordsLabel.setText(String.format("坐标: (%d, %d)", location.x, location.y));
                    pickerPreviewRect.setFill(FXColorConverter.toFXColor(color));
                    pickerHexLabel.setText(color.toHEX().toHexString());
                    pickerRgbLabel.setText(String.format("rgb(%d,%d,%d)",
                            color.getRed(), color.getGreen(), color.getBlue()));
                    
                    magnifier.updateFromScreen(location.x, location.y);
                });
            } catch (Exception e) {
                e.printStackTrace();
            }
        }, 0, 50, TimeUnit.MILLISECONDS);
    }
    
    private void confirmCurrentPick() {
        if (lastPickedColor != null) {
            screenPicker.pickColor(lastPickedColor);
            updateHistoryList(screenPicker.getColorHistory());
            
            currentColor = lastPickedColor;
            updateUIFromColor();
        }
    }

    private void stopScreenPicker() {
        isPickerRunning = false;
        startPickerBtn.setText("开始取色");
        pickerStatusLabel.setText("点击开始取色");

        if (pickerExecutor != null && !pickerExecutor.isShutdown()) {
            pickerExecutor.shutdown();
            try {
                if (!pickerExecutor.awaitTermination(1, TimeUnit.SECONDS)) {
                    pickerExecutor.shutdownNow();
                }
            } catch (InterruptedException e) {
                pickerExecutor.shutdownNow();
                Thread.currentThread().interrupt();
            }
        }

        List<ColorModel> history = screenPicker.getColorHistory();
        updateHistoryList(history);
    }

    @FXML
    private void clearPickerHistory() {
        screenPicker.clearHistory();
        historyListView.getItems().clear();
    }

    private void updateHistoryList(List<ColorModel> colors) {
        historyListView.getItems().clear();
        for (int i = 0; i < colors.size(); i++) {
            ColorModel color = colors.get(i);
            HBox item = createHistoryItem(color, i + 1);
            historyListView.getItems().add(item);
        }
    }

    private HBox createHistoryItem(ColorModel color, int index) {
        HBox item = new HBox(10);
        item.setAlignment(Pos.CENTER_LEFT);
        item.setPadding(new Insets(5));

        Rectangle rect = new Rectangle(40, 30);
        rect.setFill(FXColorConverter.toFXColor(color));
        rect.setStroke(Color.GRAY);
        rect.setArcWidth(3);
        rect.setArcHeight(3);

        Label indexLabel = new Label("#" + index);
        indexLabel.setStyle("-fx-font-weight: bold;");

        VBox infoBox = new VBox(2);
        Label hexLabel = new Label(color.toHEX().toHexString());
        hexLabel.setStyle("-fx-font-family: 'Monaco', monospace;");
        Label rgbLabel = new Label(String.format("RGB: %d,%d,%d",
                color.getRed(), color.getGreen(), color.getBlue()));
        infoBox.getChildren().addAll(hexLabel, rgbLabel);

        Button useBtn = new Button("使用");
        useBtn.setOnAction(e -> {
            currentColor = color;
            updateUIFromColor();
            mainTabPane.getSelectionModel().select(0);
        });

        item.getChildren().addAll(indexLabel, rect, infoBox, useBtn);
        HBox.setHgrow(infoBox, Priority.ALWAYS);

        return item;
    }

    private void updateSearchResults() {
    }

    private void updateGradient() {
        ColorModel start = FXColorConverter.fromFXColor(gradStartPicker.getValue());
        ColorModel end = FXColorConverter.fromFXColor(gradEndPicker.getValue());
        int steps = (int) gradStepsSlider.getValue();

        List<ColorModel> gradient = GradientGenerator.generateLinearGradient(start, end, steps);

        gradientPreviewBox.getChildren().clear();
        for (ColorModel color : gradient) {
            Rectangle rect = new Rectangle(40, 60);
            rect.setFill(FXColorConverter.toFXColor(color));
            gradientPreviewBox.getChildren().add(rect);
        }

        List<ColorModel> cssColors = GradientGenerator.generateLinearGradient(start, end, 5);
        String cssGrad = GradientGenerator.generateCSSLinearGradient(cssColors, "to right");
        cssGradientTextArea.setText(cssGrad);
    }

    private void updateExportText() {
        if (colorManager.getFavorites().isEmpty()) {
            exportTextArea.setText("请先添加颜色到收藏夹");
            return;
        }

        String format = exportFormatCombo.getValue();
        ColorManager.ExportFormat exportFormat;

        switch (format) {
            case "SASS":
                exportFormat = ColorManager.ExportFormat.SASS;
                break;
            case "LESS":
                exportFormat = ColorManager.ExportFormat.LESS;
                break;
            case "JSON":
                exportFormat = ColorManager.ExportFormat.JSON;
                break;
            case "Android":
                exportFormat = ColorManager.ExportFormat.ANDROID;
                break;
            case "iOS":
                exportFormat = ColorManager.ExportFormat.IOS;
                break;
            default:
                exportFormat = ColorManager.ExportFormat.CSS;
        }

        String exported = colorManager.exportColors(colorManager.getFavorites(), exportFormat);
        exportTextArea.setText(exported);
    }

    @FXML
    private void addToFavorites() {
        colorManager.addToFavorites(currentColor);
        updateFavoritesList();
        updateExportText();
        showInfo("已添加到收藏夹: " + currentColor.toHEX().toHexString());
    }

    @FXML
    private void copyHex() {
        copyToClipboard(currentColor.toHEX().toHexString());
        showInfo("HEX颜色已复制: " + currentColor.toHEX().toHexString());
    }

    @FXML
    private void copyRGB() {
        String text = String.format("rgb(%d, %d, %d)",
                currentColor.getRed(), currentColor.getGreen(), currentColor.getBlue());
        copyToClipboard(text);
        showInfo("RGB颜色已复制: " + text);
    }

    @FXML
    private void copyCSS() {
        copyToClipboard(RGBConverter.toCSSString(currentColor));
        showInfo("CSS颜色已复制");
    }

    @FXML
    private void copyAndroid() {
        copyToClipboard("#" + RGBConverter.toAndroidColorString(currentColor));
        showInfo("Android颜色已复制");
    }

    @FXML
    private void copyiOS() {
        copyToClipboard(RGBConverter.toiOSColorString(currentColor));
        showInfo("iOS颜色已复制");
    }

    private void copyToClipboard(String text) {
        Clipboard clipboard = Clipboard.getSystemClipboard();
        ClipboardContent content = new ClipboardContent();
        content.putString(text);
        clipboard.setContent(content);
    }

    private void updateFavoritesList() {
        favoritesListView.getItems().clear();
        List<ColorModel> favorites = colorManager.getFavorites();
        for (int i = 0; i < favorites.size(); i++) {
            ColorModel color = favorites.get(i);
            HBox item = createFavoriteItem(color, i + 1);
            favoritesListView.getItems().add(item);
        }
    }

    private HBox createFavoriteItem(ColorModel color, int index) {
        HBox item = new HBox(10);
        item.setAlignment(Pos.CENTER_LEFT);
        item.setPadding(new Insets(5));

        Rectangle rect = new Rectangle(40, 30);
        rect.setFill(FXColorConverter.toFXColor(color));
        rect.setStroke(Color.GRAY);
        rect.setArcWidth(3);
        rect.setArcHeight(3);

        Label indexLabel = new Label("#" + index);
        indexLabel.setStyle("-fx-font-weight: bold;");

        VBox infoBox = new VBox(2);
        Label hexLabel = new Label(color.toHEX().toHexString());
        hexLabel.setStyle("-fx-font-family: 'Monaco', monospace;");
        
        ColorNameRegistry.ColorNameResult nameResult = ColorNameRegistry.findClosestColor(color);
        Label nameLabel = new Label(nameResult != null ? nameResult.getName() : "");
        nameLabel.setStyle("-fx-font-size: 10px; -fx-text-fill: #666;");
        infoBox.getChildren().addAll(hexLabel, nameLabel);

        Button useBtn = new Button("使用");
        useBtn.setOnAction(e -> {
            currentColor = color;
            updateUIFromColor();
            mainTabPane.getSelectionModel().select(0);
        });

        Button removeBtn = new Button("删除");
        removeBtn.setStyle("-fx-text-fill: red;");
        removeBtn.setOnAction(e -> {
            colorManager.removeFromFavorites(color);
            updateFavoritesList();
            updateExportText();
        });

        item.getChildren().addAll(indexLabel, rect, infoBox, useBtn, removeBtn);
        HBox.setHgrow(infoBox, Priority.ALWAYS);

        return item;
    }

    private void showInfo(String message) {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle("提示");
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.showAndWait();
    }

    private void showAlert(String title, String message) {
        Alert alert = new Alert(Alert.AlertType.WARNING);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.showAndWait();
    }
}
