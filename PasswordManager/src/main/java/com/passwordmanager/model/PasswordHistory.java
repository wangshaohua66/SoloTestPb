package com.passwordmanager.model;

import java.io.Serializable;
import java.time.LocalDateTime;

public class PasswordHistory implements Serializable {
    public enum ActionType {
        CREATE("创建"),
        UPDATE("修改"),
        DELETE("删除"),
        IMPORT("导入"),
        AUTO_EXPIRED("自动过期提醒");

        private final String displayName;

        ActionType(String displayName) {
            this.displayName = displayName;
        }

        public String getDisplayName() {
            return displayName;
        }
    }

    private String id;
    private String entryId;
    private String oldPassword;
    private LocalDateTime changedAt;
    private ActionType actionType;

    public PasswordHistory() {
        this.changedAt = LocalDateTime.now();
        this.actionType = ActionType.UPDATE;
    }

    public PasswordHistory(String entryId, String oldPassword) {
        this.entryId = entryId;
        this.oldPassword = oldPassword;
        this.changedAt = LocalDateTime.now();
        this.actionType = ActionType.UPDATE;
    }

    public PasswordHistory(String entryId, String oldPassword, ActionType actionType) {
        this.entryId = entryId;
        this.oldPassword = oldPassword;
        this.changedAt = LocalDateTime.now();
        this.actionType = actionType;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getEntryId() {
        return entryId;
    }

    public void setEntryId(String entryId) {
        this.entryId = entryId;
    }

    public String getOldPassword() {
        return oldPassword;
    }

    public void setOldPassword(String oldPassword) {
        this.oldPassword = oldPassword;
    }

    public LocalDateTime getChangedAt() {
        return changedAt;
    }

    public void setChangedAt(LocalDateTime changedAt) {
        this.changedAt = changedAt;
    }

    public ActionType getActionType() {
        return actionType;
    }

    public void setActionType(ActionType actionType) {
        this.actionType = actionType;
    }
}
