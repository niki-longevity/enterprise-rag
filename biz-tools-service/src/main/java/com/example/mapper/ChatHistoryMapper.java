package com.example.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.entity.ChatHistory;
import org.apache.ibatis.annotations.Mapper;

/**
 * 对话历史Mapper接口
 */
@Mapper
public interface ChatHistoryMapper extends BaseMapper<ChatHistory> {
}
