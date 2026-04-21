package com.example.service.impl;

import com.example.client.AgentClient;
import com.example.dto.request.ChatRequest;
import com.example.dto.response.ChatResponse;
import com.example.entity.ChatHistory;
import com.example.service.ChatHistoryService;
import com.example.service.ChatService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/**
 * 对话服务实现类
 */
@Service
public class ChatServiceImpl implements ChatService {

    @Autowired
    private AgentClient agentClient;

    @Autowired
    private ChatHistoryService chatHistoryService;

    @Override
    public ChatResponse chat(ChatRequest request) {
        String userId = request.getUserId();
        String message = request.getMessage();
        String sessionId = request.getSessionId();

        // 如果sessionId为空，生成新的
        if (sessionId == null || sessionId.isEmpty()) {
            sessionId = "sess_" + System.currentTimeMillis();
        }

        // 1. 保存用户消息到数据库
        ChatHistory userMsg = new ChatHistory();
        userMsg.setUserId(userId);
        userMsg.setSessionId(sessionId);
        userMsg.setRole("USER");
        userMsg.setContent(message);
        chatHistoryService.save(userMsg);

        // 2. 调用Agent服务获取回复
        String reply = agentClient.chat(userId, message, sessionId);

        // 3. 保存助手回复到数据库
        ChatHistory assistantMsg = new ChatHistory();
        assistantMsg.setUserId(userId);
        assistantMsg.setSessionId(sessionId);
        assistantMsg.setRole("ASSISTANT");
        assistantMsg.setContent(reply);
        chatHistoryService.save(assistantMsg);

        // 4. 构建响应
        ChatResponse response = new ChatResponse();
        response.setReply(reply);
        response.setSessionId(sessionId);

        return response;
    }
}
