package com.example.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 资源实体类
 */
@Data
@TableName("resource")
public class Resource {

    @TableId(type = IdType.AUTO)
    private Long id;

    // 资源名称
    private String name;

    // 类型: PROJECTOR, LAPTOP, ROOM, LICENSE
    private String type;

    // 状态: AVAILABLE, IN_USE, MAINTENANCE
    private String status;

    // 描述
    private String description;

    // 创建时间
    private LocalDateTime createdAt;

    // 更新时间
    private LocalDateTime updatedAt;
}
