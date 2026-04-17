package com.example.controller;

import com.example.dto.request.ChatRequest;
import com.example.dto.response.ChatResponse;
import com.example.entity.ChatHistory;
import com.example.service.ChatHistoryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 对话接口Controller
 * 提供前端对话相关的API
 */
@RestController
@RequestMapping("/api/chat")
public class ChatController {

    @Autowired
    private ChatHistoryService chatHistoryService;

    /**
     * 发送对话消息
     *
     * @param request 对话请求，包含用户ID、消息内容、会话ID
     * @return 对话响应，包含助手回复、会话ID、附件信息
     */
    @PostMapping
    public ChatResponse chat(@RequestBody ChatRequest request) {
        // TODO: 调用Agent服务
        ChatResponse response = new ChatResponse();
        response.setReply("收到消息：" + request.getMessage());
        response.setSessionId(request.getSessionId() != null ? request.getSessionId() : "sess_" + System.currentTimeMillis());
        return response;
    }

    /**
     * 查询会话历史消息
     *
     * @param sessionId 会话ID
     * @return 历史消息列表
     */
    @GetMapping("/history")
    public List<ChatHistory> getHistory(@RequestParam String sessionId) {
        return chatHistoryService.listBySessionId(sessionId);
    }

    /**
     * 查询用户的会话列表
     *
     * @param userId 用户ID
     * @return 会话ID列表
     */
    @GetMapping("/sessions")
    public List<String> getSessions(@RequestParam String userId) {
        return chatHistoryService.listSessionIdsByUserId(userId);
    }
}
