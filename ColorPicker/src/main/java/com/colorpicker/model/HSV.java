package com.colorpicker.model;

public class HSV {
    private double hue;
    private double saturation;
    private double value;
    private double alpha;

    public HSV() {
        this(0, 0, 0, 1.0);
    }

    public HSV(double hue, double saturation, double value) {
        this(hue, saturation, value, 1.0);
    }

    public HSV(double hue, double saturation, double value, double alpha) {
        this.hue = clampHue(hue);
        this.saturation = clamp(saturation, 0.0, 1.0);
        this.value = clamp(value, 0.0, 1.0);
        this.alpha = clamp(alpha, 0.0, 1.0);
    }

    public double getHue() {
        return hue;
    }

    public void setHue(double hue) {
        this.hue = clampHue(hue);
    }

    public double getSaturation() {
        return saturation;
    }

    public void setSaturation(double saturation) {
        this.saturation = clamp(saturation, 0.0, 1.0);
    }

    public double getValue() {
        return value;
    }

    public void setValue(double value) {
        this.value = clamp(value, 0.0, 1.0);
    }

    public double getAlpha() {
        return alpha;
    }

    public void setAlpha(double alpha) {
        this.alpha = clamp(alpha, 0.0, 1.0);
    }

    public ColorModel toColorModel() {
        return ColorModel.fromHSV(hue, saturation, value, alpha);
    }

    public RGB toRGB() {
        return this.toColorModel().toRGB();
    }

    public HEX toHEX() {
        return this.toColorModel().toHEX();
    }

    private double clampHue(double hue) {
        hue = hue % 360;
        if (hue < 0) {
            hue += 360;
        }
        return hue;
    }

    private double clamp(double value, double min, double max) {
        return Math.max(min, Math.min(max, value));
    }

    @Override
    public String toString() {
        return "HSV(" + hue + "°, " + (saturation * 100) + "%, " + (value * 100) + "%, " + alpha + ")";
    }
}
