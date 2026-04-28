package com.qrcode.util;

import com.qrcode.model.QRCodeStyle;
import org.junit.Test;

import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.Assert.*;

public class QRCodeGeneratorTest {

    @Test
    public void testGenerateQRCode() throws Exception {
        String testContent = "Hello, QR Code Test!";
        QRCodeStyle style = new QRCodeStyle();
        style.setSize(300);
        
        BufferedImage image = QRCodeGenerator.generateQRCode(testContent, style);
        
        assertNotNull("生成的二维码图片不应为null", image);
        assertEquals("图片宽度应为300", 300, image.getWidth());
        assertEquals("图片高度应为300", 300, image.getHeight());
    }

    @Test
    public void testGenerateQRCodeWithDifferentSizes() throws Exception {
        String testContent = "Test content";
        int[] sizes = {100, 200, 300, 500};
        
        for (int size : sizes) {
            QRCodeStyle style = new QRCodeStyle();
            style.setSize(size);
            
            BufferedImage image = QRCodeGenerator.generateQRCode(testContent, style);
            
            assertNotNull("生成的图片不应为null", image);
            assertEquals("图片宽度应为 " + size, size, image.getWidth());
            assertEquals("图片高度应为 " + size, size, image.getHeight());
        }
    }

    @Test
    public void testGenerateQRCodeWithColors() throws Exception {
        String testContent = "Color test";
        QRCodeStyle style = new QRCodeStyle();
        style.setSize(200);
        style.setForegroundColor(Color.RED);
        style.setBackgroundColor(Color.LIGHT_GRAY);
        
        BufferedImage image = QRCodeGenerator.generateQRCode(testContent, style);
        
        assertNotNull("生成的图片不应为null", image);
    }

    @Test
    public void testGenerateQRCodeWithBorder() throws Exception {
        String testContent = "Border test";
        QRCodeStyle style = new QRCodeStyle();
        style.setSize(200);
        style.setBorderWidth(10);
        style.setBorderColor(Color.BLUE);
        style.setForegroundColor(Color.BLACK);
        style.setBackgroundColor(Color.WHITE);
        
        BufferedImage image = QRCodeGenerator.generateQRCode(testContent, style);
        
        assertNotNull("生成的图片不应为null", image);
        assertEquals("带边框的图片宽度应为220", 220, image.getWidth());
        assertEquals("带边框的图片高度应为220", 220, image.getHeight());
    }

    @Test
    public void testGenerateQRCodeWithDifferentFormats() throws Exception {
        String testContent = "Format test";
        
        QRCodeStyle.QRCodeFormat[] formats = {
            QRCodeStyle.QRCodeFormat.QR_CODE,
            QRCodeStyle.QRCodeFormat.DATA_MATRIX
        };
        
        for (QRCodeStyle.QRCodeFormat format : formats) {
            QRCodeStyle style = new QRCodeStyle();
            style.setSize(200);
            style.setFormat(format);
            
            BufferedImage image = QRCodeGenerator.generateQRCode(testContent, style);
            
            assertNotNull("格式 " + format + " 生成的图片不应为null", image);
        }
    }

    @Test
    public void testSaveQRCode() throws Exception {
        String testContent = "Save test";
        QRCodeStyle style = new QRCodeStyle();
        style.setSize(200);
        
        BufferedImage image = QRCodeGenerator.generateQRCode(testContent, style);
        
        Path tempDir = Files.createTempDirectory("qrcode_test_");
        File tempFile = new File(tempDir.toFile(), "test_qrcode.png");
        
        QRCodeGenerator.saveQRCode(image, tempFile.getAbsolutePath());
        
        assertTrue("保存的文件应存在", tempFile.exists());
        assertTrue("文件大小应大于0", tempFile.length() > 0);
        
        tempFile.delete();
        tempDir.toFile().delete();
    }

    @Test(expected = Exception.class)
    public void testGenerateQRCodeWithEmptyContent() throws Exception {
        QRCodeStyle style = new QRCodeStyle();
        style.setSize(200);
        QRCodeGenerator.generateQRCode("", style);
    }

    @Test
    public void testGenerateQRCodeWithLongContent() throws Exception {
        StringBuilder longContent = new StringBuilder();
        for (int i = 0; i < 20; i++) {
            longContent.append("这是一段较长的测试内容。");
        }
        
        QRCodeStyle style = new QRCodeStyle();
        style.setSize(500);
        style.setErrorLevel(QRCodeStyle.ErrorCorrectionLevel.H);
        
        BufferedImage image = QRCodeGenerator.generateQRCode(longContent.toString(), style);
        
        assertNotNull("长内容生成的图片不应为null", image);
    }

    @Test
    public void testGenerateQRCodeWithSpecialCharacters() throws Exception {
        String specialContent = "测试特殊字符: !@#$%^&*()_+{}[]|\\:;\"'<>,.?/~`\n换行\n制表符\t中文";
        
        QRCodeStyle style = new QRCodeStyle();
        style.setSize(300);
        
        BufferedImage image = QRCodeGenerator.generateQRCode(specialContent, style);
        
        assertNotNull("含特殊字符的二维码不应为null", image);
    }

    @Test
    public void testGenerateURLQRCode() throws Exception {
        String url = "https://www.example.com/path?param=value&other=test";
        
        QRCodeStyle style = new QRCodeStyle();
        style.setSize(200);
        
        BufferedImage image = QRCodeGenerator.generateQRCode(url, style);
        
        assertNotNull("URL二维码不应为null", image);
    }
}
