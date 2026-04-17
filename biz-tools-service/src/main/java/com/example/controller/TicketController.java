package com.example.controller;

import com.example.entity.Ticket;
import com.example.service.TicketService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 工单接口Controller
 * 提供前端工单查询相关的API
 */
@RestController
@RequestMapping("/api/tickets")
public class TicketController {

    @Autowired
    private TicketService ticketService;

    /**
     * 查询用户工单列表
     *
     * @param userId 用户ID
     * @param status 状态（可选）
     * @return 工单列表
     */
    @GetMapping
    public List<Ticket> listUserTickets(
            @RequestParam String userId,
            @RequestParam(required = false) String status) {
        if (status != null) {
            return ticketService.listByUserIdAndStatus(userId, status);
        }
        return ticketService.listByUserId(userId);
    }

    /**
     * 根据工单号查询工单详情
     *
     * @param ticketNo 工单号
     * @return 工单详情
     */
    @GetMapping("/no/{ticketNo}")
    public Ticket getByTicketNo(@PathVariable String ticketNo) {
        return ticketService.getByTicketNo(ticketNo);
    }

    /**
     * 根据ID查询工单详情
     *
     * @param id 工单ID
     * @return 工单详情
     */
    @GetMapping("/{id}")
    public Ticket getById(@PathVariable Long id) {
        return ticketService.getById(id);
    }
}
