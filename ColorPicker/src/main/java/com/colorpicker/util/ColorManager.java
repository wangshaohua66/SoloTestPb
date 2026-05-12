package com.colorpicker.util;

import com.colorpicker.model.ColorModel;
import com.colorpicker.model.RGBConverter;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class ColorManager {
    private List<ColorModel> favorites;
    private Map<String, List<ColorModel>> categories;

    public ColorManager() {
        this.favorites = new ArrayList<>();
        this.categories = new HashMap<>();
    }

    public void addToFavorites(ColorModel color) {
        if (!favorites.contains(color)) {
            favorites.add(color);
        }
    }

    public void removeFromFavorites(ColorModel color) {
        favorites.remove(color);
    }

    public boolean isFavorite(ColorModel color) {
        return favorites.contains(color);
    }

    public List<ColorModel> getFavorites() {
        return new ArrayList<>(favorites);
    }

    public void createCategory(String categoryName) {
        if (!categories.containsKey(categoryName)) {
            categories.put(categoryName, new ArrayList<>());
        }
    }

    public void addToCategory(String categoryName, ColorModel color) {
        List<ColorModel> categoryColors = categories.get(categoryName);
        if (categoryColors != null && !categoryColors.contains(color)) {
            categoryColors.add(color);
        }
    }

    public void removeFromCategory(String categoryName, ColorModel color) {
        List<ColorModel> categoryColors = categories.get(categoryName);
        if (categoryColors != null) {
            categoryColors.remove(color);
        }
    }

    public void deleteCategory(String categoryName) {
        categories.remove(categoryName);
    }

    public List<ColorModel> getCategoryColors(String categoryName) {
        List<ColorModel> categoryColors = categories.get(categoryName);
        return categoryColors != null ? new ArrayList<>(categoryColors) : new ArrayList<>();
    }

    public List<String> getCategoryNames() {
        return new ArrayList<>(categories.keySet());
    }

    public List<ColorModel> searchColors(String query) {
        List<ColorModel> results = new ArrayList<>();
        
        for (ColorModel color : favorites) {
            if (matchesQuery(color, query)) {
                results.add(color);
            }
        }
        
        for (List<ColorModel> categoryColors : categories.values()) {
            for (ColorModel color : categoryColors) {
                if (!results.contains(color) && matchesQuery(color, query)) {
                    results.add(color);
                }
            }
        }
        
        return results;
    }

    private boolean matchesQuery(ColorModel color, String query) {
        if (query == null || query.isEmpty()) {
            return true;
        }
        
        String lowerQuery = query.toLowerCase();
        
        if (color.getName() != null && color.getName().toLowerCase().contains(lowerQuery)) {
            return true;
        }
        
        String hex = color.toHEX().getValue().toLowerCase();
        if (hex.contains(lowerQuery.replace("#", ""))) {
            return true;
        }
        
        String rgb = String.format("%d,%d,%d", color.getRed(), color.getGreen(), color.getBlue());
        if (rgb.contains(lowerQuery)) {
            return true;
        }
        
        return false;
    }

    public String exportColors(List<ColorModel> colors, ExportFormat format) {
        switch (format) {
            case CSS:
                return exportAsCSS(colors);
            case SASS:
                return exportAsSASS(colors);
            case LESS:
                return exportAsLESS(colors);
            case JSON:
                return exportAsJSON(colors);
            case ANDROID:
                return exportAsAndroid(colors);
            case IOS:
                return exportAsiOS(colors);
            default:
                return exportAsCSS(colors);
        }
    }

    private String exportAsCSS(List<ColorModel> colors) {
        StringBuilder sb = new StringBuilder();
        sb.append("/* CSS Colors */\n");
        sb.append(":root {\n");
        for (int i = 0; i < colors.size(); i++) {
            ColorModel color = colors.get(i);
            String name = color.getName() != null ? color.getName() : "color-" + i;
            sb.append(String.format("  --%s: %s;\n", name, color.toHEX().toHexString()));
        }
        sb.append("}\n");
        return sb.toString();
    }

    private String exportAsSASS(List<ColorModel> colors) {
        StringBuilder sb = new StringBuilder();
        sb.append("// SASS Colors\n");
        for (int i = 0; i < colors.size(); i++) {
            ColorModel color = colors.get(i);
            String name = color.getName() != null ? color.getName() : "color-" + i;
            sb.append(String.format("$%s: %s;\n", name, color.toHEX().toHexString()));
        }
        return sb.toString();
    }

    private String exportAsLESS(List<ColorModel> colors) {
        StringBuilder sb = new StringBuilder();
        sb.append("// LESS Colors\n");
        for (int i = 0; i < colors.size(); i++) {
            ColorModel color = colors.get(i);
            String name = color.getName() != null ? color.getName() : "color-" + i;
            sb.append(String.format("@%s: %s;\n", name, color.toHEX().toHexString()));
        }
        return sb.toString();
    }

    private String exportAsJSON(List<ColorModel> colors) {
        StringBuilder sb = new StringBuilder();
        sb.append("{\n");
        sb.append("  \"colors\": [\n");
        for (int i = 0; i < colors.size(); i++) {
            ColorModel color = colors.get(i);
            String name = color.getName() != null ? color.getName() : "color-" + i;
            sb.append(String.format("    {\n"));
            sb.append(String.format("      \"name\": \"%s\",\n", name));
            sb.append(String.format("      \"hex\": \"%s\",\n", color.toHEX().toHexString()));
            sb.append(String.format("      \"rgb\": \"rgb(%d, %d, %d)\"\n", 
                    color.getRed(), color.getGreen(), color.getBlue()));
            sb.append(String.format("    }%s\n", i < colors.size() - 1 ? "," : ""));
        }
        sb.append("  ]\n");
        sb.append("}\n");
        return sb.toString();
    }

    private String exportAsAndroid(List<ColorModel> colors) {
        StringBuilder sb = new StringBuilder();
        sb.append("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n");
        sb.append("<resources>\n");
        for (int i = 0; i < colors.size(); i++) {
            ColorModel color = colors.get(i);
            String name = color.getName() != null ? color.getName().toLowerCase().replace(" ", "_") : "color_" + i;
            sb.append(String.format("    <color name=\"%s\">#%s</color>\n", 
                    name, RGBConverter.toAndroidColorString(color)));
        }
        sb.append("</resources>\n");
        return sb.toString();
    }

    private String exportAsiOS(List<ColorModel> colors) {
        StringBuilder sb = new StringBuilder();
        sb.append("// iOS Colors\n");
        sb.append("import UIKit\n\n");
        sb.append("extension UIColor {\n");
        for (int i = 0; i < colors.size(); i++) {
            ColorModel color = colors.get(i);
            String name = color.getName() != null ? toCamelCase(color.getName()) : "color" + i;
            sb.append(String.format("    static var %s: UIColor {\n", name));
            sb.append(String.format("        return UIColor(red: %.3f, green: %.3f, blue: %.3f, alpha: %.2f)\n",
                    color.getRed() / 255.0, color.getGreen() / 255.0, 
                    color.getBlue() / 255.0, color.getAlpha()));
            sb.append("    }\n");
        }
        sb.append("}\n");
        return sb.toString();
    }

    private String toCamelCase(String name) {
        if (name == null || name.isEmpty()) {
            return name;
        }
        String[] parts = name.split(" ");
        if (parts.length == 1) {
            return parts[0].toLowerCase();
        }
        StringBuilder sb = new StringBuilder();
        sb.append(parts[0].toLowerCase());
        for (int i = 1; i < parts.length; i++) {
            sb.append(parts[i].substring(0, 1).toUpperCase());
            sb.append(parts[i].substring(1).toLowerCase());
        }
        return sb.toString();
    }

    public enum ExportFormat {
        CSS,
        SASS,
        LESS,
        JSON,
        ANDROID,
        IOS
    }
}
