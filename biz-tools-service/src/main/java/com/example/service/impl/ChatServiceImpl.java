package com.example.service.impl;

import com.example.client.AgentClient;
import com.example.dto.request.ChatRequest;
import com.example.dto.response.ChatResponse;
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

    @Override
    public ChatResponse chat(ChatRequest request) {
        String userId = request.getUserId();
        String message = request.getMessage();
        String sessionId = request.getSessionId();

        if (sessionId == null || sessionId.isEmpty()) {
            sessionId = "sess_" + System.currentTimeMillis();
        }

        String reply = agentClient.chat(userId, message, sessionId);

        ChatResponse response = new ChatResponse();
        response.setReply(reply);
        response.setSessionId(sessionId);

        return response;
    }
}
