package com.qrcode.util;

import com.qrcode.model.QRCodeStyle;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

public class BatchProcessor {

    @FunctionalInterface
    public interface QRCodeProcessor {
        void process(String content, String outputFileName) throws Exception;
    }

    public static List<String> readFromCSV(File file) throws IOException {
        List<String> contents = new ArrayList<>();
        
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(new FileInputStream(file), StandardCharsets.UTF_8))) {
            String line;
            boolean firstLine = true;
            
            while ((line = reader.readLine()) != null) {
                if (firstLine) {
                    firstLine = false;
                    continue;
                }
                if (!line.trim().isEmpty()) {
                    contents.add(line);
                }
            }
        }
        
        return contents;
    }

    public static List<String> readFromExcel(File file) throws IOException {
        List<String> contents = new ArrayList<>();
        
        try (Workbook workbook = WorkbookFactory.create(file)) {
            Sheet sheet = workbook.getSheetAt(0);
            boolean firstRow = true;
            
            for (Row row : sheet) {
                if (firstRow) {
                    firstRow = false;
                    continue;
                }
                
                Cell cell = row.getCell(0);
                if (cell != null) {
                    String content = getCellValueAsString(cell);
                    if (!content.isEmpty()) {
                        contents.add(content);
                    }
                }
            }
        }
        
        return contents;
    }

    private static String getCellValueAsString(Cell cell) {
        switch (cell.getCellType()) {
            case STRING:
                return cell.getStringCellValue();
            case NUMERIC:
                if (DateUtil.isCellDateFormatted(cell)) {
                    return cell.getLocalDateTimeCellValue().toString();
                }
                return String.valueOf((long) cell.getNumericCellValue());
            case BOOLEAN:
                return String.valueOf(cell.getBooleanCellValue());
            case FORMULA:
                return cell.getCellFormula();
            default:
                return "";
        }
    }

    public static void batchGenerateFromCSV(File csvFile, File outputDir, QRCodeStyle style) throws Exception {
        List<String> contents = readFromCSV(csvFile);
        batchGenerate(contents, outputDir, style);
    }

    public static void batchGenerateFromExcel(File excelFile, File outputDir, QRCodeStyle style) throws Exception {
        List<String> contents = readFromExcel(excelFile);
        batchGenerate(contents, outputDir, style);
    }

    public static void batchGenerate(List<String> contents, File outputDir, QRCodeStyle style) throws Exception {
        if (!outputDir.exists()) {
            outputDir.mkdirs();
        }
        
        for (int i = 0; i < contents.size(); i++) {
            String content = contents.get(i);
            String fileName = "qrcode_" + (i + 1) + ".png";
            String filePath = new File(outputDir, fileName).getAbsolutePath();
            
            try {
                QRCodeGenerator.saveQRCode(
                    QRCodeGenerator.generateQRCode(content, style),
                    filePath
                );
            } catch (Exception e) {
                throw new Exception("生成第 " + (i + 1) + " 个二维码失败: " + e.getMessage(), e);
            }
        }
    }

    public static List<BatchDecodeResult> batchDecode(File inputDir) throws Exception {
        List<BatchDecodeResult> results = new ArrayList<>();
        
        File[] files = inputDir.listFiles((dir, name) -> 
            name.toLowerCase().endsWith(".png") || 
            name.toLowerCase().endsWith(".jpg") || 
            name.toLowerCase().endsWith(".jpeg")
        );
        
        if (files == null || files.length == 0) {
            throw new IOException("目录中没有找到图片文件");
        }
        
        for (File file : files) {
            BatchDecodeResult result = new BatchDecodeResult();
            result.setFileName(file.getName());
            result.setFilePath(file.getAbsolutePath());
            
            try {
                String content = QRCodeReader.decodeQRCode(file);
                result.setContent(content);
                result.setSuccess(true);
            } catch (Exception e) {
                result.setSuccess(false);
                result.setErrorMessage(e.getMessage());
            }
            
            results.add(result);
        }
        
        return results;
    }

    public static void writeBatchResultsToCSV(List<BatchDecodeResult> results, File outputFile) throws IOException {
        try (BufferedWriter writer = new BufferedWriter(
                new OutputStreamWriter(new FileOutputStream(outputFile), StandardCharsets.UTF_8))) {
            writer.write("\uFEFF");
            writer.write("文件名,内容,状态,错误信息");
            writer.newLine();
            
            for (BatchDecodeResult result : results) {
                StringBuilder line = new StringBuilder();
                line.append(escapeCSVField(result.getFileName())).append(",");
                line.append(escapeCSVField(result.getContent())).append(",");
                line.append(result.isSuccess() ? "成功" : "失败").append(",");
                line.append(escapeCSVField(result.getErrorMessage()));
                writer.write(line.toString());
                writer.newLine();
            }
        }
    }

    public static void writeBatchResultsToExcel(List<BatchDecodeResult> results, File outputFile) throws IOException {
        try (Workbook workbook = new XSSFWorkbook()) {
            Sheet sheet = workbook.createSheet("识别结果");
            
            Row headerRow = sheet.createRow(0);
            headerRow.createCell(0).setCellValue("文件名");
            headerRow.createCell(1).setCellValue("内容");
            headerRow.createCell(2).setCellValue("状态");
            headerRow.createCell(3).setCellValue("错误信息");
            
            CellStyle successStyle = createCellStyle(workbook, IndexedColors.GREEN);
            CellStyle failedStyle = createCellStyle(workbook, IndexedColors.RED);
            
            int rowNum = 1;
            for (BatchDecodeResult result : results) {
                Row row = sheet.createRow(rowNum++);
                row.createCell(0).setCellValue(result.getFileName());
                row.createCell(1).setCellValue(result.getContent() == null ? "" : result.getContent());
                
                Cell statusCell = row.createCell(2);
                statusCell.setCellValue(result.isSuccess() ? "成功" : "失败");
                statusCell.setCellStyle(result.isSuccess() ? successStyle : failedStyle);
                
                row.createCell(3).setCellValue(result.getErrorMessage() == null ? "" : result.getErrorMessage());
            }
            
            for (int i = 0; i < 4; i++) {
                sheet.autoSizeColumn(i);
            }
            
            try (FileOutputStream fos = new FileOutputStream(outputFile)) {
                workbook.write(fos);
            }
        }
    }

    private static CellStyle createCellStyle(Workbook workbook, IndexedColors color) {
        CellStyle style = workbook.createCellStyle();
        Font font = workbook.createFont();
        font.setColor(color.getIndex());
        style.setFont(font);
        return style;
    }

    private static String escapeCSVField(String field) {
        if (field == null) {
            return "";
        }
        if (field.contains(",") || field.contains("\"") || field.contains("\n")) {
            return "\"" + field.replace("\"", "\"\"") + "\"";
        }
        return field;
    }

    public static class BatchDecodeResult {
        private String fileName;
        private String filePath;
        private String content;
        private boolean success;
        private String errorMessage;

        public String getFileName() {
            return fileName;
        }

        public void setFileName(String fileName) {
            this.fileName = fileName;
        }

        public String getFilePath() {
            return filePath;
        }

        public void setFilePath(String filePath) {
            this.filePath = filePath;
        }

        public String getContent() {
            return content;
        }

        public void setContent(String content) {
            this.content = content;
        }

        public boolean isSuccess() {
            return success;
        }

        public void setSuccess(boolean success) {
            this.success = success;
        }

        public String getErrorMessage() {
            return errorMessage;
        }

        public void setErrorMessage(String errorMessage) {
            this.errorMessage = errorMessage;
        }
    }
}
