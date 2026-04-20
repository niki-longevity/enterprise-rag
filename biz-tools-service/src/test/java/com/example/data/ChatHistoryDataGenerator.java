package com.example.data;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.example.entity.ChatHistory;
import com.example.mapper.ChatHistoryMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.time.LocalDateTime;

/**
 * 对话历史模拟数据生成器
 */
@SpringBootTest
public class ChatHistoryDataGenerator {

    @Autowired
    private ChatHistoryMapper chatHistoryMapper;

    /**
     * 生成对话历史表模拟数据
     */
    @Test
    public void generateChatHistoryData() {
        // 清空现有数据
        LambdaQueryWrapper<ChatHistory> deleteWrapper = new LambdaQueryWrapper<>();
        chatHistoryMapper.delete(deleteWrapper);

        LocalDateTime now = LocalDateTime.now();

        // 会话1: user_001 的对话历史
        String sessionId1 = "sess_user001_001";

        ChatHistory chat1 = new ChatHistory();
        chat1.setSessionId(sessionId1);
        chat1.setUserId("user_001");
        chat1.setRole("USER");
        chat1.setContent("你好，我想咨询一下年假的规定");
        chat1.setCreatedAt(now.minusHours(2));
        chatHistoryMapper.insert(chat1);

        ChatHistory chat2 = new ChatHistory();
        chat2.setSessionId(sessionId1);
        chat2.setUserId("user_001");
        chat2.setRole("ASSISTANT");
        chat2.setContent("您好！根据《休假管理规定》，入职满1年可享受5天年假，入职满3年7天，满5年10天，最多15天。请问您具体想了解哪方面？");
        chat2.setCreatedAt(now.minusHours(2).plusMinutes(1));
        chatHistoryMapper.insert(chat2);

        ChatHistory chat3 = new ChatHistory();
        chat3.setSessionId(sessionId1);
        chat3.setUserId("user_001");
        chat3.setRole("USER");
        chat3.setContent("我入职3年了，能休几天？");
        chat3.setCreatedAt(now.minusHours(1));
        chatHistoryMapper.insert(chat3);

        ChatHistory chat4 = new ChatHistory();
        chat4.setSessionId(sessionId1);
        chat4.setUserId("user_001");
        chat4.setRole("ASSISTANT");
        chat4.setContent("入职满3年可以休7天年假。需要我帮您申请吗？");
        chat4.setCreatedAt(now.minusHours(1).plusMinutes(1));
        chatHistoryMapper.insert(chat4);

        // 会话2: user_002 的对话历史
        String sessionId2 = "sess_user002_001";

        ChatHistory chat5 = new ChatHistory();
        chat5.setSessionId(sessionId2);
        chat5.setUserId("user_002");
        chat5.setRole("USER");
        chat5.setContent("现在有闲置的投影仪吗？");
        chat5.setCreatedAt(now.minusMinutes(30));
        chatHistoryMapper.insert(chat5);

        ChatHistory chat6 = new ChatHistory();
        chat6.setSessionId(sessionId2);
        chat6.setUserId("user_002");
        chat6.setRole("ASSISTANT");
        chat6.setContent("有的！目前有2台投影仪可用：索尼投影仪 A-01 和 明基投影仪 C-03。需要帮您申请借用吗？");
        chat6.setCreatedAt(now.minusMinutes(29));
        chatHistoryMapper.insert(chat6);

        // 查询统计
        LambdaQueryWrapper<ChatHistory> countWrapper = new LambdaQueryWrapper<>();
        long totalCount = chatHistoryMapper.selectCount(countWrapper);

        System.out.println("对话历史模拟数据生成完成！");
        System.out.println("会话数: 2 个");
        System.out.println("消息总数: " + totalCount + " 条");
    }
}
