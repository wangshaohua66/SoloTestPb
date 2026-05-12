package com.qrcode.model;

import java.awt.Color;
import java.io.Serializable;

public class QRCodeStyle implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private int size = 300;
    private int margin = 10;
    private int foregroundColorRGB = Color.BLACK.getRGB();
    private int backgroundColorRGB = Color.WHITE.getRGB();
    private String logoPath;
    private double logoScale = 0.2;
    private int borderWidth = 0;
    private int borderColorRGB = Color.BLACK.getRGB();
    private QRCodeFormat format = QRCodeFormat.QR_CODE;
    private ErrorCorrectionLevel errorLevel = ErrorCorrectionLevel.L;

    public QRCodeStyle() {
    }

    public int getSize() {
        return size;
    }

    public void setSize(int size) {
        this.size = size;
    }

    public int getMargin() {
        return margin;
    }

    public void setMargin(int margin) {
        this.margin = margin;
    }

    public Color getForegroundColor() {
        return new Color(foregroundColorRGB);
    }

    public void setForegroundColor(Color foregroundColor) {
        this.foregroundColorRGB = foregroundColor.getRGB();
    }

    public int getForegroundColorRGB() {
        return foregroundColorRGB;
    }

    public void setForegroundColorRGB(int foregroundColorRGB) {
        this.foregroundColorRGB = foregroundColorRGB;
    }

    public Color getBackgroundColor() {
        return new Color(backgroundColorRGB);
    }

    public void setBackgroundColor(Color backgroundColor) {
        this.backgroundColorRGB = backgroundColor.getRGB();
    }

    public int getBackgroundColorRGB() {
        return backgroundColorRGB;
    }

    public void setBackgroundColorRGB(int backgroundColorRGB) {
        this.backgroundColorRGB = backgroundColorRGB;
    }

    public String getLogoPath() {
        return logoPath;
    }

    public void setLogoPath(String logoPath) {
        this.logoPath = logoPath;
    }

    public double getLogoScale() {
        return logoScale;
    }

    public void setLogoScale(double logoScale) {
        this.logoScale = logoScale;
    }

    public int getBorderWidth() {
        return borderWidth;
    }

    public void setBorderWidth(int borderWidth) {
        this.borderWidth = borderWidth;
    }

    public Color getBorderColor() {
        return new Color(borderColorRGB);
    }

    public void setBorderColor(Color borderColor) {
        this.borderColorRGB = borderColor.getRGB();
    }

    public int getBorderColorRGB() {
        return borderColorRGB;
    }

    public void setBorderColorRGB(int borderColorRGB) {
        this.borderColorRGB = borderColorRGB;
    }

    public QRCodeFormat getFormat() {
        return format;
    }

    public void setFormat(QRCodeFormat format) {
        this.format = format;
    }

    public ErrorCorrectionLevel getErrorLevel() {
        return errorLevel;
    }

    public void setErrorLevel(ErrorCorrectionLevel errorLevel) {
        this.errorLevel = errorLevel;
    }

    public enum QRCodeFormat {
        QR_CODE("QR Code"),
        DATA_MATRIX("Data Matrix"),
        PDF_417("PDF 417"),
        AZTEC("Aztec"),
        CODE_128("Code 128"),
        EAN_13("EAN-13");

        private final String description;

        QRCodeFormat(String description) {
            this.description = description;
        }

        public String getDescription() {
            return description;
        }
    }

    public enum ErrorCorrectionLevel {
        L("低 (7%)"),
        M("中 (15%)"),
        Q("较高 (25%)"),
        H("高 (30%)");

        private final String description;

        ErrorCorrectionLevel(String description) {
            this.description = description;
        }

        public String getDescription() {
            return description;
        }
    }
}
