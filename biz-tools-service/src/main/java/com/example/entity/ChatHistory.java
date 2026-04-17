package com.example.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 对话历史实体类
 */
@Data
@TableName("chat_history")
public class ChatHistory {

    @TableId(type = IdType.AUTO)
    private Long id;

    // 会话ID
    private String sessionId;

    // 用户ID
    private String userId;

    // 角色: USER, ASSISTANT
    private String role;

    // 消息内容
    private String content;

    // 创建时间
    private LocalDateTime createdAt;
}
