package com.example.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.entity.Ticket;
import org.apache.ibatis.annotations.Mapper;

/**
 * 工单Mapper接口
 */
@Mapper
public interface TicketMapper extends BaseMapper<Ticket> {
}
