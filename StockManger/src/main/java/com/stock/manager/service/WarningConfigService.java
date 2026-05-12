package com.stock.manager.service;

import com.stock.manager.entity.WarningConfig;
import com.stock.manager.repository.WarningConfigRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.annotation.PostConstruct;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@Service
public class WarningConfigService {

    @Autowired
    private WarningConfigRepository warningConfigRepository;

    public static final String LOW_STOCK_WARNING_ENABLED = "low.stock.warning.enabled";
    public static final String HIGH_STOCK_WARNING_ENABLED = "high.stock.warning.enabled";
    public static final String AUTO_RESOLVE_WARNING_ENABLED = "auto.resolve.warning.enabled";

    @PostConstruct
    @Transactional
    public void initDefaultConfigs() {
        initConfigIfNotExists(LOW_STOCK_WARNING_ENABLED, "true", "库存下限预警开关");
        initConfigIfNotExists(HIGH_STOCK_WARNING_ENABLED, "true", "库存上限预警开关");
        initConfigIfNotExists(AUTO_RESOLVE_WARNING_ENABLED, "false", "自动解除预警开关");
    }

    private void initConfigIfNotExists(String key, String value, String description) {
        if (!warningConfigRepository.existsByConfigKey(key)) {
            WarningConfig config = new WarningConfig();
            config.setConfigKey(key);
            config.setConfigValue(value);
            config.setDescription(description);
            warningConfigRepository.save(config);
        }
    }

    @Transactional(readOnly = true)
    public List<WarningConfig> getAllConfigs() {
        return warningConfigRepository.findAll();
    }

    @Transactional(readOnly = true)
    public Optional<WarningConfig> getConfigByKey(String key) {
        return warningConfigRepository.findByConfigKey(key);
    }

    @Transactional(readOnly = true)
    public boolean isLowStockWarningEnabled() {
        return isEnabled(LOW_STOCK_WARNING_ENABLED);
    }

    @Transactional(readOnly = true)
    public boolean isHighStockWarningEnabled() {
        return isEnabled(HIGH_STOCK_WARNING_ENABLED);
    }

    @Transactional(readOnly = true)
    public boolean isAutoResolveWarningEnabled() {
        return isEnabled(AUTO_RESOLVE_WARNING_ENABLED);
    }

    private boolean isEnabled(String key) {
        return warningConfigRepository.findByConfigKey(key)
                .map(config -> "true".equalsIgnoreCase(config.getConfigValue()))
                .orElse(true);
    }

    @Transactional
    public WarningConfig updateConfig(String key, String value, String operator) {
        WarningConfig config = warningConfigRepository.findByConfigKey(key)
                .orElseGet(() -> {
                    WarningConfig newConfig = new WarningConfig();
                    newConfig.setConfigKey(key);
                    return newConfig;
                });
        config.setConfigValue(value);
        return warningConfigRepository.save(config);
    }

    @Transactional
    public WarningConfig toggleConfig(String key, String operator) {
        WarningConfig config = warningConfigRepository.findByConfigKey(key)
                .orElseThrow(() -> new IllegalArgumentException("配置项不存在: " + key));
        boolean currentValue = "true".equalsIgnoreCase(config.getConfigValue());
        config.setConfigValue(String.valueOf(!currentValue));
        return warningConfigRepository.save(config);
    }

    @Transactional
    public Map<String, Boolean> getAllWarningSwitches() {
        Map<String, Boolean> switches = new HashMap<>();
        switches.put("lowStockWarning", isLowStockWarningEnabled());
        switches.put("highStockWarning", isHighStockWarningEnabled());
        switches.put("autoResolveWarning", isAutoResolveWarningEnabled());
        return switches;
    }
}
