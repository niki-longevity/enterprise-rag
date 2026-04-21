package com.example.service;

import com.example.dto.request.ChatRequest;
import com.example.dto.response.ChatResponse;

/**
 * 对话服务接口
 * 处理对话相关的业务逻辑
 */
public interface ChatService {

    /**
     * 处理用户对话请求
     *
     * @param request 对话请求
     * @return 对话响应
     */
    ChatResponse chat(ChatRequest request);
}
