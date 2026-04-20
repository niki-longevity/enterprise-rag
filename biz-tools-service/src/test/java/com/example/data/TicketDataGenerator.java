package com.example.data;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.example.entity.Ticket;
import com.example.mapper.TicketMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 工单模拟数据生成器
 */
@SpringBootTest
public class TicketDataGenerator {

    @Autowired
    private TicketMapper ticketMapper;

    /**
     * 生成工单表模拟数据
     */
    @Test
    public void generateTicketData() {
        // 清空现有数据
        LambdaQueryWrapper<Ticket> deleteWrapper = new LambdaQueryWrapper<>();
        ticketMapper.delete(deleteWrapper);

        LocalDateTime now = LocalDateTime.now();

        // 待审批工单
        Ticket ticket1 = new Ticket();
        ticket1.setTicketNo("TK20240420001");
        ticket1.setUserId("user_001");
        ticket1.setType("BORROW");
        ticket1.setReason("申请借用投影仪用于部门培训");
        ticket1.setStatus("PENDING");
        ticket1.setCreatedAt(now);
        ticket1.setUpdatedAt(now);
        ticketMapper.insert(ticket1);

        // 已批准工单
        Ticket ticket2 = new Ticket();
        ticket2.setTicketNo("TK20240420002");
        ticket2.setUserId("user_002");
        ticket2.setType("LEAVE");
        ticket2.setReason("申请年假3天，回老家探亲");
        ticket2.setStatus("APPROVED");
        ticket2.setApprovedBy("manager_001");
        ticket2.setApprovedAt(now.minusHours(2));
        ticket2.setCreatedAt(now.minusDays(1));
        ticket2.setUpdatedAt(now.minusHours(2));
        ticketMapper.insert(ticket2);

        // 已拒绝工单
        Ticket ticket3 = new Ticket();
        ticket3.setTicketNo("TK20240420003");
        ticket3.setUserId("user_003");
        ticket3.setType("EXPENSE");
        ticket3.setReason("报销上月差旅费用，票据不齐");
        ticket3.setStatus("REJECTED");
        ticket3.setApprovedBy("finance_001");
        ticket3.setApprovedAt(now.minusHours(1));
        ticket3.setCreatedAt(now.minusDays(2));
        ticket3.setUpdatedAt(now.minusHours(1));
        ticketMapper.insert(ticket3);

        // 借用笔记本工单
        Ticket ticket4 = new Ticket();
        ticket4.setTicketNo("TK20240420004");
        ticket4.setUserId("user_004");
        ticket4.setType("BORROW");
        ticket4.setReason("申请借用笔记本电脑出差使用");
        ticket4.setStatus("APPROVED");
        ticket4.setApprovedBy("manager_002");
        ticket4.setApprovedAt(now.minusMinutes(30));
        ticket4.setCreatedAt(now.minusHours(3));
        ticket4.setUpdatedAt(now.minusMinutes(30));
        ticketMapper.insert(ticket4);

        // 查询统计
        LambdaQueryWrapper<Ticket> pendingWrapper = new LambdaQueryWrapper<>();
        pendingWrapper.eq(Ticket::getStatus, "PENDING");
        long pendingCount = ticketMapper.selectCount(pendingWrapper);

        LambdaQueryWrapper<Ticket> approvedWrapper = new LambdaQueryWrapper<>();
        approvedWrapper.eq(Ticket::getStatus, "APPROVED");
        long approvedCount = ticketMapper.selectCount(approvedWrapper);

        LambdaQueryWrapper<Ticket> rejectedWrapper = new LambdaQueryWrapper<>();
        rejectedWrapper.eq(Ticket::getStatus, "REJECTED");
        long rejectedCount = ticketMapper.selectCount(rejectedWrapper);

        System.out.println("工单模拟数据生成完成！");
        System.out.println("待审批: " + pendingCount + " 条");
        System.out.println("已批准: " + approvedCount + " 条");
        System.out.println("已拒绝: " + rejectedCount + " 条");
        System.out.println("总计: " + (pendingCount + approvedCount + rejectedCount) + " 条");
    }
}
