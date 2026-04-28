package com.colorpicker.util;

import com.colorpicker.model.ColorModel;

import java.awt.AWTException;
import java.awt.Robot;
import java.awt.Point;
import java.awt.MouseInfo;
import java.awt.PointerInfo;
import java.awt.GraphicsEnvironment;
import java.awt.GraphicsDevice;
import java.awt.Rectangle;
import java.awt.image.BufferedImage;
import java.util.ArrayList;
import java.util.List;

public class ScreenPicker {
    private Robot robot;
    private List<ColorModel> colorHistory;
    private int maxHistorySize;
    private boolean isActive;

    public ScreenPicker() {
        this.colorHistory = new ArrayList<>();
        this.maxHistorySize = 20;
        this.isActive = false;
        try {
            this.robot = new Robot();
        } catch (AWTException e) {
            throw new RuntimeException("无法初始化屏幕取色器", e);
        }
    }

    public ColorModel pickColorAtCurrentMousePosition() {
        Point location = getMousePosition();
        return pickColorAt(location.x, location.y);
    }

    public ColorModel pickColorAt(int x, int y) {
        java.awt.Color awtColor = robot.getPixelColor(x, y);
        ColorModel color = ColorModel.fromAWTColor(awtColor);
        
        addToHistory(color);
        
        return color;
    }
    
    public void pickColor(ColorModel color) {
        addToHistory(color);
    }

    public BufferedImage captureScreenRegion(int x, int y, int width, int height) {
        Rectangle rect = new Rectangle(x, y, width, height);
        return robot.createScreenCapture(rect);
    }

    public BufferedImage captureAroundMouse(int size) {
        Point location = getMousePosition();
        int halfSize = size / 2;
        int x = location.x - halfSize;
        int y = location.y - halfSize;
        return captureScreenRegion(x, y, size, size);
    }

    public Point getMousePosition() {
        PointerInfo pointerInfo = MouseInfo.getPointerInfo();
        return pointerInfo.getLocation();
    }

    public ColorModel getAverageColor(BufferedImage image) {
        int width = image.getWidth();
        int height = image.getHeight();
        long sumR = 0, sumG = 0, sumB = 0;
        int pixelCount = width * height;

        for (int x = 0; x < width; x++) {
            for (int y = 0; y < height; y++) {
                int rgb = image.getRGB(x, y);
                sumR += (rgb >> 16) & 0xFF;
                sumG += (rgb >> 8) & 0xFF;
                sumB += rgb & 0xFF;
            }
        }

        int avgR = (int) (sumR / pixelCount);
        int avgG = (int) (sumG / pixelCount);
        int avgB = (int) (sumB / pixelCount);

        return new ColorModel(avgR, avgG, avgB);
    }

    public List<ColorModel> extractDominantColors(BufferedImage image, int numColors) {
        List<ColorModel> colors = new ArrayList<>();
        int width = image.getWidth();
        int height = image.getHeight();
        
        int[][] colorCounts = new int[256][256];
        
        for (int x = 0; x < width; x += 2) {
            for (int y = 0; y < height; y += 2) {
                int rgb = image.getRGB(x, y);
                int r = (rgb >> 16) & 0xFF;
                int g = (rgb >> 8) & 0xFF;
                int b = rgb & 0xFF;
                int hueBin = (r + g + b) / 3;
                int satBin = Math.max(Math.max(r, g), b) - Math.min(Math.min(r, g), b);
                colorCounts[hueBin][satBin]++;
            }
        }
        
        java.util.List<int[]> dominantBins = new java.util.ArrayList<>();
        for (int h = 0; h < 256; h++) {
            for (int s = 0; s < 256; s++) {
                if (colorCounts[h][s] > 0) {
                    dominantBins.add(new int[]{h, s, colorCounts[h][s]});
                }
            }
        }
        
        dominantBins.sort((a, b) -> Integer.compare(b[2], a[2]));
        
        for (int i = 0; i < Math.min(numColors, dominantBins.size()); i++) {
            int[] bin = dominantBins.get(i);
            int hue = bin[0];
            int sat = bin[1];
            int value = Math.min(255, hue + sat / 2);
            colors.add(new ColorModel(hue, (hue + sat) / 2, value));
        }
        
        return colors;
    }

    private void addToHistory(ColorModel color) {
        if (colorHistory.isEmpty() || !colorHistory.get(0).equals(color)) {
            colorHistory.add(0, color);
            if (colorHistory.size() > maxHistorySize) {
                colorHistory.remove(colorHistory.size() - 1);
            }
        }
    }

    public List<ColorModel> getColorHistory() {
        return new ArrayList<>(colorHistory);
    }

    public void clearHistory() {
        colorHistory.clear();
    }

    public int getMaxHistorySize() {
        return maxHistorySize;
    }

    public void setMaxHistorySize(int maxHistorySize) {
        this.maxHistorySize = maxHistorySize;
        while (colorHistory.size() > maxHistorySize) {
            colorHistory.remove(colorHistory.size() - 1);
        }
    }

    public boolean isActive() {
        return isActive;
    }

    public void setActive(boolean active) {
        isActive = active;
    }

    public GraphicsDevice[] getScreenDevices() {
        GraphicsEnvironment ge = GraphicsEnvironment.getLocalGraphicsEnvironment();
        return ge.getScreenDevices();
    }
}
