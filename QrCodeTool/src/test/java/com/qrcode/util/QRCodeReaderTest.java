package com.qrcode.util;

import com.qrcode.model.QRCodeStyle;
import org.junit.Test;

import java.awt.image.BufferedImage;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.Assert.*;

public class QRCodeReaderTest {

    @Test
    public void testDecodeQRCode() throws Exception {
        String originalContent = "Test content for decode";
        
        QRCodeStyle style = new QRCodeStyle();
        style.setSize(300);
        
        BufferedImage generatedImage = QRCodeGenerator.generateQRCode(originalContent, style);
        
        String decodedContent = QRCodeReader.decodeQRCode(generatedImage);
        
        assertEquals("解码内容应与原始内容一致", originalContent, decodedContent);
    }

    @Test
    public void testDecodeQRCodeFromFile() throws Exception {
        String originalContent = "File decode test";
        
        QRCodeStyle style = new QRCodeStyle();
        style.setSize(300);
        
        BufferedImage generatedImage = QRCodeGenerator.generateQRCode(originalContent, style);
        
        Path tempDir = Files.createTempDirectory("qrcode_test_");
        File tempFile = new File(tempDir.toFile(), "test_decode.png");
        
        QRCodeGenerator.saveQRCode(generatedImage, tempFile.getAbsolutePath());
        
        String decodedContent = QRCodeReader.decodeQRCode(tempFile);
        
        assertEquals("从文件解码的内容应与原始内容一致", originalContent, decodedContent);
        
        tempFile.delete();
        tempDir.toFile().delete();
    }

    @Test
    public void testIsQRCodeValid() throws Exception {
        String content = "Valid QR test";
        
        QRCodeStyle style = new QRCodeStyle();
        style.setSize(300);
        
        BufferedImage validImage = QRCodeGenerator.generateQRCode(content, style);
        
        Path tempDir = Files.createTempDirectory("qrcode_test_");
        File validFile = new File(tempDir.toFile(), "valid.png");
        File invalidFile = new File(tempDir.toFile(), "invalid.png");
        
        QRCodeGenerator.saveQRCode(validImage, validFile.getAbsolutePath());
        
        BufferedImage invalidImage = new BufferedImage(100, 100, BufferedImage.TYPE_INT_RGB);
        java.awt.Graphics2D g = invalidImage.createGraphics();
        g.setColor(java.awt.Color.WHITE);
        g.fillRect(0, 0, 100, 100);
        g.dispose();
        javax.imageio.ImageIO.write(invalidImage, "PNG", invalidFile);
        
        assertTrue("有效二维码应返回true", QRCodeReader.isQRCodeValid(validFile));
        assertFalse("无效图片应返回false", QRCodeReader.isQRCodeValid(invalidFile));
        
        validFile.delete();
        invalidFile.delete();
        tempDir.toFile().delete();
    }

    @Test
    public void testDecodeWithInfo() throws Exception {
        String originalContent = "Decode with info test";
        
        QRCodeStyle style = new QRCodeStyle();
        style.setSize(300);
        
        BufferedImage generatedImage = QRCodeGenerator.generateQRCode(originalContent, style);
        
        QRCodeReader.DecodeResult result = QRCodeReader.decodeQRCodeWithInfo(generatedImage);
        
        assertNotNull("解码结果不应为null", result);
        assertEquals("解码内容应正确", originalContent, result.getContent());
        assertNotNull("格式信息不应为null", result.getFormat());
        assertTrue("时间戳应大于0", result.getTimestamp() > 0);
    }

    @Test
    public void testDecodeChineseContent() throws Exception {
        String originalContent = "这是一段中文测试内容，包含特殊字符：！@#￥%……&*（）";
        
        QRCodeStyle style = new QRCodeStyle();
        style.setSize(300);
        
        BufferedImage generatedImage = QRCodeGenerator.generateQRCode(originalContent, style);
        
        String decodedContent = QRCodeReader.decodeQRCode(generatedImage);
        
        assertEquals("中文内容解码应正确", originalContent, decodedContent);
    }

    @Test
    public void testDecodeURLContent() throws Exception {
        String originalContent = "https://www.example.com/path/to/resource?param1=value1&param2=value2#section";
        
        QRCodeStyle style = new QRCodeStyle();
        style.setSize(300);
        
        BufferedImage generatedImage = QRCodeGenerator.generateQRCode(originalContent, style);
        
        String decodedContent = QRCodeReader.decodeQRCode(generatedImage);
        
        assertEquals("URL内容解码应正确", originalContent, decodedContent);
    }

    @Test
    public void testDecodeWithDifferentErrorLevels() throws Exception {
        String originalContent = "Error level test";
        
        QRCodeStyle.ErrorCorrectionLevel[] levels = {
            QRCodeStyle.ErrorCorrectionLevel.L,
            QRCodeStyle.ErrorCorrectionLevel.M,
            QRCodeStyle.ErrorCorrectionLevel.Q,
            QRCodeStyle.ErrorCorrectionLevel.H
        };
        
        for (QRCodeStyle.ErrorCorrectionLevel level : levels) {
            QRCodeStyle style = new QRCodeStyle();
            style.setSize(300);
            style.setErrorLevel(level);
            
            BufferedImage generatedImage = QRCodeGenerator.generateQRCode(originalContent, style);
            
            String decodedContent = QRCodeReader.decodeQRCode(generatedImage);
            
            assertEquals("纠错级别 " + level + " 解码应正确", originalContent, decodedContent);
        }
    }
}
