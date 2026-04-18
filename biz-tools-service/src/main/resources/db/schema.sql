-- 企业内部员工助手智能体 - 数据库表结构
-- 创建时间: 2024-04-18

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS db_ea
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE db_ea   ;

-- 1. 政策文档表 (policy)
CREATE TABLE IF NOT EXISTS policy (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    title VARCHAR(200) NOT NULL COMMENT '文档标题',
    content TEXT NOT NULL COMMENT '文档内容',
    category VARCHAR(50) COMMENT '分类: IT, HR, ADMIN',
    file_path VARCHAR(500) COMMENT '原文件路径',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='政策文档表';

-- 2. 资源表 (resource)
CREATE TABLE IF NOT EXISTS resource (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    name VARCHAR(100) NOT NULL COMMENT '资源名称',
    type VARCHAR(50) COMMENT '类型: PROJECTOR, LAPTOP, ROOM, LICENSE',
    status VARCHAR(20) COMMENT '状态: AVAILABLE, IN_USE, MAINTENANCE',
    description TEXT COMMENT '描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_type (type),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='资源表';

-- 3. 工单表 (ticket)
CREATE TABLE IF NOT EXISTS ticket (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    ticket_no VARCHAR(32) UNIQUE NOT NULL COMMENT '工单号',
    user_id VARCHAR(50) NOT NULL COMMENT '申请人ID',
    type VARCHAR(50) NOT NULL COMMENT '工单类型',
    reason TEXT COMMENT '申请原因',
    status VARCHAR(20) COMMENT '状态: PENDING, APPROVED, REJECTED',
    metadata JSON COMMENT '扩展字段',
    approved_by VARCHAR(50) COMMENT '审批人',
    approved_at DATETIME COMMENT '审批时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_ticket_no (ticket_no),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工单表';

-- 4. 对话历史表 (chat_history)
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
