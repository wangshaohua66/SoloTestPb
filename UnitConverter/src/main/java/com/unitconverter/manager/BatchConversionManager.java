package com.unitconverter.manager;

import com.unitconverter.converter.ConversionEngine;
import com.unitconverter.model.ConversionHistory;
import com.unitconverter.model.ConversionResult;
import com.unitconverter.model.UnitDefinition;
import com.unitconverter.model.UnitType;
import com.unitconverter.registry.UnitRegistry;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class BatchConversionManager {
    private static BatchConversionManager instance;
    private final List<ConversionHistory> conversionHistory;
    private int decimalPlaces;
    private boolean useScientificNotation;

    private BatchConversionManager() {
        conversionHistory = new ArrayList<>();
        decimalPlaces = 6;
        useScientificNotation = false;
    }

    public static synchronized BatchConversionManager getInstance() {
        if (instance == null) {
            instance = new BatchConversionManager();
        }
        return instance;
    }

    public ConversionHistory convertToAll(double value, UnitDefinition fromUnit) {
        if (fromUnit == null) {
            throw new IllegalArgumentException("源单位不能为空");
        }

        UnitType unitType = fromUnit.getUnitType();
        List<UnitDefinition> allUnits = UnitRegistry.getInstance().getUnitsByType(unitType);

        ConversionHistory history = new ConversionHistory(value, fromUnit);
        history.setId(UUID.randomUUID().toString());

        for (UnitDefinition toUnit : allUnits) {
            if (toUnit.getId().equals(fromUnit.getId())) {
                continue;
            }

            try {
                double result = ConversionEngine.convert(value, fromUnit, toUnit);
                String formatted = ConversionEngine.formatResult(result, decimalPlaces, useScientificNotation);

                ConversionResult conversionResult = new ConversionResult(toUnit, result);
                conversionResult.setFormattedResult(formatted + " " + toUnit.getSymbol());
                history.addResult(conversionResult);
            } catch (Exception e) {
            }
        }

        conversionHistory.add(0, history);
        return history;
    }

    public List<ConversionHistory> batchConvert(List<Double> values, UnitDefinition fromUnit, List<UnitDefinition> toUnits) {
        if (fromUnit == null || values == null || values.isEmpty()) {
            throw new IllegalArgumentException("参数不能为空");
        }

        List<ConversionHistory> results = new ArrayList<>();

        for (Double value : values) {
            if (value == null) {
                continue;
            }

            ConversionHistory history = new ConversionHistory(value, fromUnit);
            history.setId(UUID.randomUUID().toString());

            if (toUnits != null && !toUnits.isEmpty()) {
                for (UnitDefinition toUnit : toUnits) {
                    if (toUnit.getId().equals(fromUnit.getId())) {
                        continue;
                    }

                    try {
                        double result = ConversionEngine.convert(value, fromUnit, toUnit);
                        String formatted = ConversionEngine.formatResult(result, decimalPlaces, useScientificNotation);

                        ConversionResult conversionResult = new ConversionResult(toUnit, result);
                        conversionResult.setFormattedResult(formatted + " " + toUnit.getSymbol());
                        history.addResult(conversionResult);
                    } catch (Exception e) {
                    }
                }
            } else {
                history = convertToAll(value, fromUnit);
            }

            results.add(history);
            conversionHistory.add(0, history);
        }

        return results;
    }

    public ConversionHistory convertWithChain(double value, List<UnitDefinition> units) {
        if (units == null || units.size() < 2) {
            throw new IllegalArgumentException("换算链至少需要两个单位");
        }

        try {
            double result = ConversionEngine.convertWithChain(value, units.toArray(new UnitDefinition[0]));
            String formatted = ConversionEngine.formatResult(result, decimalPlaces, useScientificNotation);

            ConversionHistory history = new ConversionHistory(value, units.get(0));
            history.setId(UUID.randomUUID().toString());

            ConversionResult conversionResult = new ConversionResult(units.get(units.size() - 1), result);
            conversionResult.setFormattedResult(formatted + " " + units.get(units.size() - 1).getSymbol());
            history.addResult(conversionResult);

            StringBuilder chainBuilder = new StringBuilder();
            for (int i = 0; i < units.size(); i++) {
                if (i > 0) {
                    chainBuilder.append(" → ");
                }
                chainBuilder.append(units.get(i).getSymbol());
            }
            history.setNote("换算链: " + chainBuilder.toString());

            conversionHistory.add(0, history);
            return history;
        } catch (Exception e) {
            throw new IllegalArgumentException("换算链计算失败: " + e.getMessage(), e);
        }
    }

    public List<ConversionHistory> getConversionHistory() {
        return new ArrayList<>(conversionHistory);
    }

    public List<ConversionHistory> getConversionHistory(int limit) {
        if (limit <= 0 || conversionHistory.isEmpty()) {
            return new ArrayList<>();
        }
        int end = Math.min(limit, conversionHistory.size());
        return new ArrayList<>(conversionHistory.subList(0, end));
    }

    public void clearHistory() {
        conversionHistory.clear();
    }

    public void removeFromHistory(String historyId) {
        if (historyId == null) {
            return;
        }
        conversionHistory.removeIf(h -> historyId.equals(h.getId()));
    }

    public void toggleHistoryFavorite(String historyId) {
        if (historyId == null) {
            return;
        }
        for (ConversionHistory h : conversionHistory) {
            if (historyId.equals(h.getId())) {
                h.setFavorite(!h.isFavorite());
                break;
            }
        }
    }

    public int getDecimalPlaces() {
        return decimalPlaces;
    }

    public void setDecimalPlaces(int decimalPlaces) {
        this.decimalPlaces = Math.max(0, Math.min(15, decimalPlaces));
    }

    public boolean isUseScientificNotation() {
        return useScientificNotation;
    }

    public void setUseScientificNotation(boolean useScientificNotation) {
        this.useScientificNotation = useScientificNotation;
    }

    public String formatForExport(List<ConversionHistory> histories, String format) {
        if (histories == null || histories.isEmpty()) {
            return "";
        }

        if ("csv".equalsIgnoreCase(format)) {
            return exportAsCSV(histories);
        } else if ("json".equalsIgnoreCase(format)) {
            return exportAsJSON(histories);
        } else {
            return exportAsText(histories);
        }
    }

    private String exportAsCSV(List<ConversionHistory> histories) {
        StringBuilder sb = new StringBuilder();
        sb.append("时间,输入值,源单位,目标单位,结果\n");

        for (ConversionHistory h : histories) {
            for (ConversionResult r : h.getResults()) {
                sb.append(h.getTimestamp()).append(",");
                sb.append(h.getInputValue()).append(",");
                sb.append(h.getFromUnitName()).append(" (").append(h.getFromUnitSymbol()).append("),");
                sb.append(r.getToUnitName()).append(" (").append(r.getToUnitSymbol()).append("),");
                sb.append(r.getFormattedResult()).append("\n");
            }
        }
        return sb.toString();
    }

    private String exportAsJSON(List<ConversionHistory> histories) {
        StringBuilder sb = new StringBuilder();
        sb.append("[\n");
        for (int i = 0; i < histories.size(); i++) {
            ConversionHistory h = histories.get(i);
            if (i > 0) sb.append(",\n");
            sb.append("  {");
            sb.append("\"timestamp\":\"").append(h.getTimestamp()).append("\",");
            sb.append("\"inputValue\":").append(h.getInputValue()).append(",");
            sb.append("\"fromUnit\":\"").append(h.getFromUnitName()).append("\",");
            sb.append("\"fromSymbol\":\"").append(h.getFromUnitSymbol()).append("\",");
            sb.append("\"results\":[");
            for (int j = 0; j < h.getResults().size(); j++) {
                ConversionResult r = h.getResults().get(j);
                if (j > 0) sb.append(",");
                sb.append("{\"unit\":\"").append(r.getToUnitName()).append("\",");
                sb.append("\"symbol\":\"").append(r.getToUnitSymbol()).append("\",");
                sb.append("\"value\":").append(r.getResultValue()).append(",");
                sb.append("\"formatted\":\"").append(r.getFormattedResult()).append("\"}");
            }
            sb.append("]}");
        }
        sb.append("\n]");
        return sb.toString();
    }

    private String exportAsText(List<ConversionHistory> histories) {
        StringBuilder sb = new StringBuilder();
        for (ConversionHistory h : histories) {
            sb.append("时间: ").append(h.getTimestamp()).append("\n");
            sb.append("输入: ").append(h.getInputValue()).append(" ").append(h.getFromUnitSymbol()).append("\n");
            sb.append("结果:\n");
            for (ConversionResult r : h.getResults()) {
                sb.append("  ").append(r.getToUnitName()).append(" (").append(r.getToUnitSymbol()).append("): ");
                sb.append(r.getFormattedResult()).append("\n");
            }
            sb.append("\n");
        }
        return sb.toString();
    }
}
