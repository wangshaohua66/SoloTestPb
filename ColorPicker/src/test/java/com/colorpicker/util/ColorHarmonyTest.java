package com.colorpicker.util;

import com.colorpicker.model.ColorModel;
import org.junit.Test;
import static org.junit.Assert.*;

import java.util.List;

public class ColorHarmonyTest {

    @Test
    public void testGetComplementaryColors_Size() {
        ColorModel base = new ColorModel(255, 0, 0);
        List<ColorModel> colors = ColorHarmony.getComplementaryColors(base);
        
        assertEquals(2, colors.size());
    }

    @Test
    public void testGetComplementaryColors_RedToCyan() {
        ColorModel red = new ColorModel(255, 0, 0);
        List<ColorModel> colors = ColorHarmony.getComplementaryColors(red);
        
        ColorModel complementary = colors.get(1);
        assertEquals(0, complementary.getRed());
        assertEquals(255, complementary.getGreen());
        assertEquals(255, complementary.getBlue());
    }

    @Test
    public void testGetAnalogousColors_Size() {
        ColorModel base = new ColorModel(255, 0, 0);
        List<ColorModel> colors = ColorHarmony.getAnalogousColors(base);
        
        assertEquals(3, colors.size());
    }

    @Test
    public void testGetAnalogousColors_WithCustomAngle() {
        ColorModel base = new ColorModel(255, 0, 0);
        List<ColorModel> colors = ColorHarmony.getAnalogousColors(base, 45);
        
        assertEquals(3, colors.size());
    }

    @Test
    public void testGetTriadicColors_Size() {
        ColorModel base = new ColorModel(255, 0, 0);
        List<ColorModel> colors = ColorHarmony.getTriadicColors(base);
        
        assertEquals(3, colors.size());
    }

    @Test
    public void testGetTetradicColors_Size() {
        ColorModel base = new ColorModel(255, 0, 0);
        List<ColorModel> colors = ColorHarmony.getTetradicColors(base);
        
        assertEquals(4, colors.size());
    }

    @Test
    public void testGetSplitComplementaryColors_Size() {
        ColorModel base = new ColorModel(255, 0, 0);
        List<ColorModel> colors = ColorHarmony.getSplitComplementaryColors(base);
        
        assertEquals(3, colors.size());
    }

    @Test
    public void testGetMonochromaticColors_Size() {
        ColorModel base = new ColorModel(255, 100, 50);
        List<ColorModel> colors = ColorHarmony.getMonochromaticColors(base);
        
        assertEquals(5, colors.size());
    }

    @Test
    public void testGetShades_Size() {
        ColorModel base = new ColorModel(255, 100, 50);
        int steps = 5;
        List<ColorModel> colors = ColorHarmony.getShades(base, steps);
        
        assertEquals(steps, colors.size());
    }

    @Test
    public void testGetShades_DecreasingValue() {
        ColorModel base = new ColorModel(255, 100, 50);
        List<ColorModel> colors = ColorHarmony.getShades(base, 5);
        
        for (int i = 1; i < colors.size(); i++) {
            ColorModel prev = colors.get(i - 1);
            ColorModel curr = colors.get(i);
            
            assertTrue(prev.getRed() >= curr.getRed());
            assertTrue(prev.getGreen() >= curr.getGreen());
            assertTrue(prev.getBlue() >= curr.getBlue());
        }
    }

    @Test
    public void testGetTints_Size() {
        ColorModel base = new ColorModel(255, 100, 50);
        int steps = 5;
        List<ColorModel> colors = ColorHarmony.getTints(base, steps);
        
        assertEquals(steps, colors.size());
    }

    @Test
    public void testGetTones_Size() {
        ColorModel base = new ColorModel(255, 100, 50);
        int steps = 5;
        List<ColorModel> colors = ColorHarmony.getTones(base, steps);
        
        assertEquals(steps, colors.size());
    }

    @Test
    public void testGetMonochromaticColors_SameHue() {
        ColorModel base = new ColorModel(255, 100, 50);
        List<ColorModel> colors = ColorHarmony.getMonochromaticColors(base);
        
        double baseHue = base.toHSV().getHue();
        for (ColorModel color : colors) {
            assertEquals(baseHue, color.toHSV().getHue(), 5.0);
        }
    }
}
