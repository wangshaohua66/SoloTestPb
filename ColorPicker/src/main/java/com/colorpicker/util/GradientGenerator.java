package com.colorpicker.util;

import com.colorpicker.model.ColorModel;
import com.colorpicker.model.RGBConverter;

import java.util.ArrayList;
import java.util.List;

public class GradientGenerator {

    public static List<ColorModel> generateLinearGradient(ColorModel startColor, ColorModel endColor, int steps) {
        List<ColorModel> colors = new ArrayList<>();
        
        double startR = startColor.getRed() / 255.0;
        double startG = startColor.getGreen() / 255.0;
        double startB = startColor.getBlue() / 255.0;
        double startA = startColor.getAlpha();
        
        double endR = endColor.getRed() / 255.0;
        double endG = endColor.getGreen() / 255.0;
        double endB = endColor.getBlue() / 255.0;
        double endA = endColor.getAlpha();
        
        for (int i = 0; i < steps; i++) {
            double t = (double) i / (steps - 1);
            
            int r = (int) Math.round((startR + (endR - startR) * t) * 255);
            int g = (int) Math.round((startG + (endG - startG) * t) * 255);
            int b = (int) Math.round((startB + (endB - startB) * t) * 255);
            double a = startA + (endA - startA) * t;
            
            colors.add(new ColorModel(r, g, b, a));
        }
        
        return colors;
    }

    public static List<ColorModel> generateMultiStopGradient(List<ColorModel> colors, List<Double> stops, int steps) {
        if (colors.size() < 2) {
            throw new IllegalArgumentException("Multi-stop gradient requires at least 2 colors");
        }
        
        if (stops != null && stops.size() != colors.size()) {
            throw new IllegalArgumentException("Number of stops must match number of colors");
        }
        
        List<ColorModel> result = new ArrayList<>();
        
        double[] stopPositions;
        if (stops == null) {
            stopPositions = new double[colors.size()];
            for (int i = 0; i < colors.size(); i++) {
                stopPositions[i] = (double) i / (colors.size() - 1);
            }
        } else {
            stopPositions = new double[stops.size()];
            for (int i = 0; i < stops.size(); i++) {
                stopPositions[i] = stops.get(i);
            }
        }
        
        for (int i = 0; i < steps; i++) {
            double t = (double) i / (steps - 1);
            
            int segmentIndex = 0;
            for (int j = 0; j < stopPositions.length - 1; j++) {
                if (t >= stopPositions[j] && t <= stopPositions[j + 1]) {
                    segmentIndex = j;
                    break;
                }
            }
            
            double segmentStart = stopPositions[segmentIndex];
            double segmentEnd = stopPositions[segmentIndex + 1];
            double segmentT = (t - segmentStart) / (segmentEnd - segmentStart);
            
            ColorModel startColor = colors.get(segmentIndex);
            ColorModel endColor = colors.get(segmentIndex + 1);
            
            double r = interpolate(startColor.getRed(), endColor.getRed(), segmentT);
            double g = interpolate(startColor.getGreen(), endColor.getGreen(), segmentT);
            double b = interpolate(startColor.getBlue(), endColor.getBlue(), segmentT);
            double a = interpolate(startColor.getAlpha(), endColor.getAlpha(), segmentT);
            
            result.add(new ColorModel((int) r, (int) g, (int) b, a));
        }
        
        return result;
    }

    private static double interpolate(double start, double end, double t) {
        return start + (end - start) * t;
    }

    public static String generateCSSLinearGradient(List<ColorModel> colors, String direction) {
        StringBuilder sb = new StringBuilder();
        sb.append("linear-gradient(");
        if (direction != null && !direction.isEmpty()) {
            sb.append(direction).append(", ");
        }
        
        for (int i = 0; i < colors.size(); i++) {
            sb.append(RGBConverter.toCSSString(colors.get(i)));
            if (i < colors.size() - 1) {
                sb.append(", ");
            }
        }
        
        sb.append(")");
        return sb.toString();
    }

    public static String generateCSSRadialGradient(List<ColorModel> colors, String shape, String size) {
        StringBuilder sb = new StringBuilder();
        sb.append("radial-gradient(");
        
        boolean hasParams = false;
        if (shape != null && !shape.isEmpty()) {
            sb.append(shape);
            hasParams = true;
        }
        if (size != null && !size.isEmpty()) {
            if (hasParams) {
                sb.append(" ");
            }
            sb.append(size);
            hasParams = true;
        }
        if (hasParams) {
            sb.append(", ");
        }
        
        for (int i = 0; i < colors.size(); i++) {
            sb.append(RGBConverter.toCSSString(colors.get(i)));
            if (i < colors.size() - 1) {
                sb.append(", ");
            }
        }
        
        sb.append(")");
        return sb.toString();
    }

    public static List<ColorModel> generateHueGradient(int steps) {
        List<ColorModel> colors = new ArrayList<>();
        
        for (int i = 0; i < steps; i++) {
            double hue = (i / (double) steps) * 360;
            colors.add(ColorModel.fromHSV(hue, 1.0, 1.0));
        }
        
        return colors;
    }

    public static List<ColorModel> generateSaturationGradient(double hue, double value, int steps) {
        List<ColorModel> colors = new ArrayList<>();
        
        for (int i = 0; i < steps; i++) {
            double saturation = i / (double) (steps - 1);
            colors.add(ColorModel.fromHSV(hue, saturation, value));
        }
        
        return colors;
    }

    public static List<ColorModel> generateValueGradient(double hue, double saturation, int steps) {
        List<ColorModel> colors = new ArrayList<>();
        
        for (int i = 0; i < steps; i++) {
            double value = i / (double) (steps - 1);
            colors.add(ColorModel.fromHSV(hue, saturation, value));
        }
        
        return colors;
    }
}
