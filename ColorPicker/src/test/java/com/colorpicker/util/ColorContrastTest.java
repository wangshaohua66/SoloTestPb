package com.colorpicker.util;

import com.colorpicker.model.ColorModel;
import org.junit.Test;
import static org.junit.Assert.*;

public class ColorContrastTest {

    @Test
    public void testCalculateRelativeLuminance_Black() {
        ColorModel black = new ColorModel(0, 0, 0);
        double luminance = ColorContrast.calculateRelativeLuminance(black);
        
        assertEquals(0.0, luminance, 0.001);
    }

    @Test
    public void testCalculateRelativeLuminance_White() {
        ColorModel white = new ColorModel(255, 255, 255);
        double luminance = ColorContrast.calculateRelativeLuminance(white);
        
        assertEquals(1.0, luminance, 0.001);
    }

    @Test
    public void testCalculateRelativeLuminance_Red() {
        ColorModel red = new ColorModel(255, 0, 0);
        double luminance = ColorContrast.calculateRelativeLuminance(red);
        
        assertEquals(0.2126, luminance, 0.001);
    }

    @Test
    public void testCalculateRelativeLuminance_Green() {
        ColorModel green = new ColorModel(0, 255, 0);
        double luminance = ColorContrast.calculateRelativeLuminance(green);
        
        assertEquals(0.7152, luminance, 0.001);
    }

    @Test
    public void testCalculateRelativeLuminance_Blue() {
        ColorModel blue = new ColorModel(0, 0, 255);
        double luminance = ColorContrast.calculateRelativeLuminance(blue);
        
        assertEquals(0.0722, luminance, 0.001);
    }

    @Test
    public void testCalculateContrastRatio_BlackOnWhite() {
        ColorModel black = new ColorModel(0, 0, 0);
        ColorModel white = new ColorModel(255, 255, 255);
        
        double ratio = ColorContrast.calculateContrastRatio(black, white);
        
        assertEquals(21.0, ratio, 0.1);
    }

    @Test
    public void testCalculateContrastRatio_WhiteOnBlack() {
        ColorModel black = new ColorModel(0, 0, 0);
        ColorModel white = new ColorModel(255, 255, 255);
        
        double ratio = ColorContrast.calculateContrastRatio(white, black);
        
        assertEquals(21.0, ratio, 0.1);
    }

    @Test
    public void testCalculateContrastRatio_SameColor() {
        ColorModel color = new ColorModel(100, 150, 200);
        
        double ratio = ColorContrast.calculateContrastRatio(color, color);
        
        assertEquals(1.0, ratio, 0.001);
    }

    @Test
    public void testGetWCAGLevel_HighContrast_NormalText() {
        ColorModel black = new ColorModel(0, 0, 0);
        ColorModel white = new ColorModel(255, 255, 255);
        
        double ratio = ColorContrast.calculateContrastRatio(black, white);
        ColorContrast.WCAGLevel level = ColorContrast.getWCAGLevel(ratio, false);
        
        assertEquals(ColorContrast.WCAGLevel.AAA, level);
    }

    @Test
    public void testGetWCAGLevel_HighContrast_LargeText() {
        ColorModel black = new ColorModel(0, 0, 0);
        ColorModel white = new ColorModel(255, 255, 255);
        
        double ratio = ColorContrast.calculateContrastRatio(black, white);
        ColorContrast.WCAGLevel level = ColorContrast.getWCAGLevel(ratio, true);
        
        assertEquals(ColorContrast.WCAGLevel.AAA, level);
    }

    @Test
    public void testIsAccessible_HighContrast() {
        ColorModel black = new ColorModel(0, 0, 0);
        ColorModel white = new ColorModel(255, 255, 255);
        
        boolean accessible = ColorContrast.isAccessible(black, white, false);
        
        assertTrue(accessible);
    }

    @Test
    public void testIsAccessible_LowContrast() {
        ColorModel dark = new ColorModel(50, 50, 50);
        ColorModel darker = new ColorModel(30, 30, 30);
        
        boolean accessible = ColorContrast.isAccessible(dark, darker, false);
        
        assertFalse(accessible);
    }

    @Test
    public void testWCAGLevelEnum_Label() {
        assertEquals("Fail", ColorContrast.WCAGLevel.FAIL.getLabel());
        assertEquals("AA", ColorContrast.WCAGLevel.AA.getLabel());
        assertEquals("AAA", ColorContrast.WCAGLevel.AAA.getLabel());
    }
}
