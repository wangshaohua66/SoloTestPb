package com.unitconverter.model;

import java.io.Serializable;

public class ConversionResult implements Serializable {
    private static final long serialVersionUID = 1L;

    private String toUnitId;
    private String toUnitName;
    private String toUnitSymbol;
    private double resultValue;
    private String formattedResult;

    public ConversionResult() {
    }

    public ConversionResult(UnitDefinition toUnit, double resultValue) {
        if (toUnit != null) {
            this.toUnitId = toUnit.getId();
            this.toUnitName = toUnit.getName();
            this.toUnitSymbol = toUnit.getSymbol();
        }
        this.resultValue = resultValue;
    }

    public String getToUnitId() {
        return toUnitId;
    }

    public void setToUnitId(String toUnitId) {
        this.toUnitId = toUnitId;
    }

    public String getToUnitName() {
        return toUnitName;
    }

    public void setToUnitName(String toUnitName) {
        this.toUnitName = toUnitName;
    }

    public String getToUnitSymbol() {
        return toUnitSymbol;
    }

    public void setToUnitSymbol(String toUnitSymbol) {
        this.toUnitSymbol = toUnitSymbol;
    }

    public double getResultValue() {
        return resultValue;
    }

    public void setResultValue(double resultValue) {
        this.resultValue = resultValue;
    }

    public String getFormattedResult() {
        return formattedResult;
    }

    public void setFormattedResult(String formattedResult) {
        this.formattedResult = formattedResult;
    }

    @Override
    public String toString() {
        return formattedResult != null ? formattedResult : String.valueOf(resultValue);
    }
}
