package com.colorpicker.component;

import com.colorpicker.model.ColorModel;
import com.colorpicker.model.HSV;
import com.colorpicker.util.FXColorConverter;
import javafx.scene.canvas.Canvas;
import javafx.scene.canvas.GraphicsContext;
import javafx.scene.input.MouseEvent;
import javafx.scene.paint.Color;
import javafx.scene.paint.CycleMethod;
import javafx.scene.paint.LinearGradient;
import javafx.scene.paint.Stop;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

public class ColorWheel extends Canvas {

    private double hue = 0.0;
    private double saturation = 1.0;
    private double value = 1.0;
    private double alpha = 1.0;
    
    private final double WHEEL_MARGIN = 10;
    private final double WHEEL_WIDTH_RATIO = 0.4;
    private final double SAT_VAL_MARGIN = 10;
    
    private List<Consumer<ColorModel>> colorChangeListeners = new ArrayList<>();
    
    private boolean isDraggingWheel = false;
    private boolean isDraggingSatVal = false;

    public ColorWheel() {
        this(300, 250);
    }

    public ColorWheel(double width, double height) {
        super(width, height);
        setWidth(width);
        setHeight(height);
        
        addEventFilter(MouseEvent.MOUSE_PRESSED, this::handleMousePressed);
        addEventFilter(MouseEvent.MOUSE_DRAGGED, this::handleMouseDragged);
        addEventFilter(MouseEvent.MOUSE_RELEASED, this::handleMouseReleased);
        
        widthProperty().addListener(obs -> draw());
        heightProperty().addListener(obs -> draw());
        
        draw();
    }

    public void setColor(ColorModel color) {
        HSV hsv = color.toHSV();
        this.hue = hsv.getHue();
        this.saturation = hsv.getSaturation();
        this.value = hsv.getValue();
        this.alpha = color.getAlpha();
        draw();
        notifyColorChange();
    }

    public ColorModel getColor() {
        return ColorModel.fromHSV(hue, saturation, value, alpha);
    }

    public void setHue(double hue) {
        this.hue = hue;
        draw();
        notifyColorChange();
    }

    public void setSaturation(double saturation) {
        this.saturation = saturation;
        draw();
        notifyColorChange();
    }

    public void setValue(double value) {
        this.value = value;
        draw();
        notifyColorChange();
    }

    public void setAlpha(double alpha) {
        this.alpha = alpha;
        draw();
        notifyColorChange();
    }

    public double getHue() {
        return hue;
    }

    public double getSaturation() {
        return saturation;
    }

    public double getValue() {
        return value;
    }

    public double getAlpha() {
        return alpha;
    }

    public void addColorChangeListener(Consumer<ColorModel> listener) {
        colorChangeListeners.add(listener);
    }

    public void removeColorChangeListener(Consumer<ColorModel> listener) {
        colorChangeListeners.remove(listener);
    }

    private void notifyColorChange() {
        ColorModel color = getColor();
        for (Consumer<ColorModel> listener : colorChangeListeners) {
            listener.accept(color);
        }
    }

    private void draw() {
        GraphicsContext gc = getGraphicsContext2D();
        double width = getWidth();
        double height = getHeight();
        
        gc.clearRect(0, 0, width, height);
        
        double wheelCenterX = WHEEL_MARGIN + (width * WHEEL_WIDTH_RATIO) / 2;
        double wheelCenterY = height / 2;
        double wheelRadius = Math.min(width * WHEEL_WIDTH_RATIO / 2 - WHEEL_MARGIN, height / 2 - WHEEL_MARGIN);
        double wheelInnerRadius = wheelRadius * 0.6;
        
        drawHueWheel(gc, wheelCenterX, wheelCenterY, wheelRadius, wheelInnerRadius);
        drawHueSelector(gc, wheelCenterX, wheelCenterY, wheelInnerRadius + (wheelRadius - wheelInnerRadius) / 2);
        
        double satValX = width * WHEEL_WIDTH_RATIO + SAT_VAL_MARGIN;
        double satValY = WHEEL_MARGIN;
        double satValWidth = width - satValX - SAT_VAL_MARGIN;
        double satValHeight = height - 2 * WHEEL_MARGIN;
        
        drawSatValRectangle(gc, satValX, satValY, satValWidth, satValHeight);
        drawSatValSelector(gc, satValX, satValY, satValWidth, satValHeight);
    }

    private void drawHueWheel(GraphicsContext gc, double centerX, double centerY, 
                               double outerRadius, double innerRadius) {
        int segments = 360;
        double angleStep = 2 * Math.PI / segments;
        
        for (int i = 0; i < segments; i++) {
            double angle1 = i * angleStep;
            double angle2 = (i + 1) * angleStep;
            
            double hueDegrees = (i / (double) segments) * 360;
            Color color = Color.hsb(hueDegrees, 1.0, 1.0);
            
            gc.setFill(color);
            gc.beginPath();
            gc.moveTo(centerX + innerRadius * Math.cos(angle1), 
                      centerY + innerRadius * Math.sin(angle1));
            gc.lineTo(centerX + outerRadius * Math.cos(angle1), 
                      centerY + outerRadius * Math.sin(angle1));
            gc.lineTo(centerX + outerRadius * Math.cos(angle2), 
                      centerY + outerRadius * Math.sin(angle2));
            gc.lineTo(centerX + innerRadius * Math.cos(angle2), 
                      centerY + innerRadius * Math.sin(angle2));
            gc.closePath();
            gc.fill();
        }
        
        gc.setStroke(Color.BLACK);
        gc.setLineWidth(1);
        gc.strokeOval(centerX - outerRadius, centerY - outerRadius, 
                       2 * outerRadius, 2 * outerRadius);
        gc.strokeOval(centerX - innerRadius, centerY - innerRadius, 
                       2 * innerRadius, 2 * innerRadius);
    }

    private void drawHueSelector(GraphicsContext gc, double centerX, double centerY, double radius) {
        double angle = Math.toRadians(hue);
        double selectorX = centerX + radius * Math.cos(angle);
        double selectorY = centerY + radius * Math.sin(angle);
        
        double selectorRadius = 8;
        gc.setFill(Color.WHITE);
        gc.setStroke(Color.BLACK);
        gc.setLineWidth(2);
        gc.fillOval(selectorX - selectorRadius, selectorY - selectorRadius, 
                     2 * selectorRadius, 2 * selectorRadius);
        gc.strokeOval(selectorX - selectorRadius, selectorY - selectorRadius, 
                       2 * selectorRadius, 2 * selectorRadius);
    }

    private void drawSatValRectangle(GraphicsContext gc, double x, double y, double width, double height) {
        Color currentHueColor = Color.hsb(hue, 1.0, 1.0);
        
        LinearGradient satGradient = new LinearGradient(x, y, x + width, y, false, 
                CycleMethod.NO_CYCLE,
                new Stop(0, Color.WHITE),
                new Stop(1, currentHueColor));
        gc.setFill(satGradient);
        gc.fillRect(x, y, width, height);
        
        LinearGradient valGradient = new LinearGradient(x, y, x, y + height, false,
                CycleMethod.NO_CYCLE,
                new Stop(0, Color.TRANSPARENT),
                new Stop(1, Color.BLACK));
        gc.setFill(valGradient);
        gc.fillRect(x, y, width, height);
        
        gc.setStroke(Color.BLACK);
        gc.setLineWidth(1);
        gc.strokeRect(x, y, width, height);
    }

    private void drawSatValSelector(GraphicsContext gc, double x, double y, double width, double height) {
        double selectorX = x + saturation * width;
        double selectorY = y + (1 - value) * height;
        
        double selectorRadius = 6;
        
        gc.setFill(Color.WHITE);
        gc.setStroke(Color.BLACK);
        gc.setLineWidth(2);
        gc.fillOval(selectorX - selectorRadius, selectorY - selectorRadius,
                     2 * selectorRadius, 2 * selectorRadius);
        gc.strokeOval(selectorX - selectorRadius, selectorY - selectorRadius,
                       2 * selectorRadius, 2 * selectorRadius);
        
        gc.setStroke(Color.WHITE);
        gc.setLineWidth(1);
        gc.strokeOval(selectorX - (selectorRadius - 2), selectorY - (selectorRadius - 2),
                       2 * (selectorRadius - 2), 2 * (selectorRadius - 2));
    }

    private void handleMousePressed(MouseEvent event) {
        double x = event.getX();
        double y = event.getY();
        
        double width = getWidth();
        double height = getHeight();
        
        double wheelCenterX = WHEEL_MARGIN + (width * WHEEL_WIDTH_RATIO) / 2;
        double wheelCenterY = height / 2;
        double wheelRadius = Math.min(width * WHEEL_WIDTH_RATIO / 2 - WHEEL_MARGIN, height / 2 - WHEEL_MARGIN);
        double wheelInnerRadius = wheelRadius * 0.6;
        
        double dx = x - wheelCenterX;
        double dy = y - wheelCenterY;
        double distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance >= wheelInnerRadius && distance <= wheelRadius) {
            isDraggingWheel = true;
            updateHueFromPosition(x, y);
            event.consume();
            return;
        }
        
        double satValX = width * WHEEL_WIDTH_RATIO + SAT_VAL_MARGIN;
        double satValY = WHEEL_MARGIN;
        double satValWidth = width - satValX - SAT_VAL_MARGIN;
        double satValHeight = height - 2 * WHEEL_MARGIN;
        
        if (x >= satValX && x <= satValX + satValWidth &&
            y >= satValY && y <= satValY + satValHeight) {
            isDraggingSatVal = true;
            updateSatValFromPosition(x, y, satValX, satValY, satValWidth, satValHeight);
            event.consume();
        }
    }

    private void handleMouseDragged(MouseEvent event) {
        double x = event.getX();
        double y = event.getY();
        
        double width = getWidth();
        double height = getHeight();
        
        if (isDraggingWheel) {
            updateHueFromPosition(x, y);
            event.consume();
        } else if (isDraggingSatVal) {
            double satValX = width * WHEEL_WIDTH_RATIO + SAT_VAL_MARGIN;
            double satValY = WHEEL_MARGIN;
            double satValWidth = width - satValX - SAT_VAL_MARGIN;
            double satValHeight = height - 2 * WHEEL_MARGIN;
            
            updateSatValFromPosition(x, y, satValX, satValY, satValWidth, satValHeight);
            event.consume();
        }
    }

    private void handleMouseReleased(MouseEvent event) {
        isDraggingWheel = false;
        isDraggingSatVal = false;
    }

    private void updateHueFromPosition(double x, double y) {
        double width = getWidth();
        double height = getHeight();
        
        double wheelCenterX = WHEEL_MARGIN + (width * WHEEL_WIDTH_RATIO) / 2;
        double wheelCenterY = height / 2;
        
        double dx = x - wheelCenterX;
        double dy = y - wheelCenterY;
        
        double angle = Math.toDegrees(Math.atan2(dy, dx));
        if (angle < 0) {
            angle += 360;
        }
        
        hue = angle;
        draw();
        notifyColorChange();
    }

    private void updateSatValFromPosition(double x, double y, 
                                            double rectX, double rectY, 
                                            double rectWidth, double rectHeight) {
        double clampedX = Math.max(rectX, Math.min(rectX + rectWidth, x));
        double clampedY = Math.max(rectY, Math.min(rectY + rectHeight, y));
        
        saturation = (clampedX - rectX) / rectWidth;
        value = 1.0 - (clampedY - rectY) / rectHeight;
        
        draw();
        notifyColorChange();
    }
}
