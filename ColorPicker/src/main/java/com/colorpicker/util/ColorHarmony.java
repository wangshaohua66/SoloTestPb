package com.colorpicker.util;

import com.colorpicker.model.ColorModel;
import com.colorpicker.model.HSV;

import java.util.ArrayList;
import java.util.List;

public class ColorHarmony {

    public static List<ColorModel> getComplementaryColors(ColorModel baseColor) {
        List<ColorModel> colors = new ArrayList<>();
        HSV hsv = baseColor.toHSV();
        
        colors.add(baseColor);
        colors.add(ColorModel.fromHSV((hsv.getHue() + 180) % 360, hsv.getSaturation(), hsv.getValue()));
        
        return colors;
    }

    public static List<ColorModel> getAnalogousColors(ColorModel baseColor) {
        return getAnalogousColors(baseColor, 30);
    }

    public static List<ColorModel> getAnalogousColors(ColorModel baseColor, double angle) {
        List<ColorModel> colors = new ArrayList<>();
        HSV hsv = baseColor.toHSV();
        
        colors.add(ColorModel.fromHSV((hsv.getHue() - angle + 360) % 360, hsv.getSaturation(), hsv.getValue()));
        colors.add(baseColor);
        colors.add(ColorModel.fromHSV((hsv.getHue() + angle) % 360, hsv.getSaturation(), hsv.getValue()));
        
        return colors;
    }

    public static List<ColorModel> getTriadicColors(ColorModel baseColor) {
        List<ColorModel> colors = new ArrayList<>();
        HSV hsv = baseColor.toHSV();
        
        colors.add(baseColor);
        colors.add(ColorModel.fromHSV((hsv.getHue() + 120) % 360, hsv.getSaturation(), hsv.getValue()));
        colors.add(ColorModel.fromHSV((hsv.getHue() + 240) % 360, hsv.getSaturation(), hsv.getValue()));
        
        return colors;
    }

    public static List<ColorModel> getTetradicColors(ColorModel baseColor) {
        List<ColorModel> colors = new ArrayList<>();
        HSV hsv = baseColor.toHSV();
        
        colors.add(baseColor);
        colors.add(ColorModel.fromHSV((hsv.getHue() + 90) % 360, hsv.getSaturation(), hsv.getValue()));
        colors.add(ColorModel.fromHSV((hsv.getHue() + 180) % 360, hsv.getSaturation(), hsv.getValue()));
        colors.add(ColorModel.fromHSV((hsv.getHue() + 270) % 360, hsv.getSaturation(), hsv.getValue()));
        
        return colors;
    }

    public static List<ColorModel> getSplitComplementaryColors(ColorModel baseColor) {
        List<ColorModel> colors = new ArrayList<>();
        HSV hsv = baseColor.toHSV();
        
        colors.add(baseColor);
        colors.add(ColorModel.fromHSV((hsv.getHue() + 150) % 360, hsv.getSaturation(), hsv.getValue()));
        colors.add(ColorModel.fromHSV((hsv.getHue() + 210) % 360, hsv.getSaturation(), hsv.getValue()));
        
        return colors;
    }

    public static List<ColorModel> getMonochromaticColors(ColorModel baseColor) {
        List<ColorModel> colors = new ArrayList<>();
        HSV hsv = baseColor.toHSV();
        double hue = hsv.getHue();
        
        colors.add(ColorModel.fromHSV(hue, 0.1, 0.9));
        colors.add(ColorModel.fromHSV(hue, 0.3, 0.8));
        colors.add(ColorModel.fromHSV(hue, hsv.getSaturation(), hsv.getValue()));
        colors.add(ColorModel.fromHSV(hue, 0.7, 0.6));
        colors.add(ColorModel.fromHSV(hue, 0.9, 0.4));
        
        return colors;
    }

    public static List<ColorModel> getShades(ColorModel baseColor, int count) {
        List<ColorModel> colors = new ArrayList<>();
        HSV hsv = baseColor.toHSV();
        
        for (int i = 0; i < count; i++) {
            double factor = 1.0 - (i / (double) (count - 1));
            colors.add(ColorModel.fromHSV(hsv.getHue(), hsv.getSaturation(), hsv.getValue() * factor));
        }
        
        return colors;
    }

    public static List<ColorModel> getTints(ColorModel baseColor, int count) {
        List<ColorModel> colors = new ArrayList<>();
        HSV hsv = baseColor.toHSV();
        
        for (int i = 0; i < count; i++) {
            double factor = i / (double) (count - 1);
            double value = hsv.getValue() + (1.0 - hsv.getValue()) * factor;
            double saturation = hsv.getSaturation() * (1.0 - factor);
            colors.add(ColorModel.fromHSV(hsv.getHue(), saturation, value));
        }
        
        return colors;
    }

    public static List<ColorModel> getTones(ColorModel baseColor, int count) {
        List<ColorModel> colors = new ArrayList<>();
        HSV hsv = baseColor.toHSV();
        double graySaturation = 0.0;
        double baseValue = hsv.getValue();
        
        for (int i = 0; i < count; i++) {
            double factor = i / (double) (count - 1);
            double saturation = hsv.getSaturation() * (1.0 - factor) + graySaturation * factor;
            double value = baseValue;
            colors.add(ColorModel.fromHSV(hsv.getHue(), saturation, value));
        }
        
        return colors;
    }
}
