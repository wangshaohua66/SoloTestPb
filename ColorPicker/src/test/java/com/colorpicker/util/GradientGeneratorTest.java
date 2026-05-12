package com.colorpicker.util;

import com.colorpicker.model.ColorModel;
import org.junit.Test;
import static org.junit.Assert.*;

import java.util.ArrayList;
import java.util.List;

public class GradientGeneratorTest {

    @Test
    public void testGenerateLinearGradient_Size() {
        ColorModel start = new ColorModel(255, 0, 0);
        ColorModel end = new ColorModel(0, 0, 255);
        int steps = 10;
        
        List<ColorModel> gradient = GradientGenerator.generateLinearGradient(start, end, steps);
        
        assertEquals(steps, gradient.size());
    }

    @Test
    public void testGenerateLinearGradient_StartAndEnd() {
        ColorModel start = new ColorModel(255, 0, 0);
        ColorModel end = new ColorModel(0, 0, 255);
        
        List<ColorModel> gradient = GradientGenerator.generateLinearGradient(start, end, 5);
        
        assertEquals(start.getRed(), gradient.get(0).getRed());
        assertEquals(start.getGreen(), gradient.get(0).getGreen());
        assertEquals(start.getBlue(), gradient.get(0).getBlue());
        
        assertEquals(end.getRed(), gradient.get(gradient.size() - 1).getRed());
        assertEquals(end.getGreen(), gradient.get(gradient.size() - 1).getGreen());
        assertEquals(end.getBlue(), gradient.get(gradient.size() - 1).getBlue());
    }

    @Test
    public void testGenerateLinearGradient_Interpolation() {
        ColorModel start = new ColorModel(0, 0, 0);
        ColorModel end = new ColorModel(100, 100, 100);
        int steps = 11;
        
        List<ColorModel> gradient = GradientGenerator.generateLinearGradient(start, end, steps);
        
        for (int i = 0; i < steps; i++) {
            ColorModel color = gradient.get(i);
            int expected = i * 10;
            assertEquals(expected, color.getRed());
            assertEquals(expected, color.getGreen());
            assertEquals(expected, color.getBlue());
        }
    }

    @Test
    public void testGenerateLinearGradient_WithAlpha() {
        ColorModel start = new ColorModel(255, 0, 0, 0.0);
        ColorModel end = new ColorModel(255, 0, 0, 1.0);
        
        List<ColorModel> gradient = GradientGenerator.generateLinearGradient(start, end, 11);
        
        for (int i = 0; i < 11; i++) {
            assertEquals(i * 0.1, gradient.get(i).getAlpha(), 0.001);
        }
    }

    @Test
    public void testGenerateMultiStopGradient_Size() {
        List<ColorModel> colors = new ArrayList<>();
        colors.add(new ColorModel(255, 0, 0));
        colors.add(new ColorModel(0, 255, 0));
        colors.add(new ColorModel(0, 0, 255));
        int steps = 10;
        
        List<ColorModel> gradient = GradientGenerator.generateMultiStopGradient(colors, null, steps);
        
        assertEquals(steps, gradient.size());
    }

    @Test(expected = IllegalArgumentException.class)
    public void testGenerateMultiStopGradient_NotEnoughColors() {
        List<ColorModel> colors = new ArrayList<>();
        colors.add(new ColorModel(255, 0, 0));
        
        GradientGenerator.generateMultiStopGradient(colors, null, 10);
    }

    @Test(expected = IllegalArgumentException.class)
    public void testGenerateMultiStopGradient_StopsMismatch() {
        List<ColorModel> colors = new ArrayList<>();
        colors.add(new ColorModel(255, 0, 0));
        colors.add(new ColorModel(0, 0, 255));
        
        List<Double> stops = new ArrayList<>();
        stops.add(0.0);
        
        GradientGenerator.generateMultiStopGradient(colors, stops, 10);
    }

    @Test
    public void testGenerateMultiStopGradient_WithCustomStops() {
        List<ColorModel> colors = new ArrayList<>();
        colors.add(new ColorModel(255, 0, 0));
        colors.add(new ColorModel(0, 255, 0));
        colors.add(new ColorModel(0, 0, 255));
        
        List<Double> stops = new ArrayList<>();
        stops.add(0.0);
        stops.add(0.3);
        stops.add(1.0);
        
        List<ColorModel> gradient = GradientGenerator.generateMultiStopGradient(colors, stops, 10);
        
        assertEquals(10, gradient.size());
    }

    @Test
    public void testGenerateCSSLinearGradient() {
        List<ColorModel> colors = new ArrayList<>();
        colors.add(new ColorModel(255, 0, 0));
        colors.add(new ColorModel(0, 0, 255));
        
        String css = GradientGenerator.generateCSSLinearGradient(colors, "to right");
        
        assertTrue(css.contains("linear-gradient"));
        assertTrue(css.contains("to right"));
        assertTrue(css.contains("rgb(255, 0, 0)"));
        assertTrue(css.contains("rgb(0, 0, 255)"));
    }

    @Test
    public void testGenerateCSSLinearGradient_NoDirection() {
        List<ColorModel> colors = new ArrayList<>();
        colors.add(new ColorModel(255, 0, 0));
        colors.add(new ColorModel(0, 0, 255));
        
        String css = GradientGenerator.generateCSSLinearGradient(colors, null);
        
        assertTrue(css.contains("linear-gradient"));
        assertFalse(css.contains("to right"));
    }

    @Test
    public void testGenerateCSSRadialGradient() {
        List<ColorModel> colors = new ArrayList<>();
        colors.add(new ColorModel(255, 255, 255));
        colors.add(new ColorModel(0, 0, 0));
        
        String css = GradientGenerator.generateCSSRadialGradient(colors, "circle", "farthest-corner");
        
        assertTrue(css.contains("radial-gradient"));
        assertTrue(css.contains("circle"));
        assertTrue(css.contains("farthest-corner"));
    }

    @Test
    public void testGenerateHueGradient_Size() {
        int steps = 10;
        List<ColorModel> gradient = GradientGenerator.generateHueGradient(steps);
        
        assertEquals(steps, gradient.size());
    }

    @Test
    public void testGenerateHueGradient_FullSaturationAndValue() {
        List<ColorModel> gradient = GradientGenerator.generateHueGradient(10);
        
        for (ColorModel color : gradient) {
            assertEquals(1.0, color.toHSV().getSaturation(), 0.001);
            assertEquals(1.0, color.toHSV().getValue(), 0.001);
        }
    }

    @Test
    public void testGenerateSaturationGradient_Size() {
        int steps = 10;
        List<ColorModel> gradient = GradientGenerator.generateSaturationGradient(0.0, 1.0, steps);
        
        assertEquals(steps, gradient.size());
    }

    @Test
    public void testGenerateValueGradient_Size() {
        int steps = 10;
        List<ColorModel> gradient = GradientGenerator.generateValueGradient(0.0, 1.0, steps);
        
        assertEquals(steps, gradient.size());
    }
}
