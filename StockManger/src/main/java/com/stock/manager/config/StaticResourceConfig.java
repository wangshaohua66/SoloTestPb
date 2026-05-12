package com.stock.manager.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class StaticResourceConfig implements WebMvcConfigurer {

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/test-reports/**")
                .addResourceLocations(
                        "classpath:/static/test-reports/",
                        "file:target/surefire-reports/",
                        "file:target/reports/"
                );
    }
}
