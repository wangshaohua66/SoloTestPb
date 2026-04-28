package com.qrcode.controller;

import com.google.zxing.NotFoundException;
import com.qrcode.manager.QRCodeManager;
import com.qrcode.model.QRCodeRecord;
import com.qrcode.model.QRCodeStyle;
import com.qrcode.util.*;
import javafx.application.Platform;
import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.embed.swing.SwingFXUtils;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.*;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.*;
import javafx.stage.FileChooser;
import javafx.stage.DirectoryChooser;

import javax.imageio.ImageIO;
import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.image.BufferedImage;
import java.io.*;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Optional;
import java.util.ResourceBundle;

public class MainController implements Initializable {

    @FXML
    private StackPane contentPane;
    
    @FXML
    private VBox generatePane, recognizePane, batchPane, managePane, advancedPane;
    
    @FXML
    private ToggleButton btnGenerate, btnRecognize, btnBatch, btnManage, btnAdvanced;
    
    @FXML
    private ComboBox<String> contentTypeCombo, formatCombo, errorLevelCombo, 
                             wifiEncryptionCombo, batchErrorLevelCombo;
    
    @FXML
    private VBox textContentPane, urlContentPane, businessCardPane, 
                 wifiContentPane, emailContentPane, smsContentPane,
                 decryptImagePane, decryptContentPane;
    
    @FXML
    private TextArea textContentArea, emailBodyArea, smsContentArea,
                    resultArea, encryptContentArea, decryptContentArea, decryptResultArea;
    
    @FXML
    private TextField urlField, wifiSSIDField, emailToField, emailSubjectField,
                     smsPhoneField, dataFilePathField, outputDirField,
                     imageDirField, resultOutputField, searchField,
                     logoPathField, decryptImagePathField, repairImagePathField,
                     comparePath1Field, comparePath2Field;
    
    @FXML
    private PasswordField wifiPasswordField, encryptPasswordField,
                         encryptConfirmPasswordField, decryptPasswordField;
    
    @FXML
    private TextField bcNameField, bcCompanyField, bcTitleField, bcPhoneField,
                     bcMobileField, bcEmailField, bcWebsiteField, bcAddressField;
    
    @FXML
    private CheckBox wifiHiddenCheck, enableLogoCheck, enableBorderCheck,
                    rbCSV, rbExcel, rbExportCSV, rbExportExcel,
                    rbEncryptContent, rbEncryptExisting,
                    rbDecryptImage, rbDecryptContent;
    
    @FXML
    private Slider sizeSlider, marginSlider, batchSizeSlider;
    
    @FXML
    private Label sizeLabel, statusLabel, batchGenerateStatus, batchRecognizeStatus,
                 totalCountLabel, favoriteCountLabel, categoryCountLabel,
                 compareIdenticalLabel, compareSimilarityLabel,
                 compareContent1Label, compareContent2Label;
    
    @FXML
    private ColorPicker foregroundColorPicker, backgroundColorPicker, borderColorPicker;
    
    @FXML
    private Spinner<Integer> borderWidthSpinner;
    
    @FXML
    private Button btnGenerateQR, btnSaveQR, btnPreview, btnCopyResult, btnSaveResult,
                   btnStartBatchGenerate, btnStartBatchRecognize, btnEncryptGenerate,
                   btnDecrypt, btnRepair, btnSaveRepaired, btnCompare;
    
    @FXML
    private ImageView qrImageView, encryptedQRPreview,
                    originalRepairImageView, repairedImageView,
                    compareImageView1, compareImageView2;
    
    @FXML
    private TableView<?> historyTable, batchResultTable, qrCodeTable;
    
    @FXML
    private ListView<String> categoryList;
    
    @FXML
    private ProgressBar progressBar;
    
    private QRCodeManager qrCodeManager;
    private BufferedImage currentGeneratedImage;
    private String currentContent;
    private File selectedImageFile;
    private File selectedDecryptImage;
    private File selectedRepairImage;
    private File selectedCompareImage1, selectedCompareImage2;
    private BufferedImage repairedImage;
    
    private FileChooser fileChooser;
    private DirectoryChooser directoryChooser;

    @Override
    public void initialize(URL location, ResourceBundle resources) {
        qrCodeManager = QRCodeManager.getInstance();
        
        fileChooser = new FileChooser();
        directoryChooser = new DirectoryChooser();
        
        setupFileFilters();
        setupEventListeners();
        updateStatistics();
        
        showPane(generatePane);
    }

    private void setupFileFilters() {
        fileChooser.getExtensionFilters().addAll(
            new FileChooser.ExtensionFilter("图片文件", "*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif"),
            new FileChooser.ExtensionFilter("PNG文件", "*.png"),
            new FileChooser.ExtensionFilter("JPG文件", "*.jpg", "*.jpeg"),
            new FileChooser.ExtensionFilter("CSV文件", "*.csv"),
            new FileChooser.ExtensionFilter("Excel文件", "*.xlsx", "*.xls")
        );
    }

    private void setupEventListeners() {
        contentTypeCombo.getSelectionModel().selectedItemProperty().addListener((obs, oldVal, newVal) -> {
            hideAllContentPanes();
            switch (newVal) {
                case "文本":
                    textContentPane.setVisible(true);
                    break;
                case "网址":
                    urlContentPane.setVisible(true);
                    break;
                case "名片":
                    businessCardPane.setVisible(true);
                    break;
                case "WiFi":
                    wifiContentPane.setVisible(true);
                    break;
                case "邮件":
                    emailContentPane.setVisible(true);
                    break;
                case "短信":
                    smsContentPane.setVisible(true);
                    break;
            }
        });
        
        sizeSlider.valueProperty().addListener((obs, oldVal, newVal) -> {
            int size = newVal.intValue();
            sizeLabel.setText(size + " x " + size);
        });
        
        rbDecryptImage.selectedProperty().addListener((obs, oldVal, newVal) -> {
            decryptImagePane.setVisible(newVal);
            decryptContentPane.setVisible(!newVal);
        });
        
        rbDecryptContent.selectedProperty().addListener((obs, oldVal, newVal) -> {
            decryptContentPane.setVisible(newVal);
            decryptImagePane.setVisible(!newVal);
        });
        
        formatCombo.getSelectionModel().selectFirst();
        errorLevelCombo.getSelectionModel().select(1);
        wifiEncryptionCombo.getSelectionModel().selectFirst();
        contentTypeCombo.getSelectionModel().selectFirst();
        batchErrorLevelCombo.getSelectionModel().select(1);
    }

    private void hideAllContentPanes() {
        textContentPane.setVisible(false);
        urlContentPane.setVisible(false);
        businessCardPane.setVisible(false);
        wifiContentPane.setVisible(false);
        emailContentPane.setVisible(false);
        smsContentPane.setVisible(false);
    }

    private void showPane(VBox pane) {
        generatePane.setVisible(false);
        recognizePane.setVisible(false);
        batchPane.setVisible(false);
        managePane.setVisible(false);
        advancedPane.setVisible(false);
        
        pane.setVisible(true);
    }

    @FXML
    private void handleFunctionSelect() {
        if (btnGenerate.isSelected()) {
            showPane(generatePane);
        } else if (btnRecognize.isSelected()) {
            showPane(recognizePane);
        } else if (btnBatch.isSelected()) {
            showPane(batchPane);
        } else if (btnManage.isSelected()) {
            showPane(managePane);
            loadQRCodeRecords();
        } else if (btnAdvanced.isSelected()) {
            showPane(advancedPane);
        }
    }

    @FXML
    private void handleGenerateQRCode() {
        try {
            String content = getCurrentContent();
            if (content == null || content.isEmpty()) {
                showAlert(Alert.AlertType.WARNING, "提示", "请输入要生成的内容");
                return;
            }
            
            currentContent = content;
            
            QRCodeStyle style = createStyleFromUI();
            
            currentGeneratedImage = QRCodeGenerator.generateQRCode(content, style);
            
            Image fxImage = SwingFXUtils.toFXImage(currentGeneratedImage, null);
            showPreviewDialog(fxImage);
            
            btnSaveQR.setDisable(false);
            btnPreview.setDisable(false);
            
            updateStatus("二维码生成成功");
            
        } catch (Exception e) {
            showAlert(Alert.AlertType.ERROR, "错误", "生成二维码失败: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private String getCurrentContent() {
        String type = contentTypeCombo.getValue();
        if (type == null) return textContentArea.getText();
        
        switch (type) {
            case "文本":
                return textContentArea.getText();
            case "网址":
                return urlField.getText();
            case "名片":
                return QRCodeContentGenerator.generateBusinessCardContent(
                    bcNameField.getText(),
                    bcCompanyField.getText(),
                    bcTitleField.getText(),
                    bcPhoneField.getText(),
                    bcMobileField.getText(),
                    bcEmailField.getText(),
                    bcWebsiteField.getText(),
                    bcAddressField.getText()
                );
            case "WiFi":
                String encryption = wifiEncryptionCombo.getValue();
                if ("无".equals(encryption)) {
                    encryption = "nopass";
                }
                return QRCodeContentGenerator.generateWiFiContent(
                    wifiSSIDField.getText(),
                    wifiPasswordField.getText(),
                    encryption,
                    wifiHiddenCheck.isSelected()
                );
            case "邮件":
                return QRCodeContentGenerator.generateEmailContent(
                    emailToField.getText(),
                    emailSubjectField.getText(),
                    emailBodyArea.getText()
                );
            case "短信":
                return QRCodeContentGenerator.generateSMSContent(
                    smsPhoneField.getText(),
                    smsContentArea.getText()
                );
            default:
                return textContentArea.getText();
        }
    }

    private Color convertColor(javafx.scene.paint.Color fxColor) {
        if (fxColor == null) {
            return Color.BLACK;
        }
        return new Color(
            (int) (fxColor.getRed() * 255),
            (int) (fxColor.getGreen() * 255),
            (int) (fxColor.getBlue() * 255)
        );
    }

    private QRCodeStyle createStyleFromUI() {
        QRCodeStyle style = new QRCodeStyle();
        
        style.setSize((int) sizeSlider.getValue());
        style.setMargin((int) marginSlider.getValue());
        style.setForegroundColor(convertColor(foregroundColorPicker.getValue()));
        style.setBackgroundColor(convertColor(backgroundColorPicker.getValue()));
        
        String errorLevel = errorLevelCombo.getValue();
        if (errorLevel != null) {
            if (errorLevel.startsWith("低")) {
                style.setErrorLevel(QRCodeStyle.ErrorCorrectionLevel.L);
            } else if (errorLevel.startsWith("中")) {
                style.setErrorLevel(QRCodeStyle.ErrorCorrectionLevel.M);
            } else if (errorLevel.startsWith("较高")) {
                style.setErrorLevel(QRCodeStyle.ErrorCorrectionLevel.Q);
            } else {
                style.setErrorLevel(QRCodeStyle.ErrorCorrectionLevel.H);
            }
        }
        
        String format = formatCombo.getValue();
        if (format != null) {
            switch (format) {
                case "QR Code":
                    style.setFormat(QRCodeStyle.QRCodeFormat.QR_CODE);
                    break;
                case "Data Matrix":
                    style.setFormat(QRCodeStyle.QRCodeFormat.DATA_MATRIX);
                    break;
                case "PDF 417":
                    style.setFormat(QRCodeStyle.QRCodeFormat.PDF_417);
                    break;
                case "Aztec":
                    style.setFormat(QRCodeStyle.QRCodeFormat.AZTEC);
                    break;
            }
        }
        
        if (enableLogoCheck.isSelected() && logoPathField.getText() != null && !logoPathField.getText().isEmpty()) {
            style.setLogoPath(logoPathField.getText());
            style.setErrorLevel(QRCodeStyle.ErrorCorrectionLevel.H);
        }
        
        if (enableBorderCheck.isSelected()) {
            style.setBorderWidth(borderWidthSpinner.getValue());
            style.setBorderColor(convertColor(borderColorPicker.getValue()));
        }
        
        return style;
    }

    @FXML
    private void handleSelectLogo() {
        fileChooser.setTitle("选择Logo图片");
        fileChooser.setSelectedExtensionFilter(new FileChooser.ExtensionFilter("图片文件", "*.png", "*.jpg", "*.jpeg"));
        File file = fileChooser.showOpenDialog(null);
        if (file != null) {
            logoPathField.setText(file.getAbsolutePath());
        }
    }

    @FXML
    private void handleSaveQRCode() {
        if (currentGeneratedImage == null) {
            showAlert(Alert.AlertType.WARNING, "提示", "请先生成二维码");
            return;
        }
        
        fileChooser.setTitle("保存二维码");
        fileChooser.setSelectedExtensionFilter(new FileChooser.ExtensionFilter("PNG文件", "*.png"));
        File file = fileChooser.showSaveDialog(null);
        
        if (file != null) {
            try {
                QRCodeGenerator.saveQRCode(currentGeneratedImage, file.getAbsolutePath());
                
                QRCodeRecord.QRCodeType type = QRCodeRecord.QRCodeType.TEXT;
                String contentType = contentTypeCombo.getValue();
                if ("网址".equals(contentType)) type = QRCodeRecord.QRCodeType.URL;
                else if ("名片".equals(contentType)) type = QRCodeRecord.QRCodeType.BUSINESS_CARD;
                else if ("WiFi".equals(contentType)) type = QRCodeRecord.QRCodeType.WIFI;
                else if ("邮件".equals(contentType)) type = QRCodeRecord.QRCodeType.EMAIL;
                else if ("短信".equals(contentType)) type = QRCodeRecord.QRCodeType.SMS;
                
                qrCodeManager.addRecord(currentContent, type, file.getAbsolutePath());
                
                showAlert(Alert.AlertType.INFORMATION, "成功", "二维码已保存到: " + file.getAbsolutePath());
                updateStatus("二维码已保存");
                
            } catch (Exception e) {
                showAlert(Alert.AlertType.ERROR, "错误", "保存失败: " + e.getMessage());
            }
        }
    }

    @FXML
    private void handlePreview() {
        if (currentGeneratedImage == null) {
            showAlert(Alert.AlertType.WARNING, "提示", "请先生成二维码");
            return;
        }
        
        Image fxImage = SwingFXUtils.toFXImage(currentGeneratedImage, null);
        showPreviewDialog(fxImage);
    }

    private void showPreviewDialog(Image image) {
        Dialog<Void> dialog = new Dialog<>();
        dialog.setTitle("二维码预览");
        
        ImageView imageView = new ImageView(image);
        imageView.setFitWidth(400);
        imageView.setFitHeight(400);
        imageView.setPreserveRatio(true);
        
        dialog.getDialogPane().setContent(imageView);
        dialog.getDialogPane().getButtonTypes().add(ButtonType.OK);
        
        dialog.showAndWait();
    }

    @FXML
    private void handleSelectImageToRecognize() {
        fileChooser.setTitle("选择二维码图片");
        fileChooser.setSelectedExtensionFilter(new FileChooser.ExtensionFilter("图片文件", "*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif"));
        File file = fileChooser.showOpenDialog(null);
        
        if (file != null) {
            try {
                selectedImageFile = file;
                Image image = new Image(file.toURI().toString());
                qrImageView.setImage(image);
                
                String content = QRCodeReader.decodeQRCode(file);
                resultArea.setText(content);
                
                btnCopyResult.setDisable(false);
                btnSaveResult.setDisable(false);
                
                updateStatus("识别成功");
                
            } catch (NotFoundException e) {
                showAlert(Alert.AlertType.WARNING, "提示", "无法识别二维码，请确保图片清晰");
            } catch (Exception e) {
                showAlert(Alert.AlertType.ERROR, "错误", "识别失败: " + e.getMessage());
            }
        }
    }

    @FXML
    private void handlePasteFromClipboard() {
        try {
            java.awt.Toolkit toolkit = java.awt.Toolkit.getDefaultToolkit();
            java.awt.datatransfer.Clipboard clipboard = toolkit.getSystemClipboard();
            
            if (clipboard.isDataFlavorAvailable(java.awt.datatransfer.DataFlavor.imageFlavor)) {
                java.awt.Image awtImage = (java.awt.Image) clipboard.getData(java.awt.datatransfer.DataFlavor.imageFlavor);
                BufferedImage bufferedImage = toBufferedImage(awtImage);
                
                Image fxImage = SwingFXUtils.toFXImage(bufferedImage, null);
                qrImageView.setImage(fxImage);
                
                String content = QRCodeReader.decodeQRCode(bufferedImage);
                resultArea.setText(content);
                
                btnCopyResult.setDisable(false);
                btnSaveResult.setDisable(false);
                
                updateStatus("从剪贴板识别成功");
                
            } else if (clipboard.isDataFlavorAvailable(java.awt.datatransfer.DataFlavor.stringFlavor)) {
                String content = (String) clipboard.getData(java.awt.datatransfer.DataFlavor.stringFlavor);
                resultArea.setText(content);
                
                btnCopyResult.setDisable(false);
                btnSaveResult.setDisable(false);
                
                updateStatus("已粘贴文本内容");
            } else {
                showAlert(Alert.AlertType.WARNING, "提示", "剪贴板中没有可识别的内容");
            }
            
        } catch (NotFoundException e) {
            showAlert(Alert.AlertType.WARNING, "提示", "剪贴板中的图片无法识别二维码");
        } catch (Exception e) {
            showAlert(Alert.AlertType.ERROR, "错误", "操作失败: " + e.getMessage());
        }
    }

    private BufferedImage toBufferedImage(java.awt.Image image) {
        if (image instanceof BufferedImage) {
            return (BufferedImage) image;
        }
        
        BufferedImage bimage = new BufferedImage(
            image.getWidth(null),
            image.getHeight(null),
            BufferedImage.TYPE_INT_ARGB
        );
        
        Graphics2D bGr = bimage.createGraphics();
        bGr.drawImage(image, 0, 0, null);
        bGr.dispose();
        
        return bimage;
    }

    @FXML
    private void handleClearRecognize() {
        qrImageView.setImage(null);
        resultArea.clear();
        btnCopyResult.setDisable(true);
        btnSaveResult.setDisable(true);
        selectedImageFile = null;
        updateStatus("已清除");
    }

    @FXML
    private void handleCopyResult() {
        String content = resultArea.getText();
        if (content == null || content.isEmpty()) {
            return;
        }
        
        try {
            java.awt.Toolkit toolkit = java.awt.Toolkit.getDefaultToolkit();
            java.awt.datatransfer.Clipboard clipboard = toolkit.getSystemClipboard();
            clipboard.setContents(new java.awt.datatransfer.StringSelection(content), null);
            updateStatus("已复制到剪贴板");
        } catch (Exception e) {
            showAlert(Alert.AlertType.ERROR, "错误", "复制失败: " + e.getMessage());
        }
    }

    @FXML
    private void handleSaveResult() {
        String content = resultArea.getText();
        if (content == null || content.isEmpty()) {
            showAlert(Alert.AlertType.WARNING, "提示", "没有可保存的内容");
            return;
        }
        
        fileChooser.setTitle("保存识别结果");
        fileChooser.setSelectedExtensionFilter(new FileChooser.ExtensionFilter("文本文件", "*.txt"));
        File file = fileChooser.showSaveDialog(null);
        
        if (file != null) {
            try (BufferedWriter writer = new BufferedWriter(
                    new OutputStreamWriter(new FileOutputStream(file), "UTF-8"))) {
                writer.write("\uFEFF");
                writer.write(content);
                updateStatus("结果已保存到: " + file.getAbsolutePath());
            } catch (Exception e) {
                showAlert(Alert.AlertType.ERROR, "错误", "保存失败: " + e.getMessage());
            }
        }
    }

    @FXML
    private void handleSelectDataFile() {
        fileChooser.setTitle("选择数据文件");
        if (rbCSV.isSelected()) {
            fileChooser.setSelectedExtensionFilter(new FileChooser.ExtensionFilter("CSV文件", "*.csv"));
        } else {
            fileChooser.setSelectedExtensionFilter(new FileChooser.ExtensionFilter("Excel文件", "*.xlsx", "*.xls"));
        }
        File file = fileChooser.showOpenDialog(null);
        if (file != null) {
            dataFilePathField.setText(file.getAbsolutePath());
        }
    }

    @FXML
    private void handleSelectOutputDir() {
        directoryChooser.setTitle("选择输出目录");
        File dir = directoryChooser.showDialog(null);
        if (dir != null) {
            outputDirField.setText(dir.getAbsolutePath());
        }
    }

    @FXML
    private void handleStartBatchGenerate() {
        String dataFilePath = dataFilePathField.getText();
        String outputDirPath = outputDirField.getText();
        
        if (dataFilePath == null || dataFilePath.isEmpty()) {
            showAlert(Alert.AlertType.WARNING, "提示", "请选择数据文件");
            return;
        }
        if (outputDirPath == null || outputDirPath.isEmpty()) {
            showAlert(Alert.AlertType.WARNING, "提示", "请选择输出目录");
            return;
        }
        
        try {
            progressBar.setVisible(true);
            batchGenerateStatus.setText("正在处理...");
            
            File dataFile = new File(dataFilePath);
            File outputDir = new File(outputDirPath);
            
            QRCodeStyle style = new QRCodeStyle();
            style.setSize((int) batchSizeSlider.getValue());
            style.setMargin(10);
            
            String errorLevel = batchErrorLevelCombo.getValue();
            if (errorLevel != null) {
                if (errorLevel.equals("低")) {
                    style.setErrorLevel(QRCodeStyle.ErrorCorrectionLevel.L);
                } else if (errorLevel.equals("中")) {
                    style.setErrorLevel(QRCodeStyle.ErrorCorrectionLevel.M);
                } else if (errorLevel.equals("较高")) {
                    style.setErrorLevel(QRCodeStyle.ErrorCorrectionLevel.Q);
                } else {
                    style.setErrorLevel(QRCodeStyle.ErrorCorrectionLevel.H);
                }
            }
            
            if (rbCSV.isSelected()) {
                BatchProcessor.batchGenerateFromCSV(dataFile, outputDir, style);
            } else {
                BatchProcessor.batchGenerateFromExcel(dataFile, outputDir, style);
            }
            
            progressBar.setVisible(false);
            batchGenerateStatus.setText("完成");
            showAlert(Alert.AlertType.INFORMATION, "成功", "批量生成完成，已保存到: " + outputDirPath);
            updateStatus("批量生成完成");
            
        } catch (Exception e) {
            progressBar.setVisible(false);
            batchGenerateStatus.setText("失败");
            showAlert(Alert.AlertType.ERROR, "错误", "批量生成失败: " + e.getMessage());
            e.printStackTrace();
        }
    }

    @FXML
    private void handleSelectImageDir() {
        directoryChooser.setTitle("选择图片目录");
        File dir = directoryChooser.showDialog(null);
        if (dir != null) {
            imageDirField.setText(dir.getAbsolutePath());
        }
    }

    @FXML
    private void handleSelectResultOutput() {
        fileChooser.setTitle("选择输出文件");
        if (rbExportCSV.isSelected()) {
            fileChooser.setSelectedExtensionFilter(new FileChooser.ExtensionFilter("CSV文件", "*.csv"));
        } else {
            fileChooser.setSelectedExtensionFilter(new FileChooser.ExtensionFilter("Excel文件", "*.xlsx"));
        }
        File file = fileChooser.showSaveDialog(null);
        if (file != null) {
            resultOutputField.setText(file.getAbsolutePath());
        }
    }

    @FXML
    private void handleStartBatchRecognize() {
        String imageDirPath = imageDirField.getText();
        String resultOutputPath = resultOutputField.getText();
        
        if (imageDirPath == null || imageDirPath.isEmpty()) {
            showAlert(Alert.AlertType.WARNING, "提示", "请选择图片目录");
            return;
        }
        
        try {
            progressBar.setVisible(true);
            batchRecognizeStatus.setText("正在处理...");
            
            File imageDir = new File(imageDirPath);
            List<BatchProcessor.BatchDecodeResult> results = BatchProcessor.batchDecode(imageDir);
            
            if (resultOutputPath != null && !resultOutputPath.isEmpty()) {
                File outputFile = new File(resultOutputPath);
                if (rbExportCSV.isSelected()) {
                    BatchProcessor.writeBatchResultsToCSV(results, outputFile);
                } else {
                    BatchProcessor.writeBatchResultsToExcel(results, outputFile);
                }
            }
            
            progressBar.setVisible(false);
            batchRecognizeStatus.setText("完成");
            
            int successCount = (int) results.stream().filter(BatchProcessor.BatchDecodeResult::isSuccess).count();
            showAlert(Alert.AlertType.INFORMATION, "完成", 
                "识别完成: 共" + results.size() + "个文件，成功" + successCount + "个");
            updateStatus("批量识别完成");
            
        } catch (Exception e) {
            progressBar.setVisible(false);
            batchRecognizeStatus.setText("失败");
            showAlert(Alert.AlertType.ERROR, "错误", "批量识别失败: " + e.getMessage());
        }
    }

    @FXML
    private void handleLoadHistory() {
        loadQRCodeRecords();
    }

    @FXML
    private void handleRefreshManage() {
        loadQRCodeRecords();
        updateStatistics();
    }

    @FXML
    private void handleSearch() {
        String keyword = searchField.getText();
        if (keyword == null || keyword.isEmpty()) {
            loadQRCodeRecords();
        } else {
            List<QRCodeRecord> records = qrCodeManager.searchRecords(keyword);
        }
    }

    @FXML
    private void handleAddCategory() {
        TextInputDialog dialog = new TextInputDialog();
        dialog.setTitle("添加分类");
        dialog.setHeaderText("请输入分类名称:");
        dialog.setContentText("名称:");
        
        Optional<String> result = dialog.showAndWait();
        result.ifPresent(name -> {
            if (!name.trim().isEmpty()) {
                qrCodeManager.addCategory(name.trim());
                loadCategories();
                updateStatistics();
            }
        });
    }

    @FXML
    private void handleDeleteCategory() {
        String selected = categoryList.getSelectionModel().getSelectedItem();
        if (selected == null || "全部".equals(selected) || "收藏".equals(selected)) {
            showAlert(Alert.AlertType.WARNING, "提示", "请选择要删除的分类（全部和收藏不能删除）");
            return;
        }
        
        Alert alert = new Alert(Alert.AlertType.CONFIRMATION);
        alert.setTitle("确认删除");
        alert.setHeaderText("确定要删除分类 \"" + selected + "\" 吗？");
        alert.setContentText("该操作不会删除二维码记录，只会移除分类关系。");
        
        Optional<ButtonType> result = alert.showAndWait();
        if (result.isPresent() && result.get() == ButtonType.OK) {
            qrCodeManager.deleteCategory(selected);
            loadCategories();
            loadQRCodeRecords();
            updateStatistics();
        }
    }

    @FXML
    private void handleAddToFavorite() {
        String selectedCategory = categoryList.getSelectionModel().getSelectedItem();
        if ("收藏".equals(selectedCategory)) {
            showAlert(Alert.AlertType.INFORMATION, "提示", "当前已在收藏列表");
            return;
        }
        showAlert(Alert.AlertType.INFORMATION, "提示", "请在表格中选择要收藏的二维码记录");
    }

    @FXML
    private void handleAssignCategory() {
        showAlert(Alert.AlertType.INFORMATION, "提示", "请在表格中选择要分配分类的二维码记录");
    }

    @FXML
    private void handleViewQR() {
        showAlert(Alert.AlertType.INFORMATION, "提示", "请在表格中选择要查看的二维码记录");
    }

    @FXML
    private void handleDeleteQR() {
        showAlert(Alert.AlertType.INFORMATION, "提示", "请在表格中选择要删除的二维码记录");
    }

    private void loadQRCodeRecords() {
        List<QRCodeRecord> records = qrCodeManager.getAllRecords();
    }

    private void loadCategories() {
        categoryList.getItems().clear();
        categoryList.getItems().add("全部");
        categoryList.getItems().add("收藏");
        categoryList.getItems().addAll(qrCodeManager.getCategories());
    }

    private void updateStatistics() {
        QRCodeManager.Statistics stats = qrCodeManager.getStatistics();
        totalCountLabel.setText("总数: " + stats.totalCount);
        favoriteCountLabel.setText("收藏: " + stats.favoriteCount);
        categoryCountLabel.setText("分类数: " + stats.categoryCount);
    }

    @FXML
    private void handleEncryptGenerate() {
        String content = encryptContentArea.getText();
        String password = encryptPasswordField.getText();
        String confirmPassword = encryptConfirmPasswordField.getText();
        
        if (content == null || content.isEmpty()) {
            showAlert(Alert.AlertType.WARNING, "提示", "请输入要加密的内容");
            return;
        }
        if (password == null || password.isEmpty()) {
            showAlert(Alert.AlertType.WARNING, "提示", "请输入密码");
            return;
        }
        if (!password.equals(confirmPassword)) {
            showAlert(Alert.AlertType.WARNING, "提示", "两次输入的密码不一致");
            return;
        }
        
        try {
            String encrypted = QRCodeEncryptor.encrypt(content, password);
            
            QRCodeStyle style = new QRCodeStyle();
            style.setSize(300);
            style.setErrorLevel(QRCodeStyle.ErrorCorrectionLevel.H);
            
            BufferedImage image = QRCodeGenerator.generateQRCode(encrypted, style);
            currentGeneratedImage = image;
            
            Image fxImage = SwingFXUtils.toFXImage(image, null);
            encryptedQRPreview.setImage(fxImage);
            
            updateStatus("加密并生成二维码成功");
            showAlert(Alert.AlertType.INFORMATION, "成功", "加密二维码已生成，点击预览可查看");
            
        } catch (Exception e) {
            showAlert(Alert.AlertType.ERROR, "错误", "加密失败: " + e.getMessage());
            e.printStackTrace();
        }
    }

    @FXML
    private void handleSelectDecryptImage() {
        fileChooser.setTitle("选择加密的二维码图片");
        fileChooser.setSelectedExtensionFilter(new FileChooser.ExtensionFilter("图片文件", "*.png", "*.jpg", "*.jpeg"));
        File file = fileChooser.showOpenDialog(null);
        if (file != null) {
            selectedDecryptImage = file;
            decryptImagePathField.setText(file.getAbsolutePath());
        }
    }

    @FXML
    private void handleDecrypt() {
        String password = decryptPasswordField.getText();
        if (password == null || password.isEmpty()) {
            showAlert(Alert.AlertType.WARNING, "提示", "请输入密码");
            return;
        }
        
        try {
            String encryptedContent;
            
            if (rbDecryptImage.isSelected()) {
                if (selectedDecryptImage == null) {
                    showAlert(Alert.AlertType.WARNING, "提示", "请选择要解密的二维码图片");
                    return;
                }
                encryptedContent = QRCodeReader.decodeQRCode(selectedDecryptImage);
            } else {
                encryptedContent = decryptContentArea.getText();
                if (encryptedContent == null || encryptedContent.isEmpty()) {
                    showAlert(Alert.AlertType.WARNING, "提示", "请输入加密内容");
                    return;
                }
            }
            
            if (!QRCodeEncryptor.isEncrypted(encryptedContent)) {
                showAlert(Alert.AlertType.WARNING, "提示", "该内容不是加密的二维码");
                decryptResultArea.setText(encryptedContent);
                return;
            }
            
            String decrypted = QRCodeEncryptor.decrypt(encryptedContent, password);
            decryptResultArea.setText(decrypted);
            
            updateStatus("解密成功");
            
        } catch (Exception e) {
            showAlert(Alert.AlertType.ERROR, "错误", "解密失败: " + e.getMessage());
        }
    }

    @FXML
    private void handleSelectRepairImage() {
        fileChooser.setTitle("选择要修复的二维码图片");
        fileChooser.setSelectedExtensionFilter(new FileChooser.ExtensionFilter("图片文件", "*.png", "*.jpg", "*.jpeg"));
        File file = fileChooser.showOpenDialog(null);
        if (file != null) {
            selectedRepairImage = file;
            repairImagePathField.setText(file.getAbsolutePath());
            
            Image image = new Image(file.toURI().toString());
            originalRepairImageView.setImage(image);
        }
    }

    @FXML
    private void handleRepair() {
        if (selectedRepairImage == null) {
            showAlert(Alert.AlertType.WARNING, "提示", "请选择要修复的二维码图片");
            return;
        }
        
        try {
            repairedImage = QRCodeAdvanced.repairQRCode(selectedRepairImage);
            
            if (repairedImage != null) {
                Image fxImage = SwingFXUtils.toFXImage(repairedImage, null);
                repairedImageView.setImage(fxImage);
                btnSaveRepaired.setDisable(false);
                
                updateStatus("修复成功");
            } else {
                showAlert(Alert.AlertType.WARNING, "提示", "无法修复该二维码");
            }
            
        } catch (Exception e) {
            showAlert(Alert.AlertType.ERROR, "错误", "修复失败: " + e.getMessage());
            e.printStackTrace();
        }
    }

    @FXML
    private void handleSaveRepaired() {
        if (repairedImage == null) {
            showAlert(Alert.AlertType.WARNING, "提示", "没有可保存的修复结果");
            return;
        }
        
        fileChooser.setTitle("保存修复后的二维码");
        fileChooser.setSelectedExtensionFilter(new FileChooser.ExtensionFilter("PNG文件", "*.png"));
        File file = fileChooser.showSaveDialog(null);
        
        if (file != null) {
            try {
                ImageIO.write(repairedImage, "PNG", file);
                updateStatus("修复结果已保存到: " + file.getAbsolutePath());
            } catch (Exception e) {
                showAlert(Alert.AlertType.ERROR, "错误", "保存失败: " + e.getMessage());
            }
        }
    }

    @FXML
    private void handleSelectCompare1() {
        fileChooser.setTitle("选择第一个二维码图片");
        fileChooser.setSelectedExtensionFilter(new FileChooser.ExtensionFilter("图片文件", "*.png", "*.jpg", "*.jpeg"));
        File file = fileChooser.showOpenDialog(null);
        if (file != null) {
            selectedCompareImage1 = file;
            comparePath1Field.setText(file.getAbsolutePath());
            Image image = new Image(file.toURI().toString());
            compareImageView1.setImage(image);
        }
    }

    @FXML
    private void handleSelectCompare2() {
        fileChooser.setTitle("选择第二个二维码图片");
        fileChooser.setSelectedExtensionFilter(new FileChooser.ExtensionFilter("图片文件", "*.png", "*.jpg", "*.jpeg"));
        File file = fileChooser.showOpenDialog(null);
        if (file != null) {
            selectedCompareImage2 = file;
            comparePath2Field.setText(file.getAbsolutePath());
            Image image = new Image(file.toURI().toString());
            compareImageView2.setImage(image);
        }
    }

    @FXML
    private void handleCompare() {
        if (selectedCompareImage1 == null || selectedCompareImage2 == null) {
            showAlert(Alert.AlertType.WARNING, "提示", "请选择两个二维码图片");
            return;
        }
        
        try {
            QRCodeAdvanced.CompareResult result = QRCodeAdvanced.compareQRCodes(
                selectedCompareImage1, selectedCompareImage2
            );
            
            compareIdenticalLabel.setText(result.isIdentical() ? "是" : "否");
            compareIdenticalLabel.setStyle(result.isIdentical() ? "-fx-text-fill: green; -fx-font-weight: bold;" : "-fx-text-fill: red; -fx-font-weight: bold;");
            
            compareSimilarityLabel.setText(String.format("%.2f%%", result.getSimilarity() * 100));
            compareContent1Label.setText(result.getContent1());
            compareContent2Label.setText(result.getContent2());
            
            updateStatus("对比完成");
            
        } catch (Exception e) {
            showAlert(Alert.AlertType.ERROR, "错误", "对比失败: " + e.getMessage());
        }
    }

    @FXML
    private void handleNewQRCode() {
        btnGenerate.setSelected(true);
        showPane(generatePane);
        clearGenerateFields();
    }

    @FXML
    private void handleOpenImage() {
        btnRecognize.setSelected(true);
        showPane(recognizePane);
        handleSelectImageToRecognize();
    }

    @FXML
    private void handleSave() {
        if (generatePane.isVisible()) {
            handleSaveQRCode();
        } else if (recognizePane.isVisible()) {
            handleSaveResult();
        } else if (advancedPane.isVisible()) {
            if (btnAdvanced.isSelected()) {
            }
        }
    }

    @FXML
    private void handleExit() {
        Platform.exit();
    }

    @FXML
    private void handleCopyContent() {
        if (generatePane.isVisible()) {
            String content = getCurrentContent();
            if (content != null && !content.isEmpty()) {
                try {
                    java.awt.Toolkit toolkit = java.awt.Toolkit.getDefaultToolkit();
                    java.awt.datatransfer.Clipboard clipboard = toolkit.getSystemClipboard();
                    clipboard.setContents(new java.awt.datatransfer.StringSelection(content), null);
                    updateStatus("已复制到剪贴板");
                } catch (Exception e) {
                    showAlert(Alert.AlertType.ERROR, "错误", "复制失败: " + e.getMessage());
                }
            }
        }
    }

    @FXML
    private void handlePasteContent() {
        try {
            java.awt.Toolkit toolkit = java.awt.Toolkit.getDefaultToolkit();
            java.awt.datatransfer.Clipboard clipboard = toolkit.getSystemClipboard();
            
            if (clipboard.isDataFlavorAvailable(java.awt.datatransfer.DataFlavor.stringFlavor)) {
                String content = (String) clipboard.getData(java.awt.datatransfer.DataFlavor.stringFlavor);
                if (generatePane.isVisible()) {
                    textContentArea.setText(content);
                }
                updateStatus("已从剪贴板粘贴");
            }
        } catch (Exception e) {
            showAlert(Alert.AlertType.ERROR, "错误", "粘贴失败: " + e.getMessage());
        }
    }

    @FXML
    private void handleBatchGenerate() {
        btnBatch.setSelected(true);
        showPane(batchPane);
    }

    @FXML
    private void handleBatchRecognize() {
        btnBatch.setSelected(true);
        showPane(batchPane);
    }

    @FXML
    private void handleEncrypt() {
        btnAdvanced.setSelected(true);
        showPane(advancedPane);
    }

    @FXML
    private void handleAbout() {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle("关于");
        alert.setHeaderText("二维码工具 v1.0.0");
        alert.setContentText(
            "一个功能强大的本地二维码工具\n\n" +
            "功能包括:\n" +
            "• 二维码生成（文本、网址、名片、WiFi等）\n" +
            "• 二维码识别\n" +
            "• 样式定制（颜色、Logo、边框等）\n" +
            "• 批量处理\n" +
            "• 二维码管理\n" +
            "• 高级功能（加密、修复、对比）\n\n" +
            "技术栈: Java 8, JavaFX, ZXing, Maven"
        );
        alert.showAndWait();
    }

    private void clearGenerateFields() {
        textContentArea.clear();
        urlField.clear();
        bcNameField.clear();
        bcCompanyField.clear();
        bcTitleField.clear();
        bcPhoneField.clear();
        bcMobileField.clear();
        bcEmailField.clear();
        bcWebsiteField.clear();
        bcAddressField.clear();
        wifiSSIDField.clear();
        wifiPasswordField.clear();
        emailToField.clear();
        emailSubjectField.clear();
        emailBodyArea.clear();
        smsPhoneField.clear();
        smsContentArea.clear();
        logoPathField.clear();
        
        currentGeneratedImage = null;
        btnSaveQR.setDisable(true);
        btnPreview.setDisable(true);
    }

    private void updateStatus(String message) {
        statusLabel.setText(message);
    }

    private void showAlert(Alert.AlertType type, String title, String content) {
        Alert alert = new Alert(type);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(content);
        alert.showAndWait();
    }
}
