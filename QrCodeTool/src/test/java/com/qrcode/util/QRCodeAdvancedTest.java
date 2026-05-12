package com.qrcode.util;

import com.qrcode.model.QRCodeStyle;
import org.junit.Test;

import java.awt.image.BufferedImage;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.Assert.*;

public class QRCodeAdvancedTest {

    @Test
    public void testCompareIdenticalQRCodes() throws Exception {
        String content = "相同内容";
        
        QRCodeStyle style = new QRCodeStyle();
        style.setSize(300);
        
        BufferedImage image1 = QRCodeGenerator.generateQRCode(content, style);
        BufferedImage image2 = QRCodeGenerator.generateQRCode(content, style);
        
        Path tempDir = Files.createTempDirectory("qrcode_compare_test_");
        File file1 = new File(tempDir.toFile(), "qr1.png");
        File file2 = new File(tempDir.toFile(), "qr2.png");
        
        QRCodeGenerator.saveQRCode(image1, file1.getAbsolutePath());
        QRCodeGenerator.saveQRCode(image2, file2.getAbsolutePath());
        
        QRCodeAdvanced.CompareResult result = QRCodeAdvanced.compareQRCodes(file1, file2);
        
        assertNotNull("对比结果不应为null", result);
        assertTrue("相同二维码应被识别为相同", result.isIdentical());
        assertEquals("相似度应为100%", 1.0, result.getSimilarity(), 0.001);
        assertEquals("内容1应正确", content, result.getContent1());
        assertEquals("内容2应正确", content, result.getContent2());
        
        file1.delete();
        file2.delete();
        tempDir.toFile().delete();
    }

    @Test
    public void testCompareDifferentQRCodes() throws Exception {
        String content1 = "第一个内容";
        String content2 = "第二个完全不同的内容";
        
        QRCodeStyle style = new QRCodeStyle();
        style.setSize(300);
        
        BufferedImage image1 = QRCodeGenerator.generateQRCode(content1, style);
        BufferedImage image2 = QRCodeGenerator.generateQRCode(content2, style);
        
        Path tempDir = Files.createTempDirectory("qrcode_compare_test_");
        File file1 = new File(tempDir.toFile(), "qr1.png");
        File file2 = new File(tempDir.toFile(), "qr2.png");
        
        QRCodeGenerator.saveQRCode(image1, file1.getAbsolutePath());
        QRCodeGenerator.saveQRCode(image2, file2.getAbsolutePath());
        
        QRCodeAdvanced.CompareResult result = QRCodeAdvanced.compareQRCodes(file1, file2);
        
        assertNotNull("对比结果不应为null", result);
        assertFalse("不同二维码应被识别为不同", result.isIdentical());
        assertTrue("相似度应小于1", result.getSimilarity() < 1.0);
        
        file1.delete();
        file2.delete();
        tempDir.toFile().delete();
    }

    @Test
    public void testCompareSimilarContent() {
        String content1 = "这是一段测试文字";
        String content2 = "这是一段测试文字，略有不同";
        
        QRCodeAdvanced.CompareResult result = QRCodeAdvanced.compareQRCodesByContent(content1, content2);
        
        assertNotNull("对比结果不应为null", result);
        assertFalse("不完全相同的内容应返回false", result.isIdentical());
        assertTrue("相似内容应有较高相似度", result.getSimilarity() > 0.5);
    }

    @Test
    public void testCompareIdenticalContent() {
        String content = "完全相同的内容";
        
        QRCodeAdvanced.CompareResult result = QRCodeAdvanced.compareQRCodesByContent(content, content);
        
        assertNotNull("对比结果不应为null", result);
        assertTrue("相同内容应返回true", result.isIdentical());
        assertEquals("相似度应为100%", 1.0, result.getSimilarity(), 0.001);
    }

    @Test
    public void testCompareEmptyContent() {
        String emptyContent = "";
        
        QRCodeAdvanced.CompareResult result = QRCodeAdvanced.compareQRCodesByContent(emptyContent, emptyContent);
        
        assertNotNull("对比结果不应为null", result);
        assertTrue("空内容应被视为相同", result.isIdentical());
        assertEquals("相似度应为100%", 1.0, result.getSimilarity(), 0.001);
    }

    @Test
    public void testCompareNullContent() {
        QRCodeAdvanced.CompareResult result = QRCodeAdvanced.compareQRCodesByContent(null, null);
        
        assertNotNull("对比结果不应为null", result);
        assertTrue("null内容应被视为相同", result.isIdentical());
    }

    @Test
    public void testRepairQRCode() throws Exception {
        String originalContent = "修复测试内容";
        
        QRCodeStyle style = new QRCodeStyle();
        style.setSize(300);
        style.setErrorLevel(QRCodeStyle.ErrorCorrectionLevel.H);
        
        BufferedImage originalImage = QRCodeGenerator.generateQRCode(originalContent, style);
        
        Path tempDir = Files.createTempDirectory("qrcode_repair_test_");
        File tempFile = new File(tempDir.toFile(), "repair_test.png");
        
        QRCodeGenerator.saveQRCode(originalImage, tempFile.getAbsolutePath());
        
        BufferedImage repairedImage = QRCodeAdvanced.repairQRCode(tempFile);
        
        assertNotNull("修复后的图片不应为null", repairedImage);
        
        String decodedContent = QRCodeReader.decodeQRCode(repairedImage);
        assertEquals("修复后的二维码应能正确解码", originalContent, decodedContent);
        
        tempFile.delete();
        tempDir.toFile().delete();
    }

    @Test
    public void testCanRepair() throws Exception {
        String content = "可修复测试";
        
        QRCodeStyle style = new QRCodeStyle();
        style.setSize(300);
        
        BufferedImage image = QRCodeGenerator.generateQRCode(content, style);
        
        Path tempDir = Files.createTempDirectory("qrcode_repair_test_");
        File validFile = new File(tempDir.toFile(), "valid.png");
        
        QRCodeGenerator.saveQRCode(image, validFile.getAbsolutePath());
        
        assertTrue("有效二维码应能被修复", QRCodeAdvanced.canRepair(validFile));
        
        validFile.delete();
        tempDir.toFile().delete();
    }

    @Test
    public void testCompareChineseContent() {
        String content1 = "我爱北京天安门";
        String content2 = "我爱北京天安门，天安门上太阳升";
        
        QRCodeAdvanced.CompareResult result = QRCodeAdvanced.compareQRCodesByContent(content1, content2);
        
        assertNotNull("对比结果不应为null", result);
        assertFalse("不完全相同的中文内容应返回false", result.isIdentical());
        assertTrue("相似中文内容应有正相似度", result.getSimilarity() > 0.0);
    }

    @Test
    public void testCompareWithSpecialCharacters() {
        String content1 = "特殊字符: !@#$%^&*()";
        String content2 = "特殊字符: !@#$%^&*()-=+";
        
        QRCodeAdvanced.CompareResult result = QRCodeAdvanced.compareQRCodesByContent(content1, content2);
        
        assertNotNull("对比结果不应为null", result);
        assertFalse("不完全相同应返回false", result.isIdentical());
    }
}
