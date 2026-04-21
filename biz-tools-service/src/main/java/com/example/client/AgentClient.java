package com.example.client;

import com.example.dto.request.ChatRequest;
import com.example.dto.response.ChatResponse;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

/**
 * Agent服务客户端
 * 调用Agent服务的HTTP客户端
 */
@Component
public class AgentClient {

    private final WebClient webClient;
    private final ObjectMapper objectMapper;

    public AgentClient(
            @Value("${agent.service.url:http://localhost:8001}") String agentServiceUrl,
            ObjectMapper objectMapper
    ) {
        this.webClient = WebClient.create(agentServiceUrl);
        this.objectMapper = objectMapper;
    }

    /**
     * 调用Agent服务进行对话
     *
     * @param userId 用户ID
     * @param message 用户消息
     * @param sessionId 会话ID
     * @return Agent的回复
     */
    public String chat(String userId, String message, String sessionId) {
        // 构建请求体
        ChatRequest request = new ChatRequest();
        request.setUserId(userId);
        request.setMessage(message);
        request.setSessionId(sessionId);

        try {
            // 调用Python Agent服务
            String response = webClient.post()
                    .uri("/api/agent/chat")
                    .bodyValue(request)
                    .retrieve()
                    .bodyToMono(String.class)
                    .block();

            // 解析响应，提取reply字段
            if (response != null) {
                JsonNode jsonNode = objectMapper.readTree(response);
                if (jsonNode.has("reply")) {
                    return jsonNode.get("reply").asText();
                }
            }
            return "抱歉，Agent服务返回格式异常。";
        } catch (Exception e) {
            e.printStackTrace();
            return "抱歉，调用Agent服务失败：" + e.getMessage();
        }
    }
}
