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

    /**
     * 根据ID查询对话历史
     *
     * @param id 历史记录ID
     * @return 对话历史信息，不存在则返回null
     */
    @Override
    public ChatHistory getById(Long id) {
        return chatHistoryMapper.selectById(id);
    }

    /**
     * 查询会话的历史消息
     *
     * @param sessionId 会话ID
     * @return 历史消息列表，按创建时间正序排列
     */
    @Override
    public List<ChatHistory> listBySessionId(String sessionId) {
        LambdaQueryWrapper<ChatHistory> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ChatHistory::getSessionId, sessionId)
               .orderByAsc(ChatHistory::getCreatedAt);
        return chatHistoryMapper.selectList(wrapper);
    }

    /**
     * 查询用户的会话列表
     *
     * @param userId 用户ID
     * @return 会话ID列表，按最后消息时间倒序排列
     */
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

    /**
     * 保存对话历史
     *
     * @param chatHistory 对话历史信息
     * @return 是否成功
     */
    @Override
    public boolean save(ChatHistory chatHistory) {
        return chatHistoryMapper.insert(chatHistory) > 0;
    }

    /**
     * 批量保存对话历史
     *
     * @param chatHistories 对话历史列表
     * @return 是否成功
     */
    @Override
    public boolean saveBatch(List<ChatHistory> chatHistories) {
        for (ChatHistory history : chatHistories) {
            chatHistoryMapper.insert(history);
        }
        return true;
    }

    /**
     * 删除会话的所有历史消息
     *
     * @param sessionId 会话ID
     * @return 是否成功
     */
    @Override
    public boolean removeBySessionId(String sessionId) {
        LambdaQueryWrapper<ChatHistory> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(ChatHistory::getSessionId, sessionId);
        return chatHistoryMapper.delete(wrapper) > 0;
    }
}
