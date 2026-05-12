package com.qrcode.util;

import com.google.zxing.*;
import com.google.zxing.client.j2se.BufferedImageLuminanceSource;
import com.google.zxing.common.HybridBinarizer;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.EnumMap;
import java.util.Map;

public class QRCodeAdvanced {

    public static class CompareResult {
        private boolean identical;
        private double similarity;
        private String content1;
        private String content2;

        public CompareResult(boolean identical, double similarity, String content1, String content2) {
            this.identical = identical;
            this.similarity = similarity;
            this.content1 = content1;
            this.content2 = content2;
        }

        public boolean isIdentical() {
            return identical;
        }

        public double getSimilarity() {
            return similarity;
        }

        public String getContent1() {
            return content1;
        }

        public String getContent2() {
            return content2;
        }
    }

    public static CompareResult compareQRCodes(File file1, File file2) {
        try {
            String content1 = null;
            String content2 = null;
            boolean success1 = false;
            boolean success2 = false;
            
            try {
                content1 = QRCodeReader.decodeQRCode(file1);
                success1 = true;
            } catch (Exception e) {
                content1 = "无法识别";
            }
            
            try {
                content2 = QRCodeReader.decodeQRCode(file2);
                success2 = true;
            } catch (Exception e) {
                content2 = "无法识别";
            }
            
            boolean identical = success1 && success2 && content1.equals(content2);
            double similarity = calculateContentSimilarity(content1, content2);
            
            return new CompareResult(identical, similarity, content1, content2);
            
        } catch (Exception e) {
            return new CompareResult(false, 0.0, "处理错误: " + e.getMessage(), "处理错误: " + e.getMessage());
        }
    }

    public static CompareResult compareQRCodesByContent(String content1, String content2) {
        if (content1 == null && content2 == null) {
            return new CompareResult(true, 1.0, null, null);
        }
        if (content1 == null || content2 == null) {
            return new CompareResult(false, 0.0, content1, content2);
        }
        boolean identical = content1.equals(content2);
        double similarity = calculateContentSimilarity(content1, content2);
        return new CompareResult(identical, similarity, content1, content2);
    }

    private static double calculateContentSimilarity(String s1, String s2) {
        if (s1 == null || s2 == null) {
            return 0.0;
        }
        if (s1.equals(s2)) {
            return 1.0;
        }
        
        int longerLength = Math.max(s1.length(), s2.length());
        if (longerLength == 0) {
            return 1.0;
        }
        
        int editDistance = levenshteinDistance(s1, s2);
        return (double) (longerLength - editDistance) / longerLength;
    }

    private static int levenshteinDistance(String s1, String s2) {
        int[][] dp = new int[s1.length() + 1][s2.length() + 1];
        
        for (int i = 0; i <= s1.length(); i++) {
            dp[i][0] = i;
        }
        for (int j = 0; j <= s2.length(); j++) {
            dp[0][j] = j;
        }
        
        for (int i = 1; i <= s1.length(); i++) {
            for (int j = 1; j <= s2.length(); j++) {
                int cost = (s1.charAt(i - 1) == s2.charAt(j - 1)) ? 0 : 1;
                dp[i][j] = Math.min(Math.min(dp[i - 1][j] + 1, dp[i][j - 1] + 1), dp[i - 1][j - 1] + cost);
            }
        }
        
        return dp[s1.length()][s2.length()];
    }

    public static BufferedImage repairQRCode(File file) throws IOException, NotFoundException {
        BufferedImage original = ImageIO.read(file);
        if (original == null) {
            throw new IOException("无法读取图片文件");
        }
        
        try {
            LuminanceSource source = new BufferedImageLuminanceSource(original);
            BinaryBitmap bitmap = new BinaryBitmap(new HybridBinarizer(source));
            MultiFormatReader reader = new MultiFormatReader();
            
            Map<DecodeHintType, Object> hints = new EnumMap<>(DecodeHintType.class);
            hints.put(DecodeHintType.TRY_HARDER, Boolean.TRUE);
            java.util.List<com.google.zxing.BarcodeFormat> formats = 
                java.util.Arrays.asList(com.google.zxing.BarcodeFormat.QR_CODE);
            hints.put(DecodeHintType.POSSIBLE_FORMATS, formats);
            
            Result result = reader.decode(bitmap, hints);
            
            int width = original.getWidth();
            int height = original.getHeight();
            
            Map<com.google.zxing.EncodeHintType, Object> encodeHints = new EnumMap<>(com.google.zxing.EncodeHintType.class);
            encodeHints.put(com.google.zxing.EncodeHintType.CHARACTER_SET, "UTF-8");
            encodeHints.put(com.google.zxing.EncodeHintType.ERROR_CORRECTION, com.google.zxing.qrcode.decoder.ErrorCorrectionLevel.H);
            encodeHints.put(com.google.zxing.EncodeHintType.MARGIN, 4);
            
            com.google.zxing.MultiFormatWriter writer = new com.google.zxing.MultiFormatWriter();
            com.google.zxing.common.BitMatrix bitMatrix = writer.encode(
                result.getText(),
                com.google.zxing.BarcodeFormat.QR_CODE,
                width,
                height,
                encodeHints
            );
            
            BufferedImage repaired = new BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
            for (int x = 0; x < width; x++) {
                for (int y = 0; y < height; y++) {
                    repaired.setRGB(x, y, bitMatrix.get(x, y) ? Color.BLACK.getRGB() : Color.WHITE.getRGB());
                }
            }
            
            return repaired;
            
        } catch (NotFoundException e) {
            return applyEnhancementFilters(original);
        } catch (Exception e) {
            throw new IOException("修复过程中出错: " + e.getMessage(), e);
        }
    }

    private static BufferedImage applyEnhancementFilters(BufferedImage image) {
        int width = image.getWidth();
        int height = image.getHeight();
        
        BufferedImage enhanced = new BufferedImage(width, height, BufferedImage.TYPE_BYTE_BINARY);
        Graphics2D g2d = enhanced.createGraphics();
        g2d.drawImage(image, 0, 0, null);
        g2d.dispose();
        
        int threshold = calculateOtsuThreshold(image);
        
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                int rgb = image.getRGB(x, y);
                int gray = (int) (0.299 * ((rgb >> 16) & 0xFF) + 
                                  0.587 * ((rgb >> 8) & 0xFF) + 
                                  0.114 * (rgb & 0xFF));
                
                int newRgb = (gray < threshold) ? Color.BLACK.getRGB() : Color.WHITE.getRGB();
                enhanced.setRGB(x, y, newRgb);
            }
        }
        
        return enhanced;
    }

    private static int calculateOtsuThreshold(BufferedImage image) {
        int[] histogram = new int[256];
        int width = image.getWidth();
        int height = image.getHeight();
        int totalPixels = width * height;
        
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {
                int rgb = image.getRGB(x, y);
                int gray = (int) (0.299 * ((rgb >> 16) & 0xFF) + 
                                  0.587 * ((rgb >> 8) & 0xFF) + 
                                  0.114 * (rgb & 0xFF));
                histogram[gray]++;
            }
        }
        
        double sum = 0;
        for (int i = 0; i < 256; i++) {
            sum += i * histogram[i];
        }
        
        double sumB = 0;
        int wB = 0;
        int wF = 0;
        
        double varMax = 0;
        int threshold = 0;
        
        for (int i = 0; i < 256; i++) {
            wB += histogram[i];
            if (wB == 0) continue;
            
            wF = totalPixels - wB;
            if (wF == 0) break;
            
            sumB += i * histogram[i];
            
            double mB = sumB / wB;
            double mF = (sum - sumB) / wF;
            
            double varBetween = (double) wB * wF * (mB - mF) * (mB - mF);
            
            if (varBetween > varMax) {
                varMax = varBetween;
                threshold = i;
            }
        }
        
        return threshold;
    }

    public static boolean canRepair(File file) {
        try {
            repairQRCode(file);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}
