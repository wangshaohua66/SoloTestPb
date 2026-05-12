package com.colorpicker.util;

import com.colorpicker.model.ColorModel;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class ColorNameRegistry {

    private static final Map<String, ColorEntry> COLORS = new HashMap<>();
    
    static {
        addColor("AliceBlue", 240, 248, 255);
        addColor("AntiqueWhite", 250, 235, 215);
        addColor("Aqua", 0, 255, 255);
        addColor("Aquamarine", 127, 255, 212);
        addColor("Azure", 240, 255, 255);
        addColor("Beige", 245, 245, 220);
        addColor("Bisque", 255, 228, 196);
        addColor("Black", 0, 0, 0);
        addColor("BlanchedAlmond", 255, 235, 205);
        addColor("Blue", 0, 0, 255);
        addColor("BlueViolet", 138, 43, 226);
        addColor("Brown", 165, 42, 42);
        addColor("BurlyWood", 222, 184, 135);
        addColor("CadetBlue", 95, 158, 160);
        addColor("Chartreuse", 127, 255, 0);
        addColor("Chocolate", 210, 105, 30);
        addColor("Coral", 255, 127, 80);
        addColor("CornflowerBlue", 100, 149, 237);
        addColor("Cornsilk", 255, 248, 220);
        addColor("Crimson", 220, 20, 60);
        addColor("Cyan", 0, 255, 255);
        addColor("DarkBlue", 0, 0, 139);
        addColor("DarkCyan", 0, 139, 139);
        addColor("DarkGoldenRod", 184, 134, 11);
        addColor("DarkGray", 169, 169, 169);
        addColor("DarkGreen", 0, 100, 0);
        addColor("DarkKhaki", 189, 183, 107);
        addColor("DarkMagenta", 139, 0, 139);
        addColor("DarkOliveGreen", 85, 107, 47);
        addColor("DarkOrange", 255, 140, 0);
        addColor("DarkOrchid", 153, 50, 204);
        addColor("DarkRed", 139, 0, 0);
        addColor("DarkSalmon", 233, 150, 122);
        addColor("DarkSeaGreen", 143, 188, 143);
        addColor("DarkSlateBlue", 72, 61, 139);
        addColor("DarkSlateGray", 47, 79, 79);
        addColor("DarkTurquoise", 0, 206, 209);
        addColor("DarkViolet", 148, 0, 211);
        addColor("DeepPink", 255, 20, 147);
        addColor("DeepSkyBlue", 0, 191, 255);
        addColor("DimGray", 105, 105, 105);
        addColor("DodgerBlue", 30, 144, 255);
        addColor("FireBrick", 178, 34, 34);
        addColor("FloralWhite", 255, 250, 240);
        addColor("ForestGreen", 34, 139, 34);
        addColor("Fuchsia", 255, 0, 255);
        addColor("Gainsboro", 220, 220, 220);
        addColor("GhostWhite", 248, 248, 255);
        addColor("Gold", 255, 215, 0);
        addColor("GoldenRod", 218, 165, 32);
        addColor("Gray", 128, 128, 128);
        addColor("Green", 0, 128, 0);
        addColor("GreenYellow", 173, 255, 47);
        addColor("HoneyDew", 240, 255, 240);
        addColor("HotPink", 255, 105, 180);
        addColor("IndianRed", 205, 92, 92);
        addColor("Indigo", 75, 0, 130);
        addColor("Ivory", 255, 255, 240);
        addColor("Khaki", 240, 230, 140);
        addColor("Lavender", 230, 230, 250);
        addColor("LavenderBlush", 255, 240, 245);
        addColor("LawnGreen", 124, 252, 0);
        addColor("LemonChiffon", 255, 250, 205);
        addColor("LightBlue", 173, 216, 230);
        addColor("LightCoral", 240, 128, 128);
        addColor("LightCyan", 224, 255, 255);
        addColor("LightGoldenRodYellow", 250, 250, 210);
        addColor("LightGray", 211, 211, 211);
        addColor("LightGreen", 144, 238, 144);
        addColor("LightPink", 255, 182, 193);
        addColor("LightSalmon", 255, 160, 122);
        addColor("LightSeaGreen", 32, 178, 170);
        addColor("LightSkyBlue", 135, 206, 250);
        addColor("LightSlateGray", 119, 136, 153);
        addColor("LightSteelBlue", 176, 196, 222);
        addColor("LightYellow", 255, 255, 224);
        addColor("Lime", 0, 255, 0);
        addColor("LimeGreen", 50, 205, 50);
        addColor("Linen", 250, 240, 230);
        addColor("Magenta", 255, 0, 255);
        addColor("Maroon", 128, 0, 0);
        addColor("MediumAquaMarine", 102, 205, 170);
        addColor("MediumBlue", 0, 0, 205);
        addColor("MediumOrchid", 186, 85, 211);
        addColor("MediumPurple", 147, 112, 219);
        addColor("MediumSeaGreen", 60, 179, 113);
        addColor("MediumSlateBlue", 123, 104, 238);
        addColor("MediumSpringGreen", 0, 250, 154);
        addColor("MediumTurquoise", 72, 209, 204);
        addColor("MediumVioletRed", 199, 21, 133);
        addColor("MidnightBlue", 25, 25, 112);
        addColor("MintCream", 245, 255, 250);
        addColor("MistyRose", 255, 228, 225);
        addColor("Moccasin", 255, 228, 181);
        addColor("NavajoWhite", 255, 222, 173);
        addColor("Navy", 0, 0, 128);
        addColor("OldLace", 253, 245, 230);
        addColor("Olive", 128, 128, 0);
        addColor("OliveDrab", 107, 142, 35);
        addColor("Orange", 255, 165, 0);
        addColor("OrangeRed", 255, 69, 0);
        addColor("Orchid", 218, 112, 214);
        addColor("PaleGoldenRod", 238, 232, 170);
        addColor("PaleGreen", 152, 251, 152);
        addColor("PaleTurquoise", 175, 238, 238);
        addColor("PaleVioletRed", 219, 112, 147);
        addColor("PapayaWhip", 255, 239, 213);
        addColor("PeachPuff", 255, 218, 185);
        addColor("Peru", 205, 133, 63);
        addColor("Pink", 255, 192, 203);
        addColor("Plum", 221, 160, 221);
        addColor("PowderBlue", 176, 224, 230);
        addColor("Purple", 128, 0, 128);
        addColor("RebeccaPurple", 102, 51, 153);
        addColor("Red", 255, 0, 0);
        addColor("RosyBrown", 188, 143, 143);
        addColor("RoyalBlue", 65, 105, 225);
        addColor("SaddleBrown", 139, 69, 19);
        addColor("Salmon", 250, 128, 114);
        addColor("SandyBrown", 244, 164, 96);
        addColor("SeaGreen", 46, 139, 87);
        addColor("SeaShell", 255, 245, 238);
        addColor("Sienna", 160, 82, 45);
        addColor("Silver", 192, 192, 192);
        addColor("SkyBlue", 135, 206, 235);
        addColor("SlateBlue", 106, 90, 205);
        addColor("SlateGray", 112, 128, 144);
        addColor("Snow", 255, 250, 250);
        addColor("SpringGreen", 0, 255, 127);
        addColor("SteelBlue", 70, 130, 180);
        addColor("Tan", 210, 180, 140);
        addColor("Teal", 0, 128, 128);
        addColor("Thistle", 216, 191, 216);
        addColor("Tomato", 255, 99, 71);
        addColor("Turquoise", 64, 224, 208);
        addColor("Violet", 238, 130, 238);
        addColor("Wheat", 245, 222, 179);
        addColor("White", 255, 255, 255);
        addColor("WhiteSmoke", 245, 245, 245);
        addColor("Yellow", 255, 255, 0);
        addColor("YellowGreen", 154, 205, 50);
    }
    
    private static void addColor(String name, int r, int g, int b) {
        COLORS.put(name.toLowerCase(), new ColorEntry(name, r, g, b));
    }
    
    public static ColorNameResult findClosestColor(ColorModel color) {
        return findClosestColor(color.getRed(), color.getGreen(), color.getBlue());
    }
    
    public static ColorNameResult findClosestColor(int r, int g, int b) {
        ColorEntry closest = null;
        double minDistance = Double.MAX_VALUE;
        
        for (ColorEntry entry : COLORS.values()) {
            double distance = colorDistance(r, g, b, entry.r, entry.g, entry.b);
            if (distance < minDistance) {
                minDistance = distance;
                closest = entry;
            }
        }
        
        if (closest != null) {
            return new ColorNameResult(
                    closest.name,
                    new ColorModel(closest.r, closest.g, closest.b),
                    minDistance
            );
        }
        return null;
    }
    
    public static List<ColorNameResult> findSimilarColors(ColorModel color, int maxResults) {
        return findSimilarColors(color.getRed(), color.getGreen(), color.getBlue(), maxResults);
    }
    
    public static List<ColorNameResult> findSimilarColors(int r, int g, int b, int maxResults) {
        List<ColorEntry> entries = new ArrayList<>(COLORS.values());
        
        entries.sort((entryA, entryB) -> {
            double distA = colorDistance(r, g, b, entryA.r, entryA.g, entryA.b);
            double distB = colorDistance(r, g, b, entryB.r, entryB.g, entryB.b);
            return Double.compare(distA, distB);
        });
        
        List<ColorNameResult> results = new ArrayList<>();
        for (int i = 0; i < Math.min(maxResults, entries.size()); i++) {
            ColorEntry entry = entries.get(i);
            double distance = colorDistance(r, g, b, entry.r, entry.g, entry.b);
            results.add(new ColorNameResult(
                    entry.name,
                    new ColorModel(entry.r, entry.g, entry.b),
                    distance
            ));
        }
        
        return results;
    }
    
    public static ColorModel getColorByName(String name) {
        ColorEntry entry = COLORS.get(name.toLowerCase());
        if (entry != null) {
            return new ColorModel(entry.r, entry.g, entry.b);
        }
        return null;
    }
    
    public static List<String> getAllColorNames() {
        List<String> names = new ArrayList<>();
        for (ColorEntry entry : COLORS.values()) {
            names.add(entry.name);
        }
        return names;
    }
    
    private static double colorDistance(int r1, int g1, int b1, int r2, int g2, int b2) {
        long rmean = (r1 + r2) / 2L;
        long r = r1 - r2;
        long g = g1 - g2;
        long b = b1 - b2;
        
        return Math.sqrt(
                (2 + rmean / 256.0) * r * r +
                4 * g * g +
                (2 + (255 - rmean) / 256.0) * b * b
        );
    }
    
    private static class ColorEntry {
        String name;
        int r;
        int g;
        int b;
        
        ColorEntry(String name, int r, int g, int b) {
            this.name = name;
            this.r = r;
            this.g = g;
            this.b = b;
        }
    }
    
    public static class ColorNameResult {
        private final String name;
        private final ColorModel color;
        private final double distance;
        
        public ColorNameResult(String name, ColorModel color, double distance) {
            this.name = name;
            this.color = color;
            this.distance = distance;
        }
        
        public String getName() {
            return name;
        }
        
        public ColorModel getColor() {
            return color;
        }
        
        public double getDistance() {
            return distance;
        }
        
        public boolean isExactMatch() {
            return distance == 0.0;
        }
    }
}
