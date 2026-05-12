package com.unitconverter;

import com.unitconverter.converter.ConversionEngine;
import com.unitconverter.converter.FormulaParser;
import com.unitconverter.model.UnitDefinition;
import com.unitconverter.model.UnitType;
import com.unitconverter.registry.UnitRegistry;
import org.junit.Before;
import org.junit.Test;

import static org.junit.Assert.*;

public class ConversionEngineTest {

    private UnitRegistry registry;

    @Before
    public void setUp() {
        registry = UnitRegistry.getInstance();
    }

    @Test
    public void testLengthConversion() {
        UnitDefinition meter = registry.getUnit("length_meter");
        UnitDefinition kilometer = registry.getUnit("length_kilometer");
        UnitDefinition foot = registry.getUnit("length_foot");

        assertNotNull(meter);
        assertNotNull(kilometer);
        assertNotNull(foot);

        double result = ConversionEngine.convert(1.0, meter, kilometer);
        assertEquals(0.001, result, 0.0001);

        result = ConversionEngine.convert(1.0, kilometer, meter);
        assertEquals(1000.0, result, 0.0001);

        result = ConversionEngine.convert(10.0, meter, foot);
        assertEquals(32.8084, result, 0.001);
    }

    @Test
    public void testWeightConversion() {
        UnitDefinition kg = registry.getUnit("weight_kilogram");
        UnitDefinition pound = registry.getUnit("weight_pound");
        UnitDefinition gram = registry.getUnit("weight_gram");

        assertNotNull(kg);
        assertNotNull(pound);
        assertNotNull(gram);

        double result = ConversionEngine.convert(1.0, kg, pound);
        assertEquals(2.20462, result, 0.001);

        result = ConversionEngine.convert(1.0, pound, kg);
        assertEquals(0.453592, result, 0.0001);

        result = ConversionEngine.convert(1.0, kg, gram);
        assertEquals(1000.0, result, 0.0001);
    }

    @Test
    public void testTemperatureConversion() {
        UnitDefinition celsius = registry.getUnit("temp_celsius");
        UnitDefinition fahrenheit = registry.getUnit("temp_fahrenheit");
        UnitDefinition kelvin = registry.getUnit("temp_kelvin");

        assertNotNull(celsius);
        assertNotNull(fahrenheit);
        assertNotNull(kelvin);

        double result = ConversionEngine.convert(0.0, celsius, fahrenheit);
        assertEquals(32.0, result, 0.0001);

        result = ConversionEngine.convert(100.0, celsius, fahrenheit);
        assertEquals(212.0, result, 0.0001);

        result = ConversionEngine.convert(32.0, fahrenheit, celsius);
        assertEquals(0.0, result, 0.0001);

        result = ConversionEngine.convert(0.0, celsius, kelvin);
        assertEquals(273.15, result, 0.0001);

        result = ConversionEngine.convert(273.15, kelvin, celsius);
        assertEquals(0.0, result, 0.0001);
    }

    @Test
    public void testAreaConversion() {
        UnitDefinition squareMeter = registry.getUnit("area_square_meter");
        UnitDefinition hectare = registry.getUnit("area_hectare");
        UnitDefinition squareKilometer = registry.getUnit("area_square_kilometer");

        assertNotNull(squareMeter);
        assertNotNull(hectare);
        assertNotNull(squareKilometer);

        double result = ConversionEngine.convert(10000.0, squareMeter, hectare);
        assertEquals(1.0, result, 0.0001);

        result = ConversionEngine.convert(1.0, squareKilometer, squareMeter);
        assertEquals(1000000.0, result, 0.0001);
    }

    @Test
    public void testVolumeConversion() {
        UnitDefinition cubicMeter = registry.getUnit("volume_cubic_meter");
        UnitDefinition liter = registry.getUnit("volume_liter");
        UnitDefinition gallonUK = registry.getUnit("volume_gallon_uk");

        assertNotNull(cubicMeter);
        assertNotNull(liter);
        assertNotNull(gallonUK);

        double result = ConversionEngine.convert(1.0, cubicMeter, liter);
        assertEquals(1000.0, result, 0.0001);

        result = ConversionEngine.convert(1000.0, liter, cubicMeter);
        assertEquals(1.0, result, 0.0001);
    }

    @Test
    public void testSpeedConversion() {
        UnitDefinition mps = registry.getUnit("speed_mps");
        UnitDefinition kph = registry.getUnit("speed_kph");
        UnitDefinition mph = registry.getUnit("speed_mph");

        assertNotNull(mps);
        assertNotNull(kph);
        assertNotNull(mph);

        double result = ConversionEngine.convert(1.0, mps, kph);
        assertEquals(3.6, result, 0.0001);

        result = ConversionEngine.convert(100.0, kph, mph);
        assertEquals(62.137, result, 0.01);
    }

    @Test
    public void testTimeConversion() {
        UnitDefinition second = registry.getUnit("time_second");
        UnitDefinition minute = registry.getUnit("time_minute");
        UnitDefinition hour = registry.getUnit("time_hour");
        UnitDefinition day = registry.getUnit("time_day");

        assertNotNull(second);
        assertNotNull(minute);
        assertNotNull(hour);
        assertNotNull(day);

        double result = ConversionEngine.convert(60.0, second, minute);
        assertEquals(1.0, result, 0.0001);

        result = ConversionEngine.convert(1.0, hour, second);
        assertEquals(3600.0, result, 0.0001);

        result = ConversionEngine.convert(1.0, day, hour);
        assertEquals(24.0, result, 0.0001);
    }

    @Test
    public void testDataStorageConversion() {
        UnitDefinition byteUnit = registry.getUnit("data_byte");
        UnitDefinition kilobyte = registry.getUnit("data_kilobyte");
        UnitDefinition megabyte = registry.getUnit("data_megabyte");
        UnitDefinition gigabyte = registry.getUnit("data_gigabyte");

        assertNotNull(byteUnit);
        assertNotNull(kilobyte);
        assertNotNull(megabyte);
        assertNotNull(gigabyte);

        double result = ConversionEngine.convert(1.0, kilobyte, byteUnit);
        assertEquals(1024.0, result, 0.0001);

        result = ConversionEngine.convert(1.0, megabyte, kilobyte);
        assertEquals(1024.0, result, 0.0001);

        result = ConversionEngine.convert(1.0, gigabyte, megabyte);
        assertEquals(1024.0, result, 0.0001);
    }

    @Test
    public void testPressureConversion() {
        UnitDefinition pascal = registry.getUnit("pressure_pascal");
        UnitDefinition bar = registry.getUnit("pressure_bar");
        UnitDefinition atmosphere = registry.getUnit("pressure_atmosphere");

        assertNotNull(pascal);
        assertNotNull(bar);
        assertNotNull(atmosphere);

        double result = ConversionEngine.convert(1.0, bar, pascal);
        assertEquals(100000.0, result, 0.0001);

        result = ConversionEngine.convert(1.0, atmosphere, pascal);
        assertEquals(101325.0, result, 0.0001);
    }

    @Test
    public void testPowerConversion() {
        UnitDefinition watt = registry.getUnit("power_watt");
        UnitDefinition kilowatt = registry.getUnit("power_kilowatt");
        UnitDefinition hpMetric = registry.getUnit("power_horsepower_metric");

        assertNotNull(watt);
        assertNotNull(kilowatt);
        assertNotNull(hpMetric);

        double result = ConversionEngine.convert(1.0, kilowatt, watt);
        assertEquals(1000.0, result, 0.0001);

        result = ConversionEngine.convert(1.0, hpMetric, watt);
        assertEquals(735.499, result, 0.01);
    }

    @Test
    public void testSameUnitConversion() {
        UnitDefinition meter = registry.getUnit("length_meter");
        double result = ConversionEngine.convert(100.0, meter, meter);
        assertEquals(100.0, result, 0.0001);
    }

    @Test(expected = IllegalArgumentException.class)
    public void testDifferentUnitTypeConversion() {
        UnitDefinition meter = registry.getUnit("length_meter");
        UnitDefinition kg = registry.getUnit("weight_kilogram");
        ConversionEngine.convert(1.0, meter, kg);
    }

    @Test
    public void testFormatResult() {
        String result = ConversionEngine.formatResult(123.456789, 4);
        assertEquals("123.4568", result);

        result = ConversionEngine.formatResult(123.456789, 2);
        assertEquals("123.46", result);

        result = ConversionEngine.formatResult(123.0, 4);
        assertEquals("123", result);
    }

    @Test
    public void testRound() {
        double result = ConversionEngine.round(123.456789, 4);
        assertEquals(123.4568, result, 0.0001);

        result = ConversionEngine.round(123.456789, 2);
        assertEquals(123.46, result, 0.001);
    }
}
