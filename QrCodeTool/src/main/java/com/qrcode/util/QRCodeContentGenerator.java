package com.qrcode.util;

import java.util.StringJoiner;

public class QRCodeContentGenerator {

    public static String generateWiFiContent(String ssid, String password, String encryptionType, boolean hidden) {
        StringJoiner joiner = new StringJoiner(";");
        joiner.add("WIFI:T:" + encryptionType);
        joiner.add("S:" + escapeWiFiSpecialChars(ssid));
        if (password != null && !password.isEmpty()) {
            joiner.add("P:" + escapeWiFiSpecialChars(password));
        }
        if (hidden) {
            joiner.add("H:true");
        }
        joiner.add(";");
        return joiner.toString();
    }

    private static String escapeWiFiSpecialChars(String value) {
        if (value == null) {
            return "";
        }
        return value.replace("\\", "\\\\")
                    .replace(";", "\\;")
                    .replace(":", "\\:")
                    .replace(",", "\\,")
                    .replace("\"", "\\\"");
    }

    public static String generateBusinessCardContent(
            String name,
            String company,
            String title,
            String phone,
            String mobile,
            String email,
            String website,
            String address
    ) {
        StringBuilder vcard = new StringBuilder();
        vcard.append("BEGIN:VCARD\n");
        vcard.append("VERSION:3.0\n");
        
        if (name != null && !name.isEmpty()) {
            vcard.append("FN:").append(name).append("\n");
            String[] nameParts = name.split(" ", 2);
            if (nameParts.length == 2) {
                vcard.append("N:").append(nameParts[1]).append(";").append(nameParts[0]).append(";;;\n");
            } else {
                vcard.append("N:").append(name).append(";;;;\n");
            }
        }
        
        if (company != null && !company.isEmpty()) {
            vcard.append("ORG:").append(company).append("\n");
        }
        
        if (title != null && !title.isEmpty()) {
            vcard.append("TITLE:").append(title).append("\n");
        }
        
        if (phone != null && !phone.isEmpty()) {
            vcard.append("TEL;TYPE=WORK,VOICE:").append(phone).append("\n");
        }
        
        if (mobile != null && !mobile.isEmpty()) {
            vcard.append("TEL;TYPE=CELL,VOICE:").append(mobile).append("\n");
        }
        
        if (email != null && !email.isEmpty()) {
            vcard.append("EMAIL:").append(email).append("\n");
        }
        
        if (website != null && !website.isEmpty()) {
            vcard.append("URL:").append(website).append("\n");
        }
        
        if (address != null && !address.isEmpty()) {
            vcard.append("ADR;TYPE=WORK:;;").append(address).append(";;;;\n");
        }
        
        vcard.append("END:VCARD");
        
        return vcard.toString();
    }

    public static String generateEmailContent(String email, String subject, String body) {
        StringBuilder sb = new StringBuilder();
        sb.append("mailto:").append(email);
        
        boolean hasParams = false;
        if (subject != null && !subject.isEmpty()) {
            sb.append("?subject=").append(encodeURL(subject));
            hasParams = true;
        }
        
        if (body != null && !body.isEmpty()) {
            sb.append(hasParams ? "&body=" : "?body=").append(encodeURL(body));
        }
        
        return sb.toString();
    }

    public static String generateSMSContent(String phone, String message) {
        StringBuilder sb = new StringBuilder();
        sb.append("SMSTO:").append(phone);
        
        if (message != null && !message.isEmpty()) {
            sb.append(":").append(message);
        }
        
        return sb.toString();
    }

    private static String encodeURL(String value) {
        try {
            return java.net.URLEncoder.encode(value, "UTF-8")
                    .replace("+", "%20");
        } catch (Exception e) {
            return value;
        }
    }
}
