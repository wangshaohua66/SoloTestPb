package com.unitconverter.ui;

import com.unitconverter.calculator.CalculatorEngine;
import com.unitconverter.converter.ConversionEngine;
import com.unitconverter.manager.BatchConversionManager;
import com.unitconverter.manager.CustomUnitManager;
import com.unitconverter.model.*;
import com.unitconverter.persistence.DataManager;
import com.unitconverter.registry.UnitRegistry;
import javafx.application.Platform;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.*;
import javafx.scene.input.Clipboard;
import javafx.scene.input.ClipboardContent;
import javafx.stage.Stage;

import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.ResourceBundle;
import java.util.stream.Collectors;

public class MainController implements Initializable {

    @FXML
    private TabPane mainTabPane;

    @FXML
    private Tab converterTab;

    @FXML
    private Tab calculatorTab;

    @FXML
    private Tab batchTab;

    @FXML
    private Tab customTab;

    @FXML
    private Tab historyTab;

    @FXML
    private Tab favoritesTab;

    @FXML
    private ComboBox<UnitType> unitTypeComboBox;

    @FXML
    private ComboBox<UnitDefinition> fromUnitComboBox;

    @FXML
    private ComboBox<UnitDefinition> toUnitComboBox;

    @FXML
    private TextField inputValueTextField;

    @FXML
    private Label resultLabel;

    @FXML
    private Spinner<Integer> decimalPlacesSpinner;

    @FXML
    private CheckBox scientificNotationCheckBox;

    @FXML
    private TextArea allResultsTextArea;

    @FXML
    private TextField calculatorDisplay;

    @FXML
    private TextArea calculatorHistoryTextArea;

    @FXML
    private TextArea batchInputTextArea;

    @FXML
    private ComboBox<UnitType> batchUnitTypeComboBox;

    @FXML
    private ComboBox<UnitDefinition> batchFromUnitComboBox;

    @FXML
    private ListView<UnitDefinition> batchToUnitsListView;

    @FXML
    private TextArea batchResultsTextArea;

    @FXML
    private ComboBox<UnitType> customUnitTypeComboBox;

    @FXML
    private TextField customNameTextField;

    @FXML
    private TextField customSymbolTextField;

    @FXML
    private ComboBox<UnitSystem> customUnitSystemComboBox;

    @FXML
    private RadioButton factorRadioButton;

    @FXML
    private RadioButton formulaRadioButton;

    @FXML
    private TextField conversionFactorTextField;

    @FXML
    private ComboBox<UnitDefinition> baseUnitComboBox;

    @FXML
    private TextField toBaseFormulaTextField;

    @FXML
    private TextField fromBaseFormulaTextField;

    @FXML
    private ListView<UnitDefinition> customUnitsListView;

    @FXML
    private ListView<ConversionHistory> conversionHistoryListView;

    @FXML
    private TextArea historyDetailTextArea;

    @FXML
    private ListView<UnitDefinition> favoritesListView;

    private UnitRegistry unitRegistry;
    private BatchConversionManager batchManager;
    private CustomUnitManager customManager;
    private CalculatorEngine calculatorEngine;
    private DataManager dataManager;

    private Stage primaryStage;
    private String currentCalculatorExpression = "";

    @Override
    public void initialize(URL location, ResourceBundle resources) {
        unitRegistry = UnitRegistry.getInstance();
        batchManager = BatchConversionManager.getInstance();
        customManager = CustomUnitManager.getInstance();
        calculatorEngine = CalculatorEngine.getInstance();
        dataManager = DataManager.getInstance();

        initializeConverterTab();
        initializeCalculatorTab();
        initializeBatchTab();
        initializeCustomTab();
        initializeHistoryTab();
        initializeFavoritesTab();

        loadSettings();
        loadCustomUnits();
    }

    private void initializeConverterTab() {
        unitTypeComboBox.setItems(FXCollections.observableArrayList(UnitType.values()));
        unitTypeComboBox.getItems().remove(UnitType.CUSTOM);
        unitTypeComboBox.setValue(UnitType.LENGTH);

        SpinnerValueFactory<Integer> valueFactory =
            new SpinnerValueFactory.IntegerSpinnerValueFactory(0, 15, 6);
        decimalPlacesSpinner.setValueFactory(valueFactory);

        unitTypeComboBox.valueProperty().addListener((observable, oldValue, newValue) -> {
            updateUnitComboBoxes(newValue);
        });

        fromUnitComboBox.valueProperty().addListener((observable, oldValue, newValue) -> {
            performConversion();
        });

        toUnitComboBox.valueProperty().addListener((observable, oldValue, newValue) -> {
            performConversion();
        });

        inputValueTextField.textProperty().addListener((observable, oldValue, newValue) -> {
            performConversion();
        });

        decimalPlacesSpinner.valueProperty().addListener((observable, oldValue, newValue) -> {
            performConversion();
            batchManager.setDecimalPlaces(newValue);
        });

        scientificNotationCheckBox.selectedProperty().addListener((observable, oldValue, newValue) -> {
            performConversion();
            batchManager.setUseScientificNotation(newValue);
        });

        updateUnitComboBoxes(UnitType.LENGTH);
    }

    private void updateUnitComboBoxes(UnitType unitType) {
        List<UnitDefinition> units = unitRegistry.getUnitsByType(unitType);
        ObservableList<UnitDefinition> unitList = FXCollections.observableArrayList(units);

        fromUnitComboBox.setItems(unitList);
        toUnitComboBox.setItems(unitList);

        if (units.isEmpty()) {
            return;
        }

        UnitDefinition baseUnit = units.stream()
            .filter(UnitDefinition::isBaseUnit)
            .findFirst()
            .orElse(units.get(0));

        fromUnitComboBox.setValue(baseUnit);

        if (units.size() > 1) {
            toUnitComboBox.setValue(units.stream()
                .filter(u -> !u.getId().equals(baseUnit.getId()))
                .findFirst()
                .orElse(units.get(1)));
        } else {
            toUnitComboBox.setValue(baseUnit);
        }
    }

    private void performConversion() {
        String inputText = inputValueTextField.getText().trim();
        if (inputText.isEmpty()) {
            resultLabel.setText("");
            allResultsTextArea.clear();
            return;
        }

        try {
            double value;
            try {
                value = Double.parseDouble(inputText);
            } catch (NumberFormatException e) {
                resultLabel.setText("请输入有效数字");
                return;
            }

            UnitDefinition fromUnit = fromUnitComboBox.getValue();
            UnitDefinition toUnit = toUnitComboBox.getValue();

            if (fromUnit == null || toUnit == null) {
                return;
            }

            int decimalPlaces = decimalPlacesSpinner.getValue();
            boolean useScientific = scientificNotationCheckBox.isSelected();

            double result = ConversionEngine.convert(value, fromUnit, toUnit);
            String formattedResult = ConversionEngine.formatResult(result, decimalPlaces, useScientific);
            resultLabel.setText(formattedResult + " " + toUnit.getSymbol());

            ConversionHistory history = batchManager.convertToAll(value, fromUnit);
            StringBuilder allResults = new StringBuilder();
            allResults.append("所有相关单位换算结果:\n\n");
            for (ConversionResult cr : history.getResults()) {
                allResults.append(String.format("%s (%s): %s\n",
                    cr.getToUnitName(), cr.getToUnitSymbol(), cr.getFormattedResult()));
            }
            allResultsTextArea.setText(allResults.toString());

        } catch (Exception e) {
            resultLabel.setText("换算错误: " + e.getMessage());
        }
    }

    private void initializeCalculatorTab() {
        calculatorDisplay.setEditable(false);
        calculatorDisplay.setText("0");
    }

    @FXML
    private void handleCalculatorNumber(javafx.event.ActionEvent event) {
        Button button = (Button) event.getSource();
        String digit = button.getText();

        if (currentCalculatorExpression.isEmpty() || currentCalculatorExpression.equals("0")) {
            if (digit.equals(".")) {
                currentCalculatorExpression = "0.";
            } else {
                currentCalculatorExpression = digit;
            }
        } else {
            currentCalculatorExpression += digit;
        }
        updateCalculatorDisplay();
    }

    @FXML
    private void handleCalculatorOperator(javafx.event.ActionEvent event) {
        Button button = (Button) event.getSource();
        String op = button.getText();

        if ("+".equals(op)) {
            currentCalculatorExpression += " + ";
        } else if ("-".equals(op)) {
            currentCalculatorExpression += " - ";
        } else if ("×".equals(op)) {
            currentCalculatorExpression += " * ";
        } else if ("÷".equals(op)) {
            currentCalculatorExpression += " / ";
        } else if ("^".equals(op)) {
            currentCalculatorExpression += " ^ ";
        } else if ("%".equals(op)) {
            currentCalculatorExpression += " % ";
        } else if ("mod".equals(op)) {
            currentCalculatorExpression += " % ";
        }
        updateCalculatorDisplay();
    }

    @FXML
    private void handleCalculatorFunction(javafx.event.ActionEvent event) {
        Button button = (Button) event.getSource();
        String func = button.getText();

        if ("√".equals(func)) {
            currentCalculatorExpression += "sqrt(";
        } else if ("ln".equals(func)) {
            currentCalculatorExpression += "ln(";
        } else if ("log".equals(func)) {
            currentCalculatorExpression += "log(";
        } else if ("sin".equals(func)) {
            currentCalculatorExpression += "sin(";
        } else if ("cos".equals(func)) {
            currentCalculatorExpression += "cos(";
        } else if ("tan".equals(func)) {
            currentCalculatorExpression += "tan(";
        } else if ("(".equals(func)) {
            currentCalculatorExpression += "(";
        } else if (")".equals(func)) {
            currentCalculatorExpression += ")";
        } else if ("π".equals(func)) {
            currentCalculatorExpression += String.valueOf(Math.PI);
        } else if ("e".equals(func)) {
            currentCalculatorExpression += String.valueOf(Math.E);
        }
        updateCalculatorDisplay();
    }

    @FXML
    private void handleCalculatorClear() {
        currentCalculatorExpression = "";
        calculatorDisplay.setText("0");
    }

    @FXML
    private void handleCalculatorBackspace() {
        if (currentCalculatorExpression.isEmpty()) {
            return;
        }
        currentCalculatorExpression = currentCalculatorExpression.substring(0, currentCalculatorExpression.length() - 1);
        if (currentCalculatorExpression.isEmpty()) {
            calculatorDisplay.setText("0");
        } else {
            updateCalculatorDisplay();
        }
    }

    @FXML
    private void handleCalculatorEquals() {
        if (currentCalculatorExpression.isEmpty()) {
            return;
        }

        try {
            double result = calculatorEngine.calculate(currentCalculatorExpression);
            String resultStr = ConversionEngine.formatResult(result, decimalPlacesSpinner.getValue());
            calculatorDisplay.setText(currentCalculatorExpression + " = " + resultStr);
            currentCalculatorExpression = String.valueOf(result);
            updateCalculatorHistory();
        } catch (IllegalArgumentException e) {
            calculatorDisplay.setText("错误: " + e.getMessage());
            currentCalculatorExpression = "";
        }
    }

    private void updateCalculatorDisplay() {
        calculatorDisplay.setText(currentCalculatorExpression.isEmpty() ? "0" : currentCalculatorExpression);
    }

    private void updateCalculatorHistory() {
        List<CalculatorEngine.CalculationHistory> history = calculatorEngine.getCalculationHistory(20);
        StringBuilder sb = new StringBuilder();
        for (CalculatorEngine.CalculationHistory h : history) {
            sb.append(h.getExpression()).append(" = ").append(h.getResult()).append("\n");
        }
        calculatorHistoryTextArea.setText(sb.toString());
    }

    private void initializeBatchTab() {
        batchUnitTypeComboBox.setItems(FXCollections.observableArrayList(UnitType.values()));
        batchUnitTypeComboBox.getItems().remove(UnitType.CUSTOM);
        batchUnitTypeComboBox.setValue(UnitType.LENGTH);

        batchUnitTypeComboBox.valueProperty().addListener((observable, oldValue, newValue) -> {
            updateBatchUnitComboBoxes(newValue);
        });

        batchToUnitsListView.getSelectionModel().setSelectionMode(SelectionMode.MULTIPLE);

        updateBatchUnitComboBoxes(UnitType.LENGTH);
    }

    private void updateBatchUnitComboBoxes(UnitType unitType) {
        List<UnitDefinition> units = unitRegistry.getUnitsByType(unitType);
        ObservableList<UnitDefinition> unitList = FXCollections.observableArrayList(units);

        batchFromUnitComboBox.setItems(unitList);
        batchToUnitsListView.setItems(unitList);

        if (!units.isEmpty()) {
            UnitDefinition baseUnit = units.stream()
                .filter(UnitDefinition::isBaseUnit)
                .findFirst()
                .orElse(units.get(0));
            batchFromUnitComboBox.setValue(baseUnit);
        }
    }

    @FXML
    private void handleBatchConvert() {
        String inputText = batchInputTextArea.getText().trim();
        if (inputText.isEmpty()) {
            showAlert("提示", "请输入要换算的数值，每行一个");
            return;
        }

        UnitDefinition fromUnit = batchFromUnitComboBox.getValue();
        if (fromUnit == null) {
            showAlert("提示", "请选择源单位");
            return;
        }

        List<Double> values = new ArrayList<>();
        String[] lines = inputText.split("\\r?\\n");
        for (String line : lines) {
            line = line.trim();
            if (line.isEmpty()) continue;
            try {
                values.add(Double.parseDouble(line));
            } catch (NumberFormatException e) {
            }
        }

        if (values.isEmpty()) {
            showAlert("提示", "没有有效的数值");
            return;
        }

        List<UnitDefinition> selectedToUnits = new ArrayList<>(
            batchToUnitsListView.getSelectionModel().getSelectedItems());

        List<ConversionHistory> results = batchManager.batchConvert(values, fromUnit,
            selectedToUnits.isEmpty() ? null : selectedToUnits);

        StringBuilder sb = new StringBuilder();
        for (ConversionHistory history : results) {
            sb.append("输入: ").append(history.getInputValue()).append(" ")
              .append(history.getFromUnitSymbol()).append("\n");
            for (ConversionResult cr : history.getResults()) {
                sb.append("  → ").append(cr.getFormattedResult()).append("\n");
            }
            sb.append("\n");
        }
        batchResultsTextArea.setText(sb.toString());
    }

    @FXML
    private void handleBatchExport() {
        TextInputDialog dialog = new TextInputDialog();
        dialog.setTitle("导出结果");
        dialog.setHeaderText("选择导出格式");
        dialog.setContentText("格式 (csv, json, text):");

        Optional<String> result = dialog.showAndWait();
        result.ifPresent(format -> {
            String exported = batchManager.formatForExport(batchManager.getConversionHistory(), format);
            if (!exported.isEmpty()) {
                ClipboardContent content = new ClipboardContent();
                content.putString(exported);
                Clipboard.getSystemClipboard().setContent(content);
                showAlert("成功", "结果已复制到剪贴板");
            }
        });
    }

    private void initializeCustomTab() {
        customUnitTypeComboBox.setItems(FXCollections.observableArrayList(UnitType.values()));
        customUnitTypeComboBox.setValue(UnitType.LENGTH);

        customUnitSystemComboBox.setItems(FXCollections.observableArrayList(UnitSystem.values()));
        customUnitSystemComboBox.setValue(UnitSystem.CUSTOM);

        ToggleGroup conversionTypeGroup = new ToggleGroup();
        factorRadioButton.setToggleGroup(conversionTypeGroup);
        formulaRadioButton.setToggleGroup(conversionTypeGroup);
        factorRadioButton.setSelected(true);

        conversionTypeGroup.selectedToggleProperty().addListener((observable, oldValue, newValue) -> {
            boolean useFactor = newValue == factorRadioButton;
            conversionFactorTextField.setDisable(!useFactor);
            baseUnitComboBox.setDisable(!useFactor);
            toBaseFormulaTextField.setDisable(useFactor);
            fromBaseFormulaTextField.setDisable(useFactor);
        });

        customUnitTypeComboBox.valueProperty().addListener((observable, oldValue, newValue) -> {
            updateCustomBaseUnits(newValue);
        });

        updateCustomBaseUnits(UnitType.LENGTH);
        refreshCustomUnitsList();
    }

    private void updateCustomBaseUnits(UnitType unitType) {
        List<UnitDefinition> units = unitRegistry.getUnitsByType(unitType);
        ObservableList<UnitDefinition> unitList = FXCollections.observableArrayList(units);
        baseUnitComboBox.setItems(unitList);
        if (!units.isEmpty()) {
            baseUnitComboBox.setValue(units.get(0));
        }
    }

    private void refreshCustomUnitsList() {
        List<UnitDefinition> customUnits = customManager.getCustomUnits();
        customUnitsListView.setItems(FXCollections.observableArrayList(customUnits));
    }

    @FXML
    private void handleAddCustomUnit() {
        String name = customNameTextField.getText().trim();
        String symbol = customSymbolTextField.getText().trim();
        UnitType unitType = customUnitTypeComboBox.getValue();
        UnitSystem unitSystem = customUnitSystemComboBox.getValue();

        if (name.isEmpty()) {
            showAlert("错误", "请输入单位名称");
            return;
        }
        if (symbol.isEmpty()) {
            showAlert("错误", "请输入单位符号");
            return;
        }

        try {
            if (factorRadioButton.isSelected()) {
                double factor = Double.parseDouble(conversionFactorTextField.getText().trim());
                UnitDefinition baseUnit = baseUnitComboBox.getValue();
                String baseUnitId = baseUnit != null ? baseUnit.getId() : null;

                customManager.createCustomUnit(name, symbol, unitType, unitSystem, factor, baseUnitId);
            } else {
                String toFormula = toBaseFormulaTextField.getText().trim();
                String fromFormula = fromBaseFormulaTextField.getText().trim();
                UnitDefinition baseUnit = baseUnitComboBox.getValue();
                String baseUnitId = baseUnit != null ? baseUnit.getId() : null;

                customManager.createCustomUnitWithFormula(name, symbol, unitType, unitSystem,
                    toFormula, fromFormula, baseUnitId);
            }

            showAlert("成功", "自定义单位添加成功");
            refreshCustomUnitsList();

            customNameTextField.clear();
            customSymbolTextField.clear();
            conversionFactorTextField.clear();
            toBaseFormulaTextField.clear();
            fromBaseFormulaTextField.clear();

        } catch (NumberFormatException e) {
            showAlert("错误", "请输入有效的换算因子");
        } catch (IllegalArgumentException e) {
            showAlert("错误", e.getMessage());
        }
    }

    @FXML
    private void handleDeleteCustomUnit() {
        UnitDefinition selected = customUnitsListView.getSelectionModel().getSelectedItem();
        if (selected == null) {
            showAlert("提示", "请选择要删除的自定义单位");
            return;
        }

        Alert alert = new Alert(Alert.AlertType.CONFIRMATION);
        alert.setTitle("确认删除");
        alert.setHeaderText("删除自定义单位");
        alert.setContentText("确定要删除单位: " + selected.getDisplayName() + "?");

        Optional<ButtonType> result = alert.showAndWait();
        if (result.isPresent() && result.get() == ButtonType.OK) {
            customManager.deleteCustomUnit(selected.getId());
            refreshCustomUnitsList();
        }
    }

    @FXML
    private void handleTestFormula() {
        String formula = toBaseFormulaTextField.getText().trim();
        if (formula.isEmpty()) {
            showAlert("提示", "请输入公式");
            return;
        }

        TextInputDialog dialog = new TextInputDialog("1");
        dialog.setTitle("测试公式");
        dialog.setHeaderText("输入测试值");
        dialog.setContentText("x = ");

        Optional<String> result = dialog.showAndWait();
        result.ifPresent(valueStr -> {
            try {
                double value = Double.parseDouble(valueStr);
                double testResult = customManager.testFormula(formula, value);
                showAlert("测试结果", "公式: " + formula + "\nx = " + value + "\n结果: " + testResult);
            } catch (NumberFormatException e) {
                showAlert("错误", "请输入有效的数值");
            } catch (IllegalArgumentException e) {
                showAlert("错误", e.getMessage());
            }
        });
    }

    private void initializeHistoryTab() {
        conversionHistoryListView.getSelectionModel().selectedItemProperty().addListener(
            (observable, oldValue, newValue) -> {
                if (newValue != null) {
                    updateHistoryDetail(newValue);
                }
            }
        );

        refreshHistoryList();
    }

    private void refreshHistoryList() {
        List<ConversionHistory> history = batchManager.getConversionHistory(50);
        conversionHistoryListView.setItems(FXCollections.observableArrayList(history));
    }

    private void updateHistoryDetail(ConversionHistory history) {
        StringBuilder sb = new StringBuilder();
        sb.append("时间: ").append(history.getTimestamp()).append("\n");
        sb.append("输入: ").append(history.getInputValue()).append(" ")
          .append(history.getFromUnitSymbol()).append("\n");
        if (history.getNote() != null && !history.getNote().isEmpty()) {
            sb.append("备注: ").append(history.getNote()).append("\n");
        }
        sb.append("\n结果:\n");
        for (ConversionResult cr : history.getResults()) {
            sb.append("  ").append(cr.getToUnitName()).append(" (").append(cr.getToUnitSymbol())
              .append("): ").append(cr.getFormattedResult()).append("\n");
        }
        historyDetailTextArea.setText(sb.toString());
    }

    @FXML
    private void handleClearHistory() {
        Alert alert = new Alert(Alert.AlertType.CONFIRMATION);
        alert.setTitle("确认清空历史记录");
        alert.setHeaderText("清空换算历史");
        alert.setContentText("确定要清空所有历史记录吗？");

        Optional<ButtonType> result = alert.showAndWait();
        if (result.isPresent() && result.get() == ButtonType.OK) {
            batchManager.clearHistory();
            refreshHistoryList();
            historyDetailTextArea.clear();
        }
    }

    private void initializeFavoritesTab() {
        refreshFavoritesList();
    }

    private void refreshFavoritesList() {
        List<UnitDefinition> favorites = unitRegistry.getFavoriteUnits();
        favoritesListView.setItems(FXCollections.observableArrayList(favorites));
    }

    @FXML
    private void handleAddToFavorites() {
        UnitDefinition fromUnit = fromUnitComboBox.getValue();
        if (fromUnit == null) {
            showAlert("提示", "请先选择一个单位");
            return;
        }

        unitRegistry.updateUnitFavorite(fromUnit.getId(), true);
        refreshFavoritesList();
        showAlert("成功", "已添加到收藏");
    }

    @FXML
    private void handleRemoveFromFavorites() {
        UnitDefinition selected = favoritesListView.getSelectionModel().getSelectedItem();
        if (selected == null) {
            showAlert("提示", "请选择要移除的收藏单位");
            return;
        }

        unitRegistry.updateUnitFavorite(selected.getId(), false);
        refreshFavoritesList();
    }

    private void loadSettings() {
        DataManager.AppSettings settings = dataManager.loadSettings();
        if (settings != null) {
            decimalPlacesSpinner.getValueFactory().setValue(settings.getDecimalPlaces());
            scientificNotationCheckBox.setSelected(settings.isUseScientificNotation());
            batchManager.setDecimalPlaces(settings.getDecimalPlaces());
            batchManager.setUseScientificNotation(settings.isUseScientificNotation());
        }
    }

    private void loadCustomUnits() {
        List<UnitDefinition> customUnits = dataManager.loadCustomUnits();
        for (UnitDefinition unit : customUnits) {
            unitRegistry.addUnit(unit);
        }
        refreshCustomUnitsList();
    }

    @FXML
    private void handleSaveSettings() {
        DataManager.AppSettings settings = new DataManager.AppSettings();
        settings.setDecimalPlaces(decimalPlacesSpinner.getValue());
        settings.setUseScientificNotation(scientificNotationCheckBox.isSelected());
        dataManager.saveSettings(settings);

        dataManager.saveCustomUnits(customManager.getCustomUnits());

        List<String> favoriteIds = unitRegistry.getFavoriteUnits().stream()
            .map(UnitDefinition::getId)
            .collect(Collectors.toList());
        dataManager.saveFavorites(favoriteIds);

        showAlert("成功", "设置已保存");
    }

    @FXML
    private void handleAbout() {
        showAlert("关于", "单位换算器 v1.0.0\n\n" +
            "支持多种单位换算:\n" +
            "- 长度、重量、温度、面积、体积\n" +
            "- 速度、时间、数据存储、压力、功率\n\n" +
            "特性:\n" +
            "- 自定义单位\n" +
            "- 批量换算\n" +
            "- 计算器\n" +
            "- 收藏功能");
    }

    @FXML
    private void handleExit() {
        Platform.exit();
    }

    private void showAlert(String title, String message) {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.showAndWait();
    }

    public void setPrimaryStage(Stage primaryStage) {
        this.primaryStage = primaryStage;
    }
}
