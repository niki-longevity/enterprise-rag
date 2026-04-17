package com.example.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import java.time.LocalDateTime;

/**
 * 政策文档实体类
 */
@Data
@TableName("policy")
public class Policy {

    @TableId(type = IdType.AUTO)
    private Long id;

    // 文档标题
    private String title;

    // 文档内容
    private String content;

    // 分类: IT, HR, ADMIN
    private String category;

    // 原文件路径
    private String filePath;

    // 创建时间
    private LocalDateTime createdAt;

    // 更新时间
    private LocalDateTime updatedAt;
}
