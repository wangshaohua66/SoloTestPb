package com.qrcode.util;

import com.google.zxing.*;
import com.google.zxing.client.j2se.MatrixToImageConfig;
import com.google.zxing.client.j2se.MatrixToImageWriter;
import com.google.zxing.common.BitMatrix;
import com.google.zxing.qrcode.decoder.ErrorCorrectionLevel;
import com.qrcode.model.QRCodeStyle;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.geom.RoundRectangle2D;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.EnumMap;
import java.util.Map;

public class QRCodeGenerator {

    private static final String FORMAT_NAME = "PNG";

    public static BufferedImage generateQRCode(String content, QRCodeStyle style) throws WriterException, IOException {
        if (content == null || content.isEmpty()) {
            throw new IllegalArgumentException("二维码内容不能为空");
        }
        
        Map<EncodeHintType, Object> hints = createEncodeHints(style);
        
        BitMatrix bitMatrix = createBitMatrix(content, style, hints);
        
        MatrixToImageConfig config = createImageConfig(style);
        
        BufferedImage image = MatrixToImageWriter.toBufferedImage(bitMatrix, config);
        
        if (style.getBorderWidth() > 0) {
            image = addBorder(image, style);
        }
        
        if (style.getLogoPath() != null && !style.getLogoPath().isEmpty()) {
            image = addLogo(image, style);
        }
        
        return image;
    }

    private static Map<EncodeHintType, Object> createEncodeHints(QRCodeStyle style) {
        Map<EncodeHintType, Object> hints = new EnumMap<>(EncodeHintType.class);
        hints.put(EncodeHintType.CHARACTER_SET, "UTF-8");
        hints.put(EncodeHintType.MARGIN, style.getMargin());
        hints.put(EncodeHintType.ERROR_CORRECTION, getErrorCorrectionLevel(style.getErrorLevel()));
        return hints;
    }

    private static BitMatrix createBitMatrix(String content, QRCodeStyle style, Map<EncodeHintType, Object> hints) throws WriterException {
        MultiFormatWriter writer = new MultiFormatWriter();
        BarcodeFormat format = getBarcodeFormat(style.getFormat());
        return writer.encode(content, format, style.getSize(), style.getSize(), hints);
    }

    private static MatrixToImageConfig createImageConfig(QRCodeStyle style) {
        return new MatrixToImageConfig(
            style.getForegroundColorRGB(),
            style.getBackgroundColorRGB()
        );
    }

    private static BarcodeFormat getBarcodeFormat(QRCodeStyle.QRCodeFormat format) {
        switch (format) {
            case QR_CODE:
                return BarcodeFormat.QR_CODE;
            case DATA_MATRIX:
                return BarcodeFormat.DATA_MATRIX;
            case PDF_417:
                return BarcodeFormat.PDF_417;
            case AZTEC:
                return BarcodeFormat.AZTEC;
            case CODE_128:
                return BarcodeFormat.CODE_128;
            case EAN_13:
                return BarcodeFormat.EAN_13;
            default:
                return BarcodeFormat.QR_CODE;
        }
    }

    private static ErrorCorrectionLevel getErrorCorrectionLevel(QRCodeStyle.ErrorCorrectionLevel level) {
        switch (level) {
            case L:
                return ErrorCorrectionLevel.L;
            case M:
                return ErrorCorrectionLevel.M;
            case Q:
                return ErrorCorrectionLevel.Q;
            case H:
                return ErrorCorrectionLevel.H;
            default:
                return ErrorCorrectionLevel.M;
        }
    }

    private static BufferedImage addBorder(BufferedImage image, QRCodeStyle style) {
        int borderWidth = style.getBorderWidth();
        int newWidth = image.getWidth() + 2 * borderWidth;
        int newHeight = image.getHeight() + 2 * borderWidth;
        
        BufferedImage borderedImage = new BufferedImage(newWidth, newHeight, BufferedImage.TYPE_INT_ARGB);
        Graphics2D g2d = borderedImage.createGraphics();
        
        g2d.setColor(style.getBorderColor());
        g2d.fillRect(0, 0, newWidth, newHeight);
        
        g2d.drawImage(image, borderWidth, borderWidth, null);
        g2d.dispose();
        
        return borderedImage;
    }

    private static BufferedImage addLogo(BufferedImage source, QRCodeStyle style) throws IOException {
        File logoFile = new File(style.getLogoPath());
        if (!logoFile.exists()) {
            return source;
        }
        
        BufferedImage logo = ImageIO.read(logoFile);
        if (logo == null) {
            return source;
        }
        
        int sourceWidth = source.getWidth();
        int sourceHeight = source.getHeight();
        int logoWidth = (int) (sourceWidth * style.getLogoScale());
        int logoHeight = (int) (sourceHeight * style.getLogoScale());
        
        BufferedImage scaledLogo = new BufferedImage(logoWidth, logoHeight, BufferedImage.TYPE_INT_ARGB);
        Graphics2D g2d = scaledLogo.createGraphics();
        g2d.setRenderingHint(RenderingHints.KEY_INTERPOLATION, RenderingHints.VALUE_INTERPOLATION_BILINEAR);
        g2d.drawImage(logo, 0, 0, logoWidth, logoHeight, null);
        g2d.dispose();
        
        Graphics2D sourceG2d = source.createGraphics();
        sourceG2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        
        int x = (sourceWidth - logoWidth) / 2;
        int y = (sourceHeight - logoHeight) / 2;
        
        int cornerRadius = 10;
        RoundRectangle2D.Float roundRect = new RoundRectangle2D.Float(x, y, logoWidth, logoHeight, cornerRadius, cornerRadius);
        sourceG2d.setClip(roundRect);
        
        sourceG2d.drawImage(scaledLogo, x, y, null);
        
        sourceG2d.setClip(null);
        sourceG2d.setStroke(new BasicStroke(3));
        sourceG2d.setColor(Color.WHITE);
        sourceG2d.draw(roundRect);
        
        sourceG2d.dispose();
        
        return source;
    }

    public static void saveQRCode(BufferedImage image, String filePath) throws IOException {
        File file = new File(filePath);
        if (!file.getParentFile().exists()) {
            file.getParentFile().mkdirs();
        }
        ImageIO.write(image, FORMAT_NAME, file);
    }
}
