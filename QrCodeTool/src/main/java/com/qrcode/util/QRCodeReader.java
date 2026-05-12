package com.qrcode.util;

import com.google.zxing.*;
import com.google.zxing.client.j2se.BufferedImageLuminanceSource;
import com.google.zxing.common.HybridBinarizer;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.EnumMap;
import java.util.EnumSet;
import java.util.Map;

public class QRCodeReader {

    private static final Map<DecodeHintType, Object> DEFAULT_HINTS = createDefaultHints();

    private static Map<DecodeHintType, Object> createDefaultHints() {
        Map<DecodeHintType, Object> hints = new EnumMap<>(DecodeHintType.class);
        hints.put(DecodeHintType.TRY_HARDER, Boolean.TRUE);
        hints.put(DecodeHintType.POSSIBLE_FORMATS, EnumSet.allOf(BarcodeFormat.class));
        hints.put(DecodeHintType.CHARACTER_SET, "UTF-8");
        return hints;
    }

    public static String decodeQRCode(File file) throws IOException, NotFoundException {
        BufferedImage image = ImageIO.read(file);
        if (image == null) {
            throw new IOException("无法读取图片文件: " + file.getAbsolutePath());
        }
        return decodeQRCode(image);
    }

    public static String decodeQRCode(BufferedImage image) throws NotFoundException {
        LuminanceSource source = new BufferedImageLuminanceSource(image);
        BinaryBitmap bitmap = new BinaryBitmap(new HybridBinarizer(source));
        
        MultiFormatReader reader = new MultiFormatReader();
        Result result = reader.decode(bitmap, DEFAULT_HINTS);
        
        return result.getText();
    }

    public static DecodeResult decodeQRCodeWithInfo(File file) throws IOException, NotFoundException {
        BufferedImage image = ImageIO.read(file);
        if (image == null) {
            throw new IOException("无法读取图片文件: " + file.getAbsolutePath());
        }
        return decodeQRCodeWithInfo(image);
    }

    public static DecodeResult decodeQRCodeWithInfo(BufferedImage image) throws NotFoundException {
        LuminanceSource source = new BufferedImageLuminanceSource(image);
        BinaryBitmap bitmap = new BinaryBitmap(new HybridBinarizer(source));
        
        MultiFormatReader reader = new MultiFormatReader();
        Result result = reader.decode(bitmap, DEFAULT_HINTS);
        
        return new DecodeResult(
            result.getText(),
            result.getBarcodeFormat().toString(),
            result.getTimestamp()
        );
    }

    public static boolean isQRCodeValid(File file) {
        try {
            decodeQRCode(file);
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    public static class DecodeResult {
        private final String content;
        private final String format;
        private final long timestamp;

        public DecodeResult(String content, String format, long timestamp) {
            this.content = content;
            this.format = format;
            this.timestamp = timestamp;
        }

        public String getContent() {
            return content;
        }

        public String getFormat() {
            return format;
        }

        public long getTimestamp() {
            return timestamp;
        }
    }
}
