package com.stock.manager.controller;

import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.io.File;

@RestController
@RequestMapping("/allure-report")
public class AllureReportController {

    private static final String ALLURE_REPORT_PATH = "target/site/allure-report";

    @GetMapping
    public ResponseEntity<Resource> getIndex() {
        return serveResource("index.html");
    }

    @GetMapping("/")
    public ResponseEntity<Resource> getIndexWithSlash() {
        return serveResource("index.html");
    }

    @GetMapping("/{fileName:.+}")
    public ResponseEntity<Resource> getResource(@PathVariable String fileName) {
        return serveResource(fileName);
    }

    @GetMapping("/data/{fileName:.+}")
    public ResponseEntity<Resource> getDataResource(@PathVariable String fileName) {
        return serveResource("data/" + fileName);
    }

    @GetMapping("/plugins/{path:.+}")
    public ResponseEntity<Resource> getPluginResource(@PathVariable String path) {
        return serveResource("plugins/" + path);
    }

    @GetMapping("/export/{path:.+}")
    public ResponseEntity<Resource> getExportResource(@PathVariable String path) {
        return serveResource("export/" + path);
    }

    @GetMapping("/widgets/{path:.+}")
    public ResponseEntity<Resource> getWidgetsResource(@PathVariable String path) {
        return serveResource("widgets/" + path);
    }

    private ResponseEntity<Resource> serveResource(String path) {
        File file = new File(ALLURE_REPORT_PATH, path);
        
        if (file.exists() && file.isFile()) {
            Resource resource = new FileSystemResource(file);
            return ResponseEntity.ok()
                    .contentType(getContentType(path))
                    .body(resource);
        }

        Resource classPathResource = new ClassPathResource("static/allure-report/" + path);
        if (classPathResource.exists()) {
            return ResponseEntity.ok()
                    .contentType(getContentType(path))
                    .body(classPathResource);
        }

        File indexFile = new File(ALLURE_REPORT_PATH, "index.html");
        if (indexFile.exists()) {
            Resource resource = new FileSystemResource(indexFile);
            return ResponseEntity.ok()
                    .contentType(MediaType.TEXT_HTML)
                    .body(resource);
        }

        return ResponseEntity.notFound().build();
    }

    private MediaType getContentType(String path) {
        if (path.endsWith(".html")) {
            return MediaType.TEXT_HTML;
        } else if (path.endsWith(".css")) {
            return MediaType.parseMediaType("text/css");
        } else if (path.endsWith(".js")) {
            return MediaType.parseMediaType("application/javascript");
        } else if (path.endsWith(".json")) {
            return MediaType.APPLICATION_JSON;
        } else if (path.endsWith(".png")) {
            return MediaType.IMAGE_PNG;
        } else if (path.endsWith(".jpg") || path.endsWith(".jpeg")) {
            return MediaType.IMAGE_JPEG;
        } else if (path.endsWith(".svg")) {
            return MediaType.parseMediaType("image/svg+xml");
        } else if (path.endsWith(".woff") || path.endsWith(".woff2")) {
            return MediaType.parseMediaType("font/woff");
        }
        return MediaType.APPLICATION_OCTET_STREAM;
    }
}
