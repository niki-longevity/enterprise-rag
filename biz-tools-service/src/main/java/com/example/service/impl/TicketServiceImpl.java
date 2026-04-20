package com.example.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.example.entity.Ticket;
import com.example.mapper.TicketMapper;
import com.example.service.TicketService;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Random;

/**
 * 工单服务实现类
 * 提供工单的创建、查询、审批等功能，包含70%自动审批通过率的模拟审批逻辑
 */
@Service
public class TicketServiceImpl implements TicketService {

    @Autowired
    private TicketMapper ticketMapper;

    private final Random random = new Random();

    /**
     * 根据ID查询工单
     *
     * @param id 工单ID
     * @return 工单信息，不存在则返回null
     */
    @Override
    public Ticket getById(Long id) {
        return ticketMapper.selectById(id);
    }

    /**
     * 根据工单号查询工单
     *
     * @param ticketNo 工单号
     * @return 工单信息，不存在则返回null
     */
    @Override
    public Ticket getByTicketNo(String ticketNo) {
        LambdaQueryWrapper<Ticket> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Ticket::getTicketNo, ticketNo);
        return ticketMapper.selectOne(wrapper);
    }

    /**
     * 查询用户的所有工单
     *
     * @param userId 用户ID
     * @return 工单列表，按创建时间倒序排列
     */
    @Override
    public List<Ticket> listByUserId(String userId) {
        LambdaQueryWrapper<Ticket> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Ticket::getUserId, userId)
               .orderByDesc(Ticket::getCreatedAt);
        return ticketMapper.selectList(wrapper);
    }

    /**
     * 根据状态查询工单
     *
     * @param status 工单状态（PENDING, APPROVED, REJECTED）
     * @return 工单列表，按创建时间倒序排列
     */
    @Override
    public List<Ticket> listByStatus(String status) {
        LambdaQueryWrapper<Ticket> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Ticket::getStatus, status)
               .orderByDesc(Ticket::getCreatedAt);
        return ticketMapper.selectList(wrapper);
    }

    /**
     * 查询用户指定状态的工单
     *
     * @param userId 用户ID
     * @param status 工单状态
     * @return 工单列表，按创建时间倒序排列
     */
    @Override
    public List<Ticket> listByUserIdAndStatus(String userId, String status) {
        LambdaQueryWrapper<Ticket> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Ticket::getUserId, userId)
               .eq(Ticket::getStatus, status)
               .orderByDesc(Ticket::getCreatedAt);
        return ticketMapper.selectList(wrapper);
    }

    /**
     * 创建工单
     * 自动生成工单号，并触发70%通过率的自动审批
     *
     * @param ticket 工单信息
     * @return 创建后的工单（包含审批结果）
     */
    @Override
    public Ticket createTicket(Ticket ticket) {
        // 生成工单号（简化版：TK + 时间戳）
        String ticketNo = "TK" + System.currentTimeMillis();
        ticket.setTicketNo(ticketNo);
        ticket.setStatus("PENDING");
        ticket.setCreatedAt(LocalDateTime.now());
        ticket.setUpdatedAt(LocalDateTime.now());
        ticketMapper.insert(ticket);

        // 模拟自动审批：70%通过率
        autoApproveTicket(ticket);

        return ticketMapper.selectById(ticket.getId());
    }

    /**
     * 模拟自动审批（70%通过率）
     *
     * @param ticket 工单信息
     */
    private void autoApproveTicket(Ticket ticket) {
        boolean approved = random.nextDouble() < 0.7;
        String status = approved ? "APPROVED" : "REJECTED";
        ticket.setStatus(status);
        ticket.setApprovedBy("auto_approver");
        ticket.setApprovedAt(LocalDateTime.now());
        ticket.setUpdatedAt(LocalDateTime.now());
        ticketMapper.updateById(ticket);
    }

    /**
     * 根据工单号审批工单
     *
     * @param ticketNo 工单号
     * @param approved 是否批准
     * @param approvedBy 审批人
     * @return 审批后的工单，不存在则返回null
     */
    public Ticket approveTicket(String ticketNo, boolean approved, String approvedBy) {
        Ticket ticket = getByTicketNo(ticketNo);
        if (ticket == null) {
            return null;
        }
        ticket.setStatus(approved ? "APPROVED" : "REJECTED");
        ticket.setApprovedBy(approvedBy);
        ticket.setApprovedAt(LocalDateTime.now());
        ticket.setUpdatedAt(LocalDateTime.now());
        ticketMapper.updateById(ticket);
        return ticket;
    }

    /**
     * 更新工单
     *
     * @param ticket 工单信息（需包含ID）
     * @return 是否成功
     */
    @Override
    public boolean updateById(Ticket ticket) {
        ticket.setUpdatedAt(LocalDateTime.now());
        return ticketMapper.updateById(ticket) > 0;
    }

    /**
     * 批准工单
     *
     * @param id 工单ID
     * @param approvedBy 审批人
     * @return 是否成功
     */
    @Override
    public boolean approveTicket(Long id, String approvedBy) {
        Ticket ticket = ticketMapper.selectById(id);
        if (ticket == null) {
            return false;
        }
        ticket.setStatus("APPROVED");
        ticket.setApprovedBy(approvedBy);
        ticket.setApprovedAt(LocalDateTime.now());
        ticket.setUpdatedAt(LocalDateTime.now());
        return ticketMapper.updateById(ticket) > 0;
    }

    /**
     * 拒绝工单
     *
     * @param id 工单ID
     * @param approvedBy 审批人
     * @return 是否成功
     */
    @Override
    public boolean rejectTicket(Long id, String approvedBy) {
        Ticket ticket = ticketMapper.selectById(id);
        if (ticket == null) {
            return false;
        }
        ticket.setStatus("REJECTED");
        ticket.setApprovedBy(approvedBy);
        ticket.setApprovedAt(LocalDateTime.now());
        ticket.setUpdatedAt(LocalDateTime.now());
        return ticketMapper.updateById(ticket) > 0;
    }

    /**
     * 删除工单
     *
     * @param id 工单ID
     * @return 是否成功
     */
    @Override
    public boolean removeById(Long id) {
        return ticketMapper.deleteById(id) > 0;
    }
}
