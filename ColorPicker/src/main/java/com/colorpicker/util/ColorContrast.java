package com.colorpicker.util;

import com.colorpicker.model.ColorModel;

public class ColorContrast {

    public static double calculateContrastRatio(ColorModel foreground, ColorModel background) {
        double fgLuminance = calculateRelativeLuminance(foreground);
        double bgLuminance = calculateRelativeLuminance(background);
        
        double lighter = Math.max(fgLuminance, bgLuminance);
        double darker = Math.min(fgLuminance, bgLuminance);
        
        return (lighter + 0.05) / (darker + 0.05);
    }

    public static double calculateRelativeLuminance(ColorModel color) {
        double r = color.getRed() / 255.0;
        double g = color.getGreen() / 255.0;
        double b = color.getBlue() / 255.0;
        
        r = (r <= 0.03928) ? r / 12.92 : Math.pow((r + 0.055) / 1.055, 2.4);
        g = (g <= 0.03928) ? g / 12.92 : Math.pow((g + 0.055) / 1.055, 2.4);
        b = (b <= 0.03928) ? b / 12.92 : Math.pow((b + 0.055) / 1.055, 2.4);
        
        return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    }

    public static WCAGLevel getWCAGLevel(double contrastRatio, boolean isLargeText) {
        if (isLargeText) {
            if (contrastRatio >= 4.5) {
                return WCAGLevel.AAA;
            } else if (contrastRatio >= 3.0) {
                return WCAGLevel.AA;
            }
        } else {
            if (contrastRatio >= 7.0) {
                return WCAGLevel.AAA;
            } else if (contrastRatio >= 4.5) {
                return WCAGLevel.AA;
            }
        }
        return WCAGLevel.FAIL;
    }

    public static boolean isAccessible(ColorModel foreground, ColorModel background) {
        return isAccessible(foreground, background, false);
    }

    public static boolean isAccessible(ColorModel foreground, ColorModel background, boolean isLargeText) {
        double ratio = calculateContrastRatio(foreground, background);
        return getWCAGLevel(ratio, isLargeText) != WCAGLevel.FAIL;
    }

    public static boolean isAccessible(double contrastRatio, boolean isAAARequired, boolean isLargeText) {
        if (isLargeText) {
            if (isAAARequired) {
                return contrastRatio >= 4.5;
            } else {
                return contrastRatio >= 3.0;
            }
        } else {
            if (isAAARequired) {
                return contrastRatio >= 7.0;
            } else {
                return contrastRatio >= 4.5;
            }
        }
    }

    public enum WCAGLevel {
        FAIL("Fail"),
        AA("AA"),
        AAA("AAA");
        
        private final String label;
        
        WCAGLevel(String label) {
            this.label = label;
        }
        
        public String getLabel() {
            return label;
        }
    }
}
