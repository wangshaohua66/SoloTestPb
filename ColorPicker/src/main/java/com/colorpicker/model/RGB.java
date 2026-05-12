package com.colorpicker.model;

public class RGB {
    private int red;
    private int green;
    private int blue;
    private double alpha;

    public RGB() {
        this(0, 0, 0, 1.0);
    }

    public RGB(int red, int green, int blue) {
        this(red, green, blue, 1.0);
    }

    public RGB(int red, int green, int blue, double alpha) {
        this.red = clamp(red, 0, 255);
        this.green = clamp(green, 0, 255);
        this.blue = clamp(blue, 0, 255);
        this.alpha = clamp(alpha, 0.0, 1.0);
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

    public ColorModel toColorModel() {
        return new ColorModel(red, green, blue, alpha);
    }

    public HSV toHSV() {
        return RGBConverter.toHSV(this.toColorModel());
    }

    public HEX toHEX() {
        return RGBConverter.toHEX(this.toColorModel());
    }

    private int clamp(int value, int min, int max) {
        return Math.max(min, Math.min(max, value));
    }

    private double clamp(double value, double min, double max) {
        return Math.max(min, Math.min(max, value));
    }

    @Override
    public String toString() {
        return "RGB(" + red + ", " + green + ", " + blue + ", " + alpha + ")";
    }
}
