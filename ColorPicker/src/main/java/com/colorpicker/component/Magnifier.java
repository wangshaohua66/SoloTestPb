package com.colorpicker.component;

import com.colorpicker.model.ColorModel;
import com.colorpicker.util.FXColorConverter;
import javafx.scene.canvas.Canvas;
import javafx.scene.canvas.GraphicsContext;
import javafx.scene.paint.Color;
import javafx.scene.shape.StrokeLineCap;

import java.awt.*;
import java.awt.image.BufferedImage;

public class Magnifier extends Canvas {

    private int zoomFactor = 8;
    private int magnifierSize = 150;
    private int gridSize = 1;
    private boolean showGrid = true;
    private boolean showCrosshair = true;
    
    private ColorModel currentColor = new ColorModel(0, 0, 0);
    private Point currentPosition = new Point(0, 0);
    private Robot robot;

    public Magnifier() {
        this(150, 150);
    }

    public Magnifier(double width, double height) {
        super(width, height);
        setWidth(width);
        setHeight(height);
        try {
            this.robot = new Robot();
        } catch (AWTException e) {
            e.printStackTrace();
        }
    }
    
    public void update() {
        Point location = MouseInfo.getPointerInfo().getLocation();
        updateFromScreen(location.x, location.y);
    }

    public void updateFromScreen(int screenX, int screenY) {
        if (robot == null) {
            return;
        }
        
        this.currentPosition = new Point(screenX, screenY);
        
        int captureSize = magnifierSize / zoomFactor;
        int halfCapture = captureSize / 2;
        
        Rectangle screenRect = new Rectangle(
                screenX - halfCapture,
                screenY - halfCapture,
                captureSize,
                captureSize
        );
        
        BufferedImage screenImage = robot.createScreenCapture(screenRect);
        
        int centerX = screenImage.getWidth() / 2;
        int centerY = screenImage.getHeight() / 2;
        int rgb = screenImage.getRGB(centerX, centerY);
        currentColor = new ColorModel(
                (rgb >> 16) & 0xFF,
                (rgb >> 8) & 0xFF,
                rgb & 0xFF
        );
        
        drawMagnifiedImage(screenImage);
    }

    private void drawMagnifiedImage(BufferedImage sourceImage) {
        GraphicsContext gc = getGraphicsContext2D();
        double width = getWidth();
        double height = getHeight();
        
        gc.clearRect(0, 0, width, height);
        
        int sourceWidth = sourceImage.getWidth();
        int sourceHeight = sourceImage.getHeight();
        
        for (int y = 0; y < sourceHeight; y++) {
            for (int x = 0; x < sourceWidth; x++) {
                int rgb = sourceImage.getRGB(x, y);
                int r = (rgb >> 16) & 0xFF;
                int g = (rgb >> 8) & 0xFF;
                int b = rgb & 0xFF;
                
                gc.setFill(Color.rgb(r, g, b));
                gc.fillRect(
                        x * zoomFactor,
                        y * zoomFactor,
                        zoomFactor,
                        zoomFactor
                );
            }
        }
        
        if (showGrid) {
            drawGrid(gc, sourceWidth, sourceHeight);
        }
        
        if (showCrosshair) {
            drawCrosshair(gc, sourceWidth, sourceHeight);
        }
        
        drawColorInfo(gc);
    }

    private void drawGrid(GraphicsContext gc, int sourceWidth, int sourceHeight) {
        gc.setStroke(Color.rgb(128, 128, 128, 0.5));
        gc.setLineWidth(0.5);
        
        for (int i = 0; i <= sourceWidth; i += gridSize) {
            double x = i * zoomFactor;
            gc.strokeLine(x, 0, x, sourceHeight * zoomFactor);
        }
        
        for (int i = 0; i <= sourceHeight; i += gridSize) {
            double y = i * zoomFactor;
            gc.strokeLine(0, y, sourceWidth * zoomFactor, y);
        }
    }

    private void drawCrosshair(GraphicsContext gc, int sourceWidth, int sourceHeight) {
        double centerX = (sourceWidth / 2.0) * zoomFactor;
        double centerY = (sourceHeight / 2.0) * zoomFactor;
        
        gc.setLineWidth(2);
        gc.setLineCap(StrokeLineCap.ROUND);
        
        gc.setStroke(Color.RED);
        gc.strokeRect(
                centerX - zoomFactor / 2.0,
                centerY - zoomFactor / 2.0,
                zoomFactor,
                zoomFactor
        );
        
        gc.setStroke(Color.WHITE);
        gc.setLineWidth(1);
        gc.strokeLine(centerX - zoomFactor, centerY, centerX - zoomFactor / 2.0 - 2, centerY);
        gc.strokeLine(centerX + zoomFactor / 2.0 + 2, centerY, centerX + zoomFactor, centerY);
        gc.strokeLine(centerX, centerY - zoomFactor, centerX, centerY - zoomFactor / 2.0 - 2);
        gc.strokeLine(centerX, centerY + zoomFactor / 2.0 + 2, centerX, centerY + zoomFactor);
    }

    private void drawColorInfo(GraphicsContext gc) {
        double width = getWidth();
        double height = getHeight();
        
        double infoHeight = 40;
        double infoY = height - infoHeight;
        
        gc.setFill(Color.rgb(0, 0, 0, 0.7));
        gc.fillRect(0, infoY, width, infoHeight);
        
        double colorBoxSize = 30;
        double colorBoxX = 5;
        double colorBoxY = infoY + 5;
        
        gc.setFill(FXColorConverter.toFXColor(currentColor));
        gc.fillRect(colorBoxX, colorBoxY, colorBoxSize, colorBoxSize);
        gc.setStroke(Color.WHITE);
        gc.setLineWidth(1);
        gc.strokeRect(colorBoxX, colorBoxY, colorBoxSize, colorBoxSize);
        
        gc.setFill(Color.WHITE);
        gc.setFont(javafx.scene.text.Font.font(11));
        
        String hexText = String.format("HEX: #%02X%02X%02X",
                currentColor.getRed(),
                currentColor.getGreen(),
                currentColor.getBlue());
        String rgbText = String.format("RGB: %d, %d, %d",
                currentColor.getRed(),
                currentColor.getGreen(),
                currentColor.getBlue());
        String posText = String.format("(%d, %d)",
                currentPosition.x,
                currentPosition.y);
        
        double textX = colorBoxX + colorBoxSize + 10;
        gc.fillText(hexText, textX, infoY + 15);
        gc.fillText(rgbText, textX, infoY + 30);
        gc.fillText(posText, width - 80, infoY + 22);
    }

    public ColorModel getCurrentColor() {
        return currentColor;
    }

    public Point getCurrentPosition() {
        return currentPosition;
    }

    public int getZoomFactor() {
        return zoomFactor;
    }

    public void setZoomFactor(int zoomFactor) {
        this.zoomFactor = Math.max(2, Math.min(32, zoomFactor));
    }

    public int getMagnifierSize() {
        return magnifierSize;
    }

    public void setMagnifierSize(int magnifierSize) {
        this.magnifierSize = magnifierSize;
        setWidth(magnifierSize);
        setHeight(magnifierSize);
    }

    public boolean isShowGrid() {
        return showGrid;
    }

    public void setShowGrid(boolean showGrid) {
        this.showGrid = showGrid;
    }

    public boolean isShowCrosshair() {
        return showCrosshair;
    }

    public void setShowCrosshair(boolean showCrosshair) {
        this.showCrosshair = showCrosshair;
    }
}
