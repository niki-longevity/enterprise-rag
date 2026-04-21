-- 企业内部员工助手智能体 - 数据库表结构
-- 创建时间: 2024-04-18

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS db_ea
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE db_ea   ;

--  对话历史表 (chat_history)
CREATE TABLE IF NOT EXISTS chat_history (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    session_id VARCHAR(64) NOT NULL COMMENT '会话ID',
    user_id VARCHAR(50) NOT NULL COMMENT '用户ID',
    role VARCHAR(20) COMMENT '角色: USER, ASSISTANT',
    content TEXT NOT NULL COMMENT '消息内容',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话历史表';
