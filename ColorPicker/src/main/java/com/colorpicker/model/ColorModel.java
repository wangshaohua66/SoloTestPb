package com.colorpicker.model;

import java.util.Objects;

public class ColorModel {
    private int red;
    private int green;
    private int blue;
    private double alpha;
    private String name;

    public ColorModel() {
        this(0, 0, 0, 1.0);
    }

    public ColorModel(int red, int green, int blue) {
        this(red, green, blue, 1.0);
    }

    public ColorModel(int red, int green, int blue, double alpha) {
        this.red = clamp(red, 0, 255);
        this.green = clamp(green, 0, 255);
        this.blue = clamp(blue, 0, 255);
        this.alpha = clamp(alpha, 0.0, 1.0);
        this.name = null;
    }

    public int getRed() {
        return red;
    }

    public void setRed(int red) {
        this.red = clamp(red, 0, 255);
    }

    public int getGreen() {
        return green;
    }

    public void setGreen(int green) {
        this.green = clamp(green, 0, 255);
    }

    public int getBlue() {
        return blue;
    }

    public void setBlue(int blue) {
        this.blue = clamp(blue, 0, 255);
    }

    public double getAlpha() {
        return alpha;
    }

    public void setAlpha(double alpha) {
        this.alpha = clamp(alpha, 0.0, 1.0);
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public RGB toRGB() {
        return new RGB(red, green, blue, alpha);
    }

    public HSV toHSV() {
        return RGBConverter.toHSV(this);
    }

    public HEX toHEX() {
        return RGBConverter.toHEX(this);
    }

    public static ColorModel fromRGB(int r, int g, int b) {
        return new ColorModel(r, g, b);
    }

    public static ColorModel fromRGB(int r, int g, int b, double alpha) {
        return new ColorModel(r, g, b, alpha);
    }

    public static ColorModel fromHSV(double h, double s, double v) {
        return RGBConverter.fromHSV(h, s, v);
    }

    public static ColorModel fromHSV(double h, double s, double v, double alpha) {
        ColorModel color = RGBConverter.fromHSV(h, s, v);
        color.setAlpha(alpha);
        return color;
    }

    public static ColorModel fromHEX(String hex) {
        return RGBConverter.fromHEX(hex);
    }

    public static ColorModel fromAWTColor(java.awt.Color awtColor) {
        return new ColorModel(
                awtColor.getRed(),
                awtColor.getGreen(),
                awtColor.getBlue(),
                awtColor.getAlpha() / 255.0
        );
    }

    public java.awt.Color toAWTColor() {
        return new java.awt.Color(red, green, blue, (int) (alpha * 255));
    }

    private int clamp(int value, int min, int max) {
        return Math.max(min, Math.min(max, value));
    }

    private double clamp(double value, double min, double max) {
        return Math.max(min, Math.min(max, value));
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ColorModel that = (ColorModel) o;
        return red == that.red && green == that.green && blue == that.blue &&
                Double.compare(that.alpha, alpha) == 0;
    }

    @Override
    public int hashCode() {
        return Objects.hash(red, green, blue, alpha);
    }

    @Override
    public String toString() {
        return "ColorModel{" +
                "red=" + red +
                ", green=" + green +
                ", blue=" + blue +
                ", alpha=" + alpha +
                '}';
    }
}
