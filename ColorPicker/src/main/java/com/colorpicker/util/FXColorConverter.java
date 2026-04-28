package com.colorpicker.util;

import com.colorpicker.model.ColorModel;
import javafx.scene.paint.Color;

public class FXColorConverter {

    public static Color toFXColor(ColorModel color) {
        if (color == null) {
            return Color.BLACK;
        }
        return Color.rgb(
                color.getRed(),
                color.getGreen(),
                color.getBlue(),
                color.getAlpha()
        );
    }

    public static ColorModel fromFXColor(Color fxColor) {
        if (fxColor == null) {
            return new ColorModel(0, 0, 0);
        }
        return new ColorModel(
                (int) (fxColor.getRed() * 255),
                (int) (fxColor.getGreen() * 255),
                (int) (fxColor.getBlue() * 255),
                fxColor.getOpacity()
        );
    }
}
