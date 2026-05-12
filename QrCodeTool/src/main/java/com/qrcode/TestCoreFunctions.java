package com.qrcode;

import com.qrcode.model.QRCodeStyle;
import com.qrcode.util.*;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public class TestCoreFunctions {

    public static void main(String[] args) {
        System.out.println("=== 二维码工具核心功能测试 ===");
        System.out.println();
        
        try {
            Path tempDir = Files.createTempDirectory("qrcode_test_");
            System.out.println("临时目录: " + tempDir);
            System.out.println();
            
            testQRCodeGeneration(tempDir);
            testQRCodeRecognition(tempDir);
            testContentGeneration();
            testEncryption();
            testBatchProcessing(tempDir);
            
            System.out.println();
            System.out.println("=== 所有核心功能测试通过! ===");
            
        } catch (Exception e) {
            System.err.println("测试失败: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }

    private static void testQRCodeGeneration(Path tempDir) throws Exception {
        System.out.println("[测试] 二维码生成...");
        
        QRCodeStyle style = new QRCodeStyle();
        style.setSize(300);
        style.setMargin(10);
        
        String testContent = "Hello, QR Code! 你好，二维码！";
        
        BufferedImage image = QRCodeGenerator.generateQRCode(testContent, style);
        
        if (image == null) {
            throw new RuntimeException("生成的二维码图片为空");
        }
        if (image.getWidth() != 300 || image.getHeight() != 300) {
            throw new RuntimeException("二维码大小不正确: " + image.getWidth() + "x" + image.getHeight());
        }
        
        File outputFile = new File(tempDir.toFile(), "test_generate.png");
        QRCodeGenerator.saveQRCode(image, outputFile.getAbsolutePath());
        
        if (!outputFile.exists() || outputFile.length() == 0) {
            throw new RuntimeException("保存的二维码文件无效");
        }
        
        System.out.println("  ✓ 二维码生成成功: " + outputFile.getAbsolutePath());
        System.out.println("  ✓ 二维码大小: 300x300");
        System.out.println();
    }

    private static void testQRCodeRecognition(Path tempDir) throws Exception {
        System.out.println("[测试] 二维码识别...");
        
        String originalContent = "测试识别功能 - Test Recognition";
        
        QRCodeStyle style = new QRCodeStyle();
        style.setSize(300);
        
        BufferedImage image = QRCodeGenerator.generateQRCode(originalContent, style);
        File testFile = new File(tempDir.toFile(), "test_recognize.png");
        QRCodeGenerator.saveQRCode(image, testFile.getAbsolutePath());
        
        String decoded = QRCodeReader.decodeQRCode(testFile);
        
        if (!originalContent.equals(decoded)) {
            throw new RuntimeException("识别结果不匹配!\n原始: " + originalContent + "\n识别: " + decoded);
        }
        
        boolean isValid = QRCodeReader.isQRCodeValid(testFile);
        if (!isValid) {
            throw new RuntimeException("有效的二维码应该返回true");
        }
        
        QRCodeReader.DecodeResult result = QRCodeReader.decodeQRCodeWithInfo(testFile);
        if (!originalContent.equals(result.getContent())) {
            throw new RuntimeException("带信息的识别结果不匹配");
        }
        if (result.getFormat() == null || result.getFormat().isEmpty()) {
            throw new RuntimeException("格式信息为空");
        }
        
        System.out.println("  ✓ 二维码识别成功");
        System.out.println("  ✓ 原始内容: " + originalContent);
        System.out.println("  ✓ 识别内容: " + decoded);
        System.out.println("  ✓ 格式: " + result.getFormat());
        System.out.println();
    }

    private static void testContentGeneration() {
        System.out.println("[测试] 内容生成器...");
        
        String wifiContent = QRCodeContentGenerator.generateWiFiContent(
            "MyNetwork", "password123", "WPA", false
        );
        
        if (!wifiContent.startsWith("WIFI:")) {
            throw new RuntimeException("WiFi内容格式不正确: " + wifiContent);
        }
        if (!wifiContent.contains("S:MyNetwork")) {
            throw new RuntimeException("WiFi内容缺少SSID");
        }
        System.out.println("  ✓ WiFi内容生成: " + wifiContent);
        
        String vcardContent = QRCodeContentGenerator.generateBusinessCardContent(
            "张三", "科技公司", "工程师",
            "010-12345678", "13800138000",
            "zhangsan@example.com", "https://www.example.com", "北京市"
        );
        
        if (!vcardContent.startsWith("BEGIN:VCARD")) {
            throw new RuntimeException("vCard格式不正确");
        }
        if (!vcardContent.contains("FN:张三")) {
            throw new RuntimeException("vCard缺少姓名");
        }
        System.out.println("  ✓ 名片(vCard)内容生成成功");
        
        String emailContent = QRCodeContentGenerator.generateEmailContent(
            "test@example.com", "测试主题", "测试正文"
        );
        
        if (!emailContent.startsWith("mailto:")) {
            throw new RuntimeException("邮件内容格式不正确: " + emailContent);
        }
        System.out.println("  ✓ 邮件内容生成: " + emailContent);
        
        String smsContent = QRCodeContentGenerator.generateSMSContent(
            "13800138000", "测试短信内容"
        );
        
        if (!smsContent.startsWith("SMSTO:")) {
            throw new RuntimeException("短信内容格式不正确: " + smsContent);
        }
        System.out.println("  ✓ 短信内容生成: " + smsContent);
        
        System.out.println();
    }

    private static void testEncryption() throws Exception {
        System.out.println("[测试] 加密功能...");
        
        String originalContent = "这是敏感信息，需要加密保护";
        String password = "MySecurePassword123";
        String wrongPassword = "WrongPassword";
        
        String encrypted = QRCodeEncryptor.encrypt(originalContent, password);
        
        if (!QRCodeEncryptor.isEncrypted(encrypted)) {
            throw new RuntimeException("加密内容未被正确标记");
        }
        
        if (encrypted.equals(originalContent)) {
            throw new RuntimeException("加密内容不应与原文相同");
        }
        
        System.out.println("  ✓ 原文: " + originalContent);
        System.out.println("  ✓ 加密后: " + encrypted.substring(0, Math.min(50, encrypted.length())) + "...");
        
        String decrypted = QRCodeEncryptor.decrypt(encrypted, password);
        
        if (!originalContent.equals(decrypted)) {
            throw new RuntimeException("解密结果与原文不匹配!\n原文: " + originalContent + "\n解密: " + decrypted);
        }
        System.out.println("  ✓ 使用正确密码解密成功: " + decrypted);
        
        boolean passwordVerified = QRCodeEncryptor.verifyPassword(encrypted, password);
        if (!passwordVerified) {
            throw new RuntimeException("正确密码应该验证通过");
        }
        
        boolean wrongPasswordVerified = QRCodeEncryptor.verifyPassword(encrypted, wrongPassword);
        if (wrongPasswordVerified) {
            throw new RuntimeException("错误密码不应该验证通过");
        }
        
        System.out.println("  ✓ 密码验证功能正常");
        
        System.out.println();
    }

    private static void testBatchProcessing(Path tempDir) throws Exception {
        System.out.println("[测试] 批量处理功能...");
        
        QRCodeStyle style = new QRCodeStyle();
        style.setSize(200);
        
        List<String> contents = java.util.Arrays.asList(
            "批量测试内容1",
            "批量测试内容2 - URL: https://www.example.com",
            "批量测试内容3 - 中文支持"
        );
        
        File outputDir = new File(tempDir.toFile(), "batch_output");
        outputDir.mkdirs();
        
        BatchProcessor.batchGenerate(contents, outputDir, style);
        
        File[] generatedFiles = outputDir.listFiles((dir, name) -> name.endsWith(".png"));
        
        if (generatedFiles == null || generatedFiles.length != 3) {
            throw new RuntimeException("批量生成的文件数量不正确: " + 
                (generatedFiles == null ? 0 : generatedFiles.length));
        }
        
        for (File file : generatedFiles) {
            if (!file.exists() || file.length() == 0) {
                throw new RuntimeException("批量生成的文件无效: " + file.getName());
            }
            System.out.println("  ✓ 生成: " + file.getName());
        }
        
        List<BatchProcessor.BatchDecodeResult> decodeResults = BatchProcessor.batchDecode(outputDir);
        
        if (decodeResults.size() != 3) {
            throw new RuntimeException("批量识别结果数量不正确");
        }
        
        for (BatchProcessor.BatchDecodeResult result : decodeResults) {
            if (!result.isSuccess()) {
                throw new RuntimeException("批量识别失败: " + result.getFileName() + 
                    " - " + result.getErrorMessage());
            }
            System.out.println("  ✓ 识别: " + result.getFileName() + " -> " + result.getContent());
        }
        
        System.out.println();
    }
}
