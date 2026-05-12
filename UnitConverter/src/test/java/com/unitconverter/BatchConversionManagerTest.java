package com.unitconverter;

import com.unitconverter.manager.BatchConversionManager;
import com.unitconverter.model.ConversionHistory;
import com.unitconverter.model.UnitDefinition;
import com.unitconverter.model.UnitType;
import com.unitconverter.registry.UnitRegistry;
import org.junit.Before;
import org.junit.Test;

import java.util.ArrayList;
import java.util.List;

import static org.junit.Assert.*;

public class BatchConversionManagerTest {

    private BatchConversionManager batchManager;
    private UnitRegistry unitRegistry;

    @Before
    public void setUp() {
        batchManager = BatchConversionManager.getInstance();
        unitRegistry = UnitRegistry.getInstance();
        batchManager.clearHistory();
        batchManager.setDecimalPlaces(6);
        batchManager.setUseScientificNotation(false);
    }

    @Test
    public void testSingletonInstance() {
        BatchConversionManager instance1 = BatchConversionManager.getInstance();
        BatchConversionManager instance2 = BatchConversionManager.getInstance();
        assertSame(instance1, instance2);
    }

    @Test
    public void testConvertToAll() {
        UnitDefinition meter = unitRegistry.getUnit("length_meter");
        assertNotNull(meter);

        ConversionHistory history = batchManager.convertToAll(10.0, meter);

        assertNotNull(history);
        assertEquals(10.0, history.getInputValue(), 0.0001);
        assertEquals("米", history.getFromUnitName());
        assertEquals("m", history.getFromUnitSymbol());
        assertFalse(history.getResults().isEmpty());
        
        List<ConversionHistory> historyList = batchManager.getConversionHistory();
        assertEquals(1, historyList.size());
    }

    @Test
    public void testBatchConvert() {
        UnitDefinition meter = unitRegistry.getUnit("length_meter");
        UnitDefinition kilometer = unitRegistry.getUnit("length_kilometer");
        UnitDefinition centimeter = unitRegistry.getUnit("length_centimeter");

        assertNotNull(meter);
        assertNotNull(kilometer);
        assertNotNull(centimeter);

        List<Double> values = new ArrayList<>();
        values.add(1000.0);
        values.add(2000.0);
        values.add(500.0);

        List<UnitDefinition> toUnits = new ArrayList<>();
        toUnits.add(kilometer);
        toUnits.add(centimeter);

        List<ConversionHistory> results = batchManager.batchConvert(values, meter, toUnits);

        assertEquals(3, results.size());
        
        for (ConversionHistory h : results) {
            assertEquals(2, h.getResults().size());
        }

        ConversionHistory first = results.get(0);
        assertEquals(1000.0, first.getInputValue(), 0.0001);
        
        assertEquals(3, batchManager.getConversionHistory().size());
    }

    @Test
    public void testBatchConvertWithNullToUnits() {
        UnitDefinition meter = unitRegistry.getUnit("length_meter");
        assertNotNull(meter);

        List<Double> values = new ArrayList<>();
        values.add(10.0);

        List<ConversionHistory> results = batchManager.batchConvert(values, meter, null);

        assertEquals(1, results.size());
        assertFalse(results.get(0).getResults().isEmpty());
    }

    @Test(expected = IllegalArgumentException.class)
    public void testBatchConvertWithNullFromUnit() {
        List<Double> values = new ArrayList<>();
        values.add(10.0);
        batchManager.batchConvert(values, null, null);
    }

    @Test(expected = IllegalArgumentException.class)
    public void testBatchConvertWithEmptyValues() {
        UnitDefinition meter = unitRegistry.getUnit("length_meter");
        batchManager.batchConvert(new ArrayList<>(), meter, null);
    }

    @Test
    public void testConvertWithChain() {
        UnitDefinition meter = unitRegistry.getUnit("length_meter");
        UnitDefinition kilometer = unitRegistry.getUnit("length_kilometer");
        UnitDefinition centimeter = unitRegistry.getUnit("length_centimeter");

        List<UnitDefinition> chain = new ArrayList<>();
        chain.add(kilometer);
        chain.add(meter);
        chain.add(centimeter);

        ConversionHistory history = batchManager.convertWithChain(1.0, chain);

        assertNotNull(history);
        assertEquals(1.0, history.getInputValue(), 0.0001);
        assertEquals(1, history.getResults().size());
        assertTrue(history.getNote().contains("换算链"));
    }

    @Test(expected = IllegalArgumentException.class)
    public void testConvertWithChainTooFewUnits() {
        List<UnitDefinition> chain = new ArrayList<>();
        chain.add(unitRegistry.getUnit("length_meter"));
        batchManager.convertWithChain(1.0, chain);
    }

    @Test
    public void testHistoryManagement() {
        UnitDefinition meter = unitRegistry.getUnit("length_meter");

        batchManager.convertToAll(10.0, meter);
        batchManager.convertToAll(20.0, meter);
        batchManager.convertToAll(30.0, meter);

        List<ConversionHistory> history = batchManager.getConversionHistory();
        assertEquals(3, history.size());

        List<ConversionHistory> limitedHistory = batchManager.getConversionHistory(2);
        assertEquals(2, limitedHistory.size());

        batchManager.clearHistory();
        assertTrue(batchManager.getConversionHistory().isEmpty());
    }

    @Test
    public void testDecimalPlacesSettings() {
        batchManager.setDecimalPlaces(10);
        assertEquals(10, batchManager.getDecimalPlaces());

        batchManager.setDecimalPlaces(-1);
        assertEquals(0, batchManager.getDecimalPlaces());

        batchManager.setDecimalPlaces(20);
        assertEquals(15, batchManager.getDecimalPlaces());
    }

    @Test
    public void testScientificNotationSettings() {
        batchManager.setUseScientificNotation(true);
        assertTrue(batchManager.isUseScientificNotation());

        batchManager.setUseScientificNotation(false);
        assertFalse(batchManager.isUseScientificNotation());
    }

    @Test
    public void testExportFormats() {
        UnitDefinition meter = unitRegistry.getUnit("length_meter");

        batchManager.convertToAll(1000.0, meter);
        batchManager.convertToAll(2000.0, meter);

        List<ConversionHistory> history = batchManager.getConversionHistory();

        String csvExport = batchManager.formatForExport(history, "csv");
        assertFalse(csvExport.isEmpty());
        assertTrue(csvExport.contains(","));

        String jsonExport = batchManager.formatForExport(history, "json");
        assertFalse(jsonExport.isEmpty());
        assertTrue(jsonExport.contains("[") && jsonExport.contains("]"));

        String textExport = batchManager.formatForExport(history, "text");
        assertFalse(textExport.isEmpty());
    }

    @Test
    public void testWeightConversion() {
        UnitDefinition kilogram = unitRegistry.getUnit("weight_kilogram");
        UnitDefinition gram = unitRegistry.getUnit("weight_gram");
        UnitDefinition pound = unitRegistry.getUnit("weight_pound");

        List<Double> values = new ArrayList<>();
        values.add(1.0);
        values.add(2.5);

        List<UnitDefinition> toUnits = new ArrayList<>();
        toUnits.add(gram);
        toUnits.add(pound);

        List<ConversionHistory> results = batchManager.batchConvert(values, kilogram, toUnits);

        assertEquals(2, results.size());
        
        ConversionHistory first = results.get(0);
        assertEquals(1.0, first.getInputValue(), 0.0001);
        assertEquals(2, first.getResults().size());
    }

    @Test
    public void testTemperatureConversionWithBatch() {
        UnitDefinition celsius = unitRegistry.getUnit("temp_celsius");
        UnitDefinition fahrenheit = unitRegistry.getUnit("temp_fahrenheit");
        UnitDefinition kelvin = unitRegistry.getUnit("temp_kelvin");

        List<Double> values = new ArrayList<>();
        values.add(0.0);
        values.add(100.0);

        List<UnitDefinition> toUnits = new ArrayList<>();
        toUnits.add(fahrenheit);
        toUnits.add(kelvin);

        List<ConversionHistory> results = batchManager.batchConvert(values, celsius, toUnits);

        assertEquals(2, results.size());
        
        ConversionHistory first = results.get(0);
        assertEquals(0.0, first.getInputValue(), 0.0001);
    }
}
