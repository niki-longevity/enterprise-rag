package com.example.dto.response;

import lombok.Data;
import java.util.List;

/**
 * 对话响应DTO
 */
@Data
public class ChatResponse {

    // 助手回复
    private String reply;

    // 会话ID
    private String sessionId;

    // 附件信息（政策文档等）
    private List<Attachment> attachments;

    @Data
    public static class Attachment {
        // 类型：POLICY, RESOURCE, TICKET
        private String type;

        // 标题
        private String title;
    }
}
