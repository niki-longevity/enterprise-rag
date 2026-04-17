package com.example.service;

import com.example.entity.ChatHistory;
import java.util.List;

/**
 * 对话历史服务接口
 * 提供对话历史的保存、查询等功能
 */
public interface ChatHistoryService {

    /**
     * 根据ID查询对话历史
     */
    ChatHistory getById(Long id);

    /**
     * 查询会话的所有历史消息
     */
    List<ChatHistory> listBySessionId(String sessionId);

    /**
     * 查询用户的所有会话
     */
    List<String> listSessionIdsByUserId(String userId);

    /**
     * 保存对话消息
     */
    boolean save(ChatHistory chatHistory);

    /**
     * 批量保存对话消息
     */
    boolean saveBatch(List<ChatHistory> chatHistories);

    /**
     * 删除会话的所有历史
     */
    boolean removeBySessionId(String sessionId);
}
