package com.example.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.example.entity.Ticket;
import com.example.mapper.TicketMapper;
import com.example.service.TicketService;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import java.time.LocalDateTime;
import java.util.List;

/**
 * 工单服务实现类
 */
@Service
public class TicketServiceImpl implements TicketService {

    @Autowired
    private TicketMapper ticketMapper;

    @Override
    public Ticket getById(Long id) {
        return ticketMapper.selectById(id);
    }

    @Override
    public Ticket getByTicketNo(String ticketNo) {
        LambdaQueryWrapper<Ticket> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Ticket::getTicketNo, ticketNo);
        return ticketMapper.selectOne(wrapper);
    }

    @Override
    public List<Ticket> listByUserId(String userId) {
        LambdaQueryWrapper<Ticket> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Ticket::getUserId, userId)
               .orderByDesc(Ticket::getCreatedAt);
        return ticketMapper.selectList(wrapper);
    }

    @Override
    public List<Ticket> listByStatus(String status) {
        LambdaQueryWrapper<Ticket> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Ticket::getStatus, status)
               .orderByDesc(Ticket::getCreatedAt);
        return ticketMapper.selectList(wrapper);
    }

    @Override
    public List<Ticket> listByUserIdAndStatus(String userId, String status) {
        LambdaQueryWrapper<Ticket> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Ticket::getUserId, userId)
               .eq(Ticket::getStatus, status)
               .orderByDesc(Ticket::getCreatedAt);
        return ticketMapper.selectList(wrapper);
    }

    @Override
    public Ticket createTicket(Ticket ticket) {
        // 生成工单号（简化版：TK + 时间戳）
        String ticketNo = "TK" + System.currentTimeMillis();
        ticket.setTicketNo(ticketNo);
        ticket.setStatus("PENDING");
        ticketMapper.insert(ticket);
        return ticket;
    }

    @Override
    public boolean updateById(Ticket ticket) {
        return ticketMapper.updateById(ticket) > 0;
    }

    @Override
    public boolean approveTicket(Long id, String approvedBy) {
        Ticket ticket = ticketMapper.selectById(id);
        if (ticket == null) {
            return false;
        }
        ticket.setStatus("APPROVED");
        ticket.setApprovedBy(approvedBy);
        ticket.setApprovedAt(LocalDateTime.now());
        return ticketMapper.updateById(ticket) > 0;
    }

    @Override
    public boolean rejectTicket(Long id, String approvedBy) {
        Ticket ticket = ticketMapper.selectById(id);
        if (ticket == null) {
            return false;
        }
        ticket.setStatus("REJECTED");
        ticket.setApprovedBy(approvedBy);
        ticket.setApprovedAt(LocalDateTime.now());
        return ticketMapper.updateById(ticket) > 0;
    }

    @Override
    public boolean removeById(Long id) {
        return ticketMapper.deleteById(id) > 0;
    }
}
