package com.example.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.entity.Policy;
import org.apache.ibatis.annotations.Mapper;

/**
 * 政策文档Mapper接口
 */
@Mapper
public interface PolicyMapper extends BaseMapper<Policy> {
}
