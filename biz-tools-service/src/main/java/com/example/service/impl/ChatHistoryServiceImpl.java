package com.example.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.example.entity.ChatHistory;
import com.example.mapper.ChatHistoryMapper;
import com.example.service.ChatHistoryService;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 对话历史服务实现类
 */
@Service
public class ChatHistoryServiceImpl implements ChatHistoryService {

    @Autowired
    private ChatHistoryMapper chatHistoryMapper;

    @Override
    public ChatHistory getById(Long id) {
        return chatHistoryMapper.selectById(id);
    }

    @Override
    public List<ChatHistory> listBySessionId(String sessionId) {
        LambdaQueryWrapper<ChatHistory> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ChatHistory::getSessionId, sessionId)
               .orderByAsc(ChatHistory::getCreatedAt);
        return chatHistoryMapper.selectList(wrapper);
    }

    @Override
    public List<String> listSessionIdsByUserId(String userId) {
        LambdaQueryWrapper<ChatHistory> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ChatHistory::getUserId, userId)
               .select(ChatHistory::getSessionId)
               .groupBy(ChatHistory::getSessionId)
               .orderByDesc(ChatHistory::getCreatedAt);
        List<ChatHistory> histories = chatHistoryMapper.selectList(wrapper);
        return histories.stream()
                .map(ChatHistory::getSessionId)
                .distinct()
                .collect(Collectors.toList());
    }

    @Override
    public boolean save(ChatHistory chatHistory) {
        return chatHistoryMapper.insert(chatHistory) > 0;
    }

    @Override
    public boolean saveBatch(List<ChatHistory> chatHistories) {
        for (ChatHistory history : chatHistories) {
            chatHistoryMapper.insert(history);
        }
        return true;
    }

    @Override
    public boolean removeBySessionId(String sessionId) {
        LambdaQueryWrapper<ChatHistory> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ChatHistory::getSessionId, sessionId);
        return chatHistoryMapper.delete(wrapper) > 0;
    }
}
