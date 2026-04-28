package com.colorpicker.model;

import org.junit.Test;
import static org.junit.Assert.*;

public class ColorModelTest {

    @Test
    public void testDefaultConstructor() {
        ColorModel color = new ColorModel();
        assertEquals(0, color.getRed());
        assertEquals(0, color.getGreen());
        assertEquals(0, color.getBlue());
        assertEquals(1.0, color.getAlpha(), 0.001);
    }

    @Test
    public void testRGBConstructor() {
        ColorModel color = new ColorModel(100, 150, 200);
        assertEquals(100, color.getRed());
        assertEquals(150, color.getGreen());
        assertEquals(200, color.getBlue());
        assertEquals(1.0, color.getAlpha(), 0.001);
    }

    @Test
    public void testRGBAConstructor() {
        ColorModel color = new ColorModel(100, 150, 200, 0.5);
        assertEquals(100, color.getRed());
        assertEquals(150, color.getGreen());
        assertEquals(200, color.getBlue());
        assertEquals(0.5, color.getAlpha(), 0.001);
    }

    @Test
    public void testClampValues() {
        ColorModel color = new ColorModel(300, -50, 256, 2.0);
        assertEquals(255, color.getRed());
        assertEquals(0, color.getGreen());
        assertEquals(255, color.getBlue());
        assertEquals(1.0, color.getAlpha(), 0.001);
    }

    @Test
    public void testSetters() {
        ColorModel color = new ColorModel();
        color.setRed(100);
        color.setGreen(150);
        color.setBlue(200);
        color.setAlpha(0.75);

        assertEquals(100, color.getRed());
        assertEquals(150, color.getGreen());
        assertEquals(200, color.getBlue());
        assertEquals(0.75, color.getAlpha(), 0.001);
    }

    @Test
    public void testFromRGBStaticMethod() {
        ColorModel color = ColorModel.fromRGB(50, 100, 150);
        assertEquals(50, color.getRed());
        assertEquals(100, color.getGreen());
        assertEquals(150, color.getBlue());
    }

    @Test
    public void testFromRGBStaticMethodWithAlpha() {
        ColorModel color = ColorModel.fromRGB(50, 100, 150, 0.6);
        assertEquals(50, color.getRed());
        assertEquals(100, color.getGreen());
        assertEquals(150, color.getBlue());
        assertEquals(0.6, color.getAlpha(), 0.001);
    }

    @Test
    public void testEquals() {
        ColorModel color1 = new ColorModel(100, 150, 200, 0.8);
        ColorModel color2 = new ColorModel(100, 150, 200, 0.8);
        ColorModel color3 = new ColorModel(100, 150, 200, 0.9);

        assertTrue(color1.equals(color2));
        assertFalse(color1.equals(color3));
        assertFalse(color1.equals(null));
        assertFalse(color1.equals("not a color"));
    }

    @Test
    public void testHashCode() {
        ColorModel color1 = new ColorModel(100, 150, 200, 0.8);
        ColorModel color2 = new ColorModel(100, 150, 200, 0.8);

        assertEquals(color1.hashCode(), color2.hashCode());
    }

    @Test
    public void testToString() {
        ColorModel color = new ColorModel(100, 150, 200, 0.8);
        String str = color.toString();
        assertTrue(str.contains("100"));
        assertTrue(str.contains("150"));
        assertTrue(str.contains("200"));
        assertTrue(str.contains("0.8"));
    }

    @Test
    public void testToRGB() {
        ColorModel color = new ColorModel(100, 150, 200, 0.8);
        RGB rgb = color.toRGB();
        assertEquals(100, rgb.getRed());
        assertEquals(150, rgb.getGreen());
        assertEquals(200, rgb.getBlue());
        assertEquals(0.8, rgb.getAlpha(), 0.001);
    }

    @Test
    public void testNameProperty() {
        ColorModel color = new ColorModel(255, 0, 0);
        assertNull(color.getName());
        
        color.setName("Red");
        assertEquals("Red", color.getName());
    }
}
