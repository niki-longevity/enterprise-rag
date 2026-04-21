package com.example.ChainTests;

import com.example.dto.request.ChatRequest;
import com.example.dto.response.ChatResponse;
import com.example.service.ChatService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

/**
 * 链路测试类
 */
@SpringBootTest
public class ChatControllerTest {

    @Autowired
    private ChatService chatService;

    /**
     * 测试链路一：政策问答
     * 从Java端ChatService -> Python Agent服务 -> RAG检索 -> 返回结果
     */
    @Test
    public void testPolicyQaFlow() {
        ChatRequest request = new ChatRequest();
        request.setUserId("user001");
        request.setMessage("婚假能请几天？");
        request.setSessionId("test_session_001");

        ChatResponse response = chatService.chat(request);

        System.out.println("用户问题: " + request.getMessage());
        System.out.println("助手回复: " + response.getReply());
        System.out.println("会话ID: " + response.getSessionId());
    }
}
