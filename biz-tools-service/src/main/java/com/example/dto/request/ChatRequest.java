package com.example.dto.request;

import lombok.Data;

/**
 * 对话请求DTO
 */
@Data
public class ChatRequest {

    // 用户ID
    private String userId;

    // 消息内容
    private String message;

    // 会话ID（可选，用于会话续传）
    private String sessionId;
}
