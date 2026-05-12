package com.qrcode.model;

import java.time.LocalDateTime;

public class QRCodeRecord {
    private Long id;
    private String content;
    private QRCodeType type;
    private String filePath;
    private String category;
    private boolean favorite;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;

    public QRCodeRecord() {
        this.createTime = LocalDateTime.now();
        this.updateTime = LocalDateTime.now();
    }

    public QRCodeRecord(String content, QRCodeType type) {
        this();
        this.content = content;
        this.type = type;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public QRCodeType getType() {
        return type;
    }

    public void setType(QRCodeType type) {
        this.type = type;
    }

    public String getFilePath() {
        return filePath;
    }

    public void setFilePath(String filePath) {
        this.filePath = filePath;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public boolean isFavorite() {
        return favorite;
    }

    public void setFavorite(boolean favorite) {
        this.favorite = favorite;
    }

    public LocalDateTime getCreateTime() {
        return createTime;
    }

    public void setCreateTime(LocalDateTime createTime) {
        this.createTime = createTime;
    }

    public LocalDateTime getUpdateTime() {
        return updateTime;
    }

    public void setUpdateTime(LocalDateTime updateTime) {
        this.updateTime = updateTime;
    }

    public enum QRCodeType {
        TEXT("文本"),
        URL("网址"),
        BUSINESS_CARD("名片"),
        WIFI("WiFi"),
        EMAIL("邮件"),
        SMS("短信");

        private final String description;

        QRCodeType(String description) {
            this.description = description;
        }

        public String getDescription() {
            return description;
        }
    }
}
