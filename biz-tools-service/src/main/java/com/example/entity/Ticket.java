package com.example.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 工单实体类
 */
@Data
@TableName("ticket")
public class Ticket {

    @TableId(type = IdType.AUTO)
    private Long id;

    // 工单号
    private String ticketNo;

    // 申请人ID
    private String userId;

    // 工单类型
    private String type;

    // 申请原因
    private String reason;

    // 状态: PENDING, APPROVED, REJECTED
    private String status;

    // 扩展字段(JSON)
    private String metadata;

    // 审批人
    private String approvedBy;

    // 审批时间
    private LocalDateTime approvedAt;

    // 创建时间
    private LocalDateTime createdAt;

    // 更新时间
    private LocalDateTime updatedAt;
}
