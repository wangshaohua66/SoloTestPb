package com.taskmanager.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.servlet.http.HttpServletRequest;
import java.io.File;
import java.io.IOException;

@RestController
@RequestMapping("/allure-report")
@Tag(name = "Allure报告", description = "Allure测试报告访问")
public class AllureReportController {

    private static final String ALLURE_REPORT_PATH = System.getProperty("user.dir") + "/target/allure-report/";

    @GetMapping(value = {"", "/"})
    @Operation(summary = "获取Allure报告首页")
    public ResponseEntity<Resource> getIndex(HttpServletRequest request) throws IOException {
        return getResource("index.html");
    }

    @GetMapping("/{filename:.+}")
    @Operation(summary = "获取Allure报告资源文件")
    public ResponseEntity<Resource> getResource(@PathVariable String filename) throws IOException {
        File file = new File(ALLURE_REPORT_PATH + filename);
        
        if (!file.exists() || file.isDirectory()) {
            file = new File(ALLURE_REPORT_PATH + "index.html");
        }

        Resource resource = new FileSystemResource(file);
        
        if (!resource.exists()) {
            resource = new ClassPathResource("static/" + filename);
        }

        MediaType mediaType = getMediaType(filename);
        return ResponseEntity.ok()
                .contentType(mediaType)
                .body(resource);
    }

    @GetMapping("/data/{filename:.+}")
    @Operation(summary = "获取Allure报告数据文件")
    public ResponseEntity<Resource> getDataFile(@PathVariable String filename) throws IOException {
        return getResource("data/" + filename);
    }

    @GetMapping("/widgets/{filename:.+}")
    @Operation(summary = "获取Allure报告组件文件")
    public ResponseEntity<Resource> getWidgetFile(@PathVariable String filename) throws IOException {
        return getResource("widgets/" + filename);
    }

    @GetMapping("/plugin/{plugin}/{filename:.+}")
    @Operation(summary = "获取Allure报告插件文件")
    public ResponseEntity<Resource> getPluginFile(
            @PathVariable String plugin,
            @PathVariable String filename) throws IOException {
        return getResource("plugin/" + plugin + "/" + filename);
    }

    private MediaType getMediaType(String filename) {
        if (filename.endsWith(".html") || filename.endsWith(".htm")) {
            return MediaType.TEXT_HTML;
        } else if (filename.endsWith(".css")) {
            return MediaType.parseMediaType("text/css");
        } else if (filename.endsWith(".js")) {
            return MediaType.parseMediaType("application/javascript");
        } else if (filename.endsWith(".json")) {
            return MediaType.APPLICATION_JSON;
        } else if (filename.endsWith(".png")) {
            return MediaType.IMAGE_PNG;
        } else if (filename.endsWith(".ico")) {
            return MediaType.parseMediaType("image/x-icon");
        } else if (filename.endsWith(".csv")) {
            return MediaType.parseMediaType("text/csv");
        } else if (filename.endsWith(".txt")) {
            return MediaType.TEXT_PLAIN;
        }
        return MediaType.APPLICATION_OCTET_STREAM;
    }
}
