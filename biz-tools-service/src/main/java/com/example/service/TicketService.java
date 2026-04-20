package com.example.service;

import com.example.entity.Ticket;
import java.util.List;

/**
 * 工单服务接口
 * 提供工单的创建、查询、审批等功能
 */
public interface TicketService {

    /**
     * 根据ID查询工单
     */
    Ticket getById(Long id);

    /**
     * 根据工单号查询工单
     */
    Ticket getByTicketNo(String ticketNo);

    /**
     * 查询用户的所有工单
     */
    List<Ticket> listByUserId(String userId);

    /**
     * 根据状态查询工单
     */
    List<Ticket> listByStatus(String status);

    /**
     * 查询用户指定状态的工单
     */
    List<Ticket> listByUserIdAndStatus(String userId, String status);

    /**
     * 创建工单
     */
    Ticket createTicket(Ticket ticket);

    /**
     * 更新工单
     */
    boolean updateById(Ticket ticket);

    /**
     * 审批工单
     */
    boolean approveTicket(Long id, String approvedBy);

    /**
     * 拒绝工单
     */
    boolean rejectTicket(Long id, String approvedBy);

    /**
     * 根据工单号审批工单
     */
    Ticket approveTicket(String ticketNo, boolean approved, String approvedBy);

    /**
     * 删除工单
     */
    boolean removeById(Long id);
}
