package com.colorpicker.model;

public class HEX {
    private String value;
    private boolean hasAlpha;

    public HEX() {
        this("#000000");
    }

    public HEX(String hexValue) {
        this.value = normalizeHex(hexValue);
        this.hasAlpha = this.value.length() == 8;
    }

    public String getValue() {
        return value;
    }

    public void setValue(String value) {
        this.value = normalizeHex(value);
        this.hasAlpha = this.value.length() == 8;
    }

    public boolean hasAlpha() {
        return hasAlpha;
    }

    public ColorModel toColorModel() {
        return ColorModel.fromHEX(value);
    }

    public RGB toRGB() {
        return this.toColorModel().toRGB();
    }

    public HSV toHSV() {
        return this.toColorModel().toHSV();
    }

    public String toHexString() {
        return "#" + value;
    }

    public String toHexStringWithAlpha() {
        if (hasAlpha) {
            return "#" + value;
        }
        return "#" + value + "FF";
    }

    private String normalizeHex(String hex) {
        if (hex == null || hex.isEmpty()) {
            return "000000";
        }

        String normalized = hex.trim();
        if (normalized.startsWith("#")) {
            normalized = normalized.substring(1);
        }

        if (normalized.length() == 3) {
            StringBuilder sb = new StringBuilder();
            for (char c : normalized.toCharArray()) {
                sb.append(c).append(c);
            }
            normalized = sb.toString();
        } else if (normalized.length() == 4) {
            StringBuilder sb = new StringBuilder();
            for (char c : normalized.toCharArray()) {
                sb.append(c).append(c);
            }
            normalized = sb.toString();
        }

        if (normalized.length() != 6 && normalized.length() != 8) {
            normalized = normalized.length() > 8 ? normalized.substring(0, 8) : normalized;
            while (normalized.length() < 6) {
                normalized += "0";
            }
        }

        return normalized.toUpperCase();
    }

    @Override
    public String toString() {
        return "HEX(" + value + ")";
    }
}
