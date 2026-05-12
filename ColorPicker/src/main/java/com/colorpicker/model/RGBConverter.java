package com.colorpicker.model;

public class RGBConverter {

    public static HSV toHSV(ColorModel color) {
        int r = color.getRed();
        int g = color.getGreen();
        int b = color.getBlue();

        double rNorm = r / 255.0;
        double gNorm = g / 255.0;
        double bNorm = b / 255.0;

        double max = Math.max(Math.max(rNorm, gNorm), bNorm);
        double min = Math.min(Math.min(rNorm, gNorm), bNorm);
        double delta = max - min;

        double hue = 0;
        double saturation = max == 0 ? 0 : delta / max;
        double value = max;

        if (delta != 0) {
            if (rNorm == max) {
                hue = ((gNorm - bNorm) / delta);
            } else if (gNorm == max) {
                hue = 2 + ((bNorm - rNorm) / delta);
            } else {
                hue = 4 + ((rNorm - gNorm) / delta);
            }
            hue *= 60;
            if (hue < 0) {
                hue += 360;
            }
        }

        return new HSV(hue, saturation, value, color.getAlpha());
    }

    public static ColorModel fromHSV(double hue, double saturation, double value) {
        hue = hue % 360;
        if (hue < 0) {
            hue += 360;
        }
        saturation = Math.max(0, Math.min(1, saturation));
        value = Math.max(0, Math.min(1, value));

        double c = value * saturation;
        double x = c * (1 - Math.abs((hue / 60) % 2 - 1));
        double m = value - c;

        double r = 0, g = 0, b = 0;
        if (hue >= 0 && hue < 60) {
            r = c; g = x; b = 0;
        } else if (hue >= 60 && hue < 120) {
            r = x; g = c; b = 0;
        } else if (hue >= 120 && hue < 180) {
            r = 0; g = c; b = x;
        } else if (hue >= 180 && hue < 240) {
            r = 0; g = x; b = c;
        } else if (hue >= 240 && hue < 300) {
            r = x; g = 0; b = c;
        } else if (hue >= 300 && hue < 360) {
            r = c; g = 0; b = x;
        }

        return new ColorModel(
                (int) ((r + m) * 255),
                (int) ((g + m) * 255),
                (int) ((b + m) * 255)
        );
    }

    public static HEX toHEX(ColorModel color) {
        int r = color.getRed();
        int g = color.getGreen();
        int b = color.getBlue();
        int a = (int) (color.getAlpha() * 255);

        StringBuilder sb = new StringBuilder();
        if (color.getAlpha() != 1.0) {
            sb.append(String.format("%02X%02X%02X%02X", r, g, b, a));
        } else {
            sb.append(String.format("%02X%02X%02X", r, g, b));
        }

        return new HEX(sb.toString());
    }

    public static ColorModel fromHEX(String hex) {
        String normalized = hex.trim();
        if (normalized.startsWith("#")) {
            normalized = normalized.substring(1);
        }

        int r, g, b, a = 255;

        if (normalized.length() == 3) {
            r = Integer.parseInt(repeatChar(normalized.substring(0, 1), 2), 16);
            g = Integer.parseInt(repeatChar(normalized.substring(1, 2), 2), 16);
            b = Integer.parseInt(repeatChar(normalized.substring(2, 3), 2), 16);
        } else if (normalized.length() == 4) {
            r = Integer.parseInt(repeatChar(normalized.substring(0, 1), 2), 16);
            g = Integer.parseInt(repeatChar(normalized.substring(1, 2), 2), 16);
            b = Integer.parseInt(repeatChar(normalized.substring(2, 3), 2), 16);
            a = Integer.parseInt(repeatChar(normalized.substring(3, 4), 2), 16);
        } else if (normalized.length() == 6) {
            r = Integer.parseInt(normalized.substring(0, 2), 16);
            g = Integer.parseInt(normalized.substring(2, 4), 16);
            b = Integer.parseInt(normalized.substring(4, 6), 16);
        } else if (normalized.length() == 8) {
            r = Integer.parseInt(normalized.substring(0, 2), 16);
            g = Integer.parseInt(normalized.substring(2, 4), 16);
            b = Integer.parseInt(normalized.substring(4, 6), 16);
            a = Integer.parseInt(normalized.substring(6, 8), 16);
        } else {
            throw new IllegalArgumentException("Invalid HEX color: " + hex);
        }

        return new ColorModel(r, g, b, a / 255.0);
    }

    public static String toCSSString(ColorModel color) {
        if (color.getAlpha() == 1.0) {
            return "rgb(" + color.getRed() + ", " + color.getGreen() + ", " + color.getBlue() + ")";
        } else {
            return "rgba(" + color.getRed() + ", " + color.getGreen() + ", " + color.getBlue() + ", " + String.format("%.2f", color.getAlpha()) + ")";
        }
    }

    public static String toAndroidColorString(ColorModel color) {
        int a = (int) (color.getAlpha() * 255);
        return String.format("%02X%02X%02X%02X", a, color.getRed(), color.getGreen(), color.getBlue());
    }

    public static String toiOSColorString(ColorModel color) {
        return String.format("[UIColor colorWithRed:%.3f green:%.3f blue:%.3f alpha:%.2f]",
                color.getRed() / 255.0,
                color.getGreen() / 255.0,
                color.getBlue() / 255.0,
                color.getAlpha());
    }

    private static String repeatChar(String str, int times) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < times; i++) {
            sb.append(str);
        }
        return sb.toString();
    }
}
