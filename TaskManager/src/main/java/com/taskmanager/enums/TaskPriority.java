package com.taskmanager.enums;

public enum TaskPriority {
    HIGH("高", 1),
    MEDIUM("中", 2),
    LOW("低", 3);

    private final String description;
    private final int order;

    TaskPriority(String description, int order) {
        this.description = description;
        this.order = order;
    }

    public String getDescription() {
        return description;
    }

    public int getOrder() {
        return order;
    }
}
