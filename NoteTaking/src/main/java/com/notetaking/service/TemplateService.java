package com.notetaking.service;

import com.notetaking.model.Note;
import com.notetaking.model.Template;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;

public class TemplateService {
    private static final Logger logger = LoggerFactory.getLogger(TemplateService.class);

    private final FileStorageService storageService;

    public TemplateService() {
        this.storageService = new FileStorageService();
        initializeDefaultTemplates();
    }

    public TemplateService(FileStorageService storageService) {
        this.storageService = storageService;
        initializeDefaultTemplates();
    }

    private void initializeDefaultTemplates() {
        List<Template> existing = getAllTemplates();
        if (existing.isEmpty()) {
            createDefaultTemplates();
        }
    }

    private void createDefaultTemplates() {
        Template meetingTemplate = new Template();
        meetingTemplate.setName("会议记录");
        meetingTemplate.setDescription("用于记录会议内容的模板");
        meetingTemplate.setContent("# 会议记录\n\n## 会议信息\n- 日期：\n- 参会人员：\n- 会议主题：\n\n## 会议议程\n1. \n2. \n3. \n\n## 会议内容\n\n### 议题一\n\n### 议题二\n\n## 行动项\n- [ ] \n- [ ] \n\n## 下次会议\n- 时间：\n- 议题：");
        meetingTemplate.setSystem(true);
        saveTemplate(meetingTemplate);

        Template dailyTemplate = new Template();
        dailyTemplate.setName("日常记录");
        dailyTemplate.setDescription("用于记录日常工作或生活的模板");
        dailyTemplate.setContent("# 日常记录\n\n## 日期\n\n## 今日目标\n- [ ] \n- [ ] \n\n## 完成情况\n\n## 遇到的问题\n\n## 明日计划\n- \n- \n\n## 备注");
        dailyTemplate.setSystem(true);
        saveTemplate(dailyTemplate);

        Template projectTemplate = new Template();
        projectTemplate.setName("项目文档");
        projectTemplate.setDescription("用于项目相关的文档模板");
        projectTemplate.setContent("# 项目名称\n\n## 项目概述\n\n## 目标\n\n## 里程碑\n| 阶段 | 时间 | 状态 |\n| --- | --- | --- |\n| 阶段一 |  |  |\n| 阶段二 |  |  |\n\n## 团队成员\n\n## 相关资源\n- \n- \n\n## 更新日志");
        projectTemplate.setSystem(true);
        saveTemplate(projectTemplate);

        Template noteTemplate = new Template();
        noteTemplate.setName("学习笔记");
        noteTemplate.setDescription("用于学习和知识整理的模板");
        noteTemplate.setContent("# 主题\n\n## 概述\n\n## 核心概念\n\n### 概念一\n\n### 概念二\n\n## 实践示例\n\n```\n代码示例\n```\n\n## 总结\n\n## 相关链接\n- \n- \n\n## 待深入");
        noteTemplate.setSystem(true);
        saveTemplate(noteTemplate);

        logger.info("已创建默认模板");
    }

    public Template createTemplate(String name, String content) {
        Template template = new Template(name, content);
        saveTemplate(template);
        logger.info("创建模板: {} (ID: {})", name, template.getId());
        return template;
    }

    public Template getTemplateById(String id) {
        return storageService.load(id, Template.class, FileStorageService.getTemplatesDir());
    }

    public void saveTemplate(Template template) {
        storageService.save(template.getId(), template, FileStorageService.getTemplatesDir());
    }

    public void updateTemplate(Template template) {
        saveTemplate(template);
        logger.info("更新模板: {} (ID: {})", template.getName(), template.getId());
    }

    public boolean deleteTemplate(String id) {
        Template template = getTemplateById(id);
        if (template != null && template.isSystem()) {
            logger.warn("无法删除系统模板: {}", id);
            return false;
        }
        boolean deleted = storageService.delete(id, FileStorageService.getTemplatesDir());
        if (deleted) {
            logger.info("删除模板: ID: {}", id);
        }
        return deleted;
    }

    public List<Template> getAllTemplates() {
        return storageService.loadAll(Template.class, FileStorageService.getTemplatesDir());
    }

    public List<Template> getUserTemplates() {
        return getAllTemplates().stream()
                .filter(t -> !t.isSystem())
                .collect(java.util.stream.Collectors.toList());
    }

    public List<Template> getSystemTemplates() {
        return getAllTemplates().stream()
                .filter(Template::isSystem)
                .collect(java.util.stream.Collectors.toList());
    }

    public Note createNoteFromTemplate(String templateId) {
        Template template = getTemplateById(templateId);
        if (template == null) {
            return null;
        }
        Note note = template.toNote();
        logger.info("从模板创建笔记: {}", templateId);
        return note;
    }
}
