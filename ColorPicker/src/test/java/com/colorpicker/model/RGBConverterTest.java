package com.colorpicker.model;

import org.junit.Test;
import static org.junit.Assert.*;

public class RGBConverterTest {

    @Test
    public void testRGBToHSV_Black() {
        ColorModel black = new ColorModel(0, 0, 0);
        HSV hsv = RGBConverter.toHSV(black);
        
        assertEquals(0.0, hsv.getHue(), 0.1);
        assertEquals(0.0, hsv.getSaturation(), 0.001);
        assertEquals(0.0, hsv.getValue(), 0.001);
    }

    @Test
    public void testRGBToHSV_White() {
        ColorModel white = new ColorModel(255, 255, 255);
        HSV hsv = RGBConverter.toHSV(white);
        
        assertEquals(0.0, hsv.getHue(), 0.1);
        assertEquals(0.0, hsv.getSaturation(), 0.001);
        assertEquals(1.0, hsv.getValue(), 0.001);
    }

    @Test
    public void testRGBToHSV_Red() {
        ColorModel red = new ColorModel(255, 0, 0);
        HSV hsv = RGBConverter.toHSV(red);
        
        assertEquals(0.0, hsv.getHue(), 0.1);
        assertEquals(1.0, hsv.getSaturation(), 0.001);
        assertEquals(1.0, hsv.getValue(), 0.001);
    }

    @Test
    public void testRGBToHSV_Green() {
        ColorModel green = new ColorModel(0, 255, 0);
        HSV hsv = RGBConverter.toHSV(green);
        
        assertEquals(120.0, hsv.getHue(), 0.1);
        assertEquals(1.0, hsv.getSaturation(), 0.001);
        assertEquals(1.0, hsv.getValue(), 0.001);
    }

    @Test
    public void testRGBToHSV_Blue() {
        ColorModel blue = new ColorModel(0, 0, 255);
        HSV hsv = RGBConverter.toHSV(blue);
        
        assertEquals(240.0, hsv.getHue(), 0.1);
        assertEquals(1.0, hsv.getSaturation(), 0.001);
        assertEquals(1.0, hsv.getValue(), 0.001);
    }

    @Test
    public void testHSVToRGB_Red() {
        ColorModel color = RGBConverter.fromHSV(0.0, 1.0, 1.0);
        
        assertEquals(255, color.getRed());
        assertEquals(0, color.getGreen());
        assertEquals(0, color.getBlue());
    }

    @Test
    public void testHSVToRGB_Green() {
        ColorModel color = RGBConverter.fromHSV(120.0, 1.0, 1.0);
        
        assertEquals(0, color.getRed());
        assertEquals(255, color.getGreen());
        assertEquals(0, color.getBlue());
    }

    @Test
    public void testHSVToRGB_Blue() {
        ColorModel color = RGBConverter.fromHSV(240.0, 1.0, 1.0);
        
        assertEquals(0, color.getRed());
        assertEquals(0, color.getGreen());
        assertEquals(255, color.getBlue());
    }

    @Test
    public void testHSVToRGB_RoundTrip() {
        ColorModel original = new ColorModel(100, 150, 200);
        HSV hsv = RGBConverter.toHSV(original);
        ColorModel converted = RGBConverter.fromHSV(hsv.getHue(), hsv.getSaturation(), hsv.getValue());
        
        assertEquals(original.getRed(), converted.getRed());
        assertEquals(original.getGreen(), converted.getGreen());
        assertEquals(original.getBlue(), converted.getBlue());
    }

    @Test
    public void testRGBToHEX() {
        ColorModel red = new ColorModel(255, 0, 0);
        HEX hex = RGBConverter.toHEX(red);
        
        assertEquals("FF0000", hex.getValue());
    }

    @Test
    public void testHEXToRGB() {
        ColorModel color = RGBConverter.fromHEX("#FF0000");
        
        assertEquals(255, color.getRed());
        assertEquals(0, color.getGreen());
        assertEquals(0, color.getBlue());
    }

    @Test
    public void testHEXToRGB_ShortForm() {
        ColorModel color = RGBConverter.fromHEX("#F00");
        
        assertEquals(255, color.getRed());
        assertEquals(0, color.getGreen());
        assertEquals(0, color.getBlue());
    }

    @Test
    public void testHEXToRGB_WithoutHash() {
        ColorModel color = RGBConverter.fromHEX("00FF00");
        
        assertEquals(0, color.getRed());
        assertEquals(255, color.getGreen());
        assertEquals(0, color.getBlue());
    }

    @Test
    public void testToCSSString() {
        ColorModel color = new ColorModel(100, 150, 200);
        String css = RGBConverter.toCSSString(color);
        
        assertEquals("rgb(100, 150, 200)", css);
    }

    @Test
    public void testToCSSString_WithAlpha() {
        ColorModel color = new ColorModel(100, 150, 200, 0.5);
        String css = RGBConverter.toCSSString(color);
        
        assertTrue(css.startsWith("rgba("));
        assertTrue(css.contains("100"));
        assertTrue(css.contains("150"));
        assertTrue(css.contains("200"));
        assertTrue(css.contains("0.50"));
    }

    @Test
    public void testToAndroidColorString() {
        ColorModel color = new ColorModel(100, 150, 200, 1.0);
        String android = RGBConverter.toAndroidColorString(color);
        
        assertEquals("FF6496C8", android);
    }

    @Test
    public void testToiOSColorString() {
        ColorModel color = new ColorModel(100, 150, 200, 0.8);
        String ios = RGBConverter.toiOSColorString(color);
        
        assertTrue(ios.contains("UIColor"));
        assertTrue(ios.contains("0.392"));
        assertTrue(ios.contains("0.588"));
        assertTrue(ios.contains("0.784"));
        assertTrue(ios.contains("0.80"));
    }

    @Test(expected = IllegalArgumentException.class)
    public void testFromHEX_Invalid() {
        RGBConverter.fromHEX("invalid");
    }
}
