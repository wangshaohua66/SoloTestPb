package com.unitconverter.model;

import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

public class ConversionHistory implements Serializable {
    private static final long serialVersionUID = 1L;

    private String id;
    private LocalDateTime timestamp;
    private double inputValue;
    private String fromUnitId;
    private String fromUnitName;
    private String fromUnitSymbol;
    private List<ConversionResult> results;
    private String note;
    private boolean isFavorite;
    private String groupName;

    public ConversionHistory() {
        this.timestamp = LocalDateTime.now();
        this.results = new ArrayList<>();
        this.isFavorite = false;
    }

    public ConversionHistory(double inputValue, UnitDefinition fromUnit) {
        this();
        this.inputValue = inputValue;
        if (fromUnit != null) {
            this.fromUnitId = fromUnit.getId();
            this.fromUnitName = fromUnit.getName();
            this.fromUnitSymbol = fromUnit.getSymbol();
        }
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }

    public double getInputValue() {
        return inputValue;
    }

    public void setInputValue(double inputValue) {
        this.inputValue = inputValue;
    }

    public String getFromUnitId() {
        return fromUnitId;
    }

    public void setFromUnitId(String fromUnitId) {
        this.fromUnitId = fromUnitId;
    }

    public String getFromUnitName() {
        return fromUnitName;
    }

    public void setFromUnitName(String fromUnitName) {
        this.fromUnitName = fromUnitName;
    }

    public String getFromUnitSymbol() {
        return fromUnitSymbol;
    }

    public void setFromUnitSymbol(String fromUnitSymbol) {
        this.fromUnitSymbol = fromUnitSymbol;
    }

    public List<ConversionResult> getResults() {
        return results;
    }

    public void setResults(List<ConversionResult> results) {
        this.results = results;
    }

    public void addResult(ConversionResult result) {
        if (this.results == null) {
            this.results = new ArrayList<>();
        }
        this.results.add(result);
    }

    public String getNote() {
        return note;
    }

    public void setNote(String note) {
        this.note = note;
    }

    public boolean isFavorite() {
        return isFavorite;
    }

    public void setFavorite(boolean favorite) {
        isFavorite = favorite;
    }

    public String getGroupName() {
        return groupName;
    }

    public void setGroupName(String groupName) {
        this.groupName = groupName;
    }
}
