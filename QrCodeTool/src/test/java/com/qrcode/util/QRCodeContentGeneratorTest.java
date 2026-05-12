package com.qrcode.util;

import org.junit.Test;

import static org.junit.Assert.*;

public class QRCodeContentGeneratorTest {

    @Test
    public void testGenerateWiFiContent() {
        String ssid = "MyWiFi";
        String password = "password123";
        String encryption = "WPA";
        boolean hidden = false;
        
        String result = QRCodeContentGenerator.generateWiFiContent(ssid, password, encryption, hidden);
        
        assertNotNull("WiFi内容不应为null", result);
        assertTrue("应包含SSID", result.contains("S:MyWiFi"));
        assertTrue("应包含密码", result.contains("P:password123"));
        assertTrue("应包含加密类型", result.contains("T:WPA"));
        assertTrue("应以WIFI:开头", result.startsWith("WIFI:"));
    }

    @Test
    public void testGenerateWiFiContentWithoutPassword() {
        String ssid = "OpenWiFi";
        String password = "";
        String encryption = "nopass";
        boolean hidden = false;
        
        String result = QRCodeContentGenerator.generateWiFiContent(ssid, password, encryption, hidden);
        
        assertNotNull("WiFi内容不应为null", result);
        assertTrue("应包含SSID", result.contains("S:OpenWiFi"));
        assertFalse("不应包含密码", result.contains("P:"));
    }

    @Test
    public void testGenerateWiFiContentWithHidden() {
        String ssid = "HiddenWiFi";
        String password = "secret";
        String encryption = "WPA2";
        boolean hidden = true;
        
        String result = QRCodeContentGenerator.generateWiFiContent(ssid, password, encryption, hidden);
        
        assertNotNull("WiFi内容不应为null", result);
        assertTrue("应包含隐藏标志", result.contains("H:true"));
    }

    @Test
    public void testGenerateWiFiContentWithSpecialChars() {
        String ssid = "WiFi;Name:Test";
        String password = "pass;word:123";
        String encryption = "WPA";
        boolean hidden = false;
        
        String result = QRCodeContentGenerator.generateWiFiContent(ssid, password, encryption, hidden);
        
        assertNotNull("WiFi内容不应为null", result);
        assertTrue("特殊字符应被转义", result.contains("S:WiFi\\;Name\\:Test"));
    }

    @Test
    public void testGenerateBusinessCardContent() {
        String name = "张三";
        String company = "科技有限公司";
        String title = "高级工程师";
        String phone = "010-12345678";
        String mobile = "13800138000";
        String email = "zhangsan@example.com";
        String website = "https://www.example.com";
        String address = "北京市朝阳区";
        
        String result = QRCodeContentGenerator.generateBusinessCardContent(
            name, company, title, phone, mobile, email, website, address
        );
        
        assertNotNull("名片内容不应为null", result);
        assertTrue("应以BEGIN:VCARD开头", result.startsWith("BEGIN:VCARD"));
        assertTrue("应以END:VCARD结尾", result.endsWith("END:VCARD"));
        assertTrue("应包含姓名", result.contains("FN:张三"));
        assertTrue("应包含公司", result.contains("ORG:科技有限公司"));
        assertTrue("应包含邮箱", result.contains("EMAIL:zhangsan@example.com"));
        assertTrue("应包含手机号", result.contains("TEL;TYPE=CELL,VOICE:13800138000"));
    }

    @Test
    public void testGenerateBusinessCardContentWithPartialInfo() {
        String name = "李四";
        String company = "";
        String title = "";
        String phone = "";
        String mobile = "";
        String email = "lisi@example.com";
        String website = "";
        String address = "";
        
        String result = QRCodeContentGenerator.generateBusinessCardContent(
            name, company, title, phone, mobile, email, website, address
        );
        
        assertNotNull("名片内容不应为null", result);
        assertTrue("应包含姓名", result.contains("FN:李四"));
        assertTrue("应包含邮箱", result.contains("EMAIL:lisi@example.com"));
        assertFalse("不应包含空的公司", result.contains("ORG:"));
    }

    @Test
    public void testGenerateEmailContent() {
        String email = "test@example.com";
        String subject = "测试邮件主题";
        String body = "这是邮件正文内容";
        
        String result = QRCodeContentGenerator.generateEmailContent(email, subject, body);
        
        assertNotNull("邮件内容不应为null", result);
        assertTrue("应以mailto:开头", result.startsWith("mailto:"));
        assertTrue("应包含邮箱地址", result.contains("test@example.com"));
        assertTrue("应包含主题", result.contains("subject="));
        assertTrue("应包含正文", result.contains("body="));
    }

    @Test
    public void testGenerateEmailContentWithoutSubjectAndBody() {
        String email = "simple@example.com";
        String subject = "";
        String body = "";
        
        String result = QRCodeContentGenerator.generateEmailContent(email, subject, body);
        
        assertNotNull("邮件内容不应为null", result);
        assertEquals("simple@example.com邮箱应直接使用", "mailto:simple@example.com", result);
    }

    @Test
    public void testGenerateSMSContent() {
        String phone = "13800138000";
        String message = "这是短信内容";
        
        String result = QRCodeContentGenerator.generateSMSContent(phone, message);
        
        assertNotNull("短信内容不应为null", result);
        assertTrue("应以SMSTO:开头", result.startsWith("SMSTO:"));
        assertTrue("应包含手机号", result.contains("13800138000"));
        assertTrue("应包含消息内容", result.contains("这是短信内容"));
    }

    @Test
    public void testGenerateSMSContentWithoutMessage() {
        String phone = "13900139000";
        String message = "";
        
        String result = QRCodeContentGenerator.generateSMSContent(phone, message);
        
        assertNotNull("短信内容不应为null", result);
        assertEquals("SMSTO:13900139000", result);
    }

    @Test
    public void testGenerateWiFiContentNullValues() {
        String result = QRCodeContentGenerator.generateWiFiContent(null, null, "WPA", false);
        
        assertNotNull("结果不应为null", result);
        assertTrue("空的SSID应正确处理", result.contains("S:"));
    }

    @Test
    public void testGenerateBusinessCardContentNullValues() {
        String result = QRCodeContentGenerator.generateBusinessCardContent(
            null, null, null, null, null, null, null, null
        );
        
        assertNotNull("名片内容不应为null", result);
        assertTrue("应以BEGIN:VCARD开头", result.startsWith("BEGIN:VCARD"));
    }
}
