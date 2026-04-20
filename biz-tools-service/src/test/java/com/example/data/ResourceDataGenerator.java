package com.example.data;

import com.example.entity.Resource;
import com.example.service.ResourceService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.time.LocalDateTime;

/**
 * 资源模拟数据生成器
 */
@SpringBootTest
public class ResourceDataGenerator {

    @Autowired
    private ResourceService resourceService;

    /**
     * 生成资源表模拟数据
     */
    @Test
    public void generateResourceData() {
        // 清空现有数据
        for (Resource resource : resourceService.listAll()) {
            resourceService.removeById(resource.getId());
        }

        LocalDateTime now = LocalDateTime.now();

        // 投影仪数据
        Resource projector1 = new Resource();
        projector1.setName("索尼投影仪 A-01");
        projector1.setType("PROJECTOR");
        projector1.setStatus("AVAILABLE");
        projector1.setQuantity(5);
        projector1.setAvailableQuantity(3);
        projector1.setDescription("4K分辨率，支持无线投屏");
        projector1.setCreatedAt(now);
        projector1.setUpdatedAt(now);
        resourceService.save(projector1);

        Resource projector2 = new Resource();
        projector2.setName("爱普生投影仪 B-02");
        projector2.setType("PROJECTOR");
        projector2.setStatus("IN_USE");
        projector2.setQuantity(3);
        projector2.setAvailableQuantity(0);
        projector2.setDescription("便携商务投影仪");
        projector2.setCreatedAt(now);
        projector2.setUpdatedAt(now);
        resourceService.save(projector2);

        Resource projector3 = new Resource();
        projector3.setName("明基投影仪 C-03");
        projector3.setType("PROJECTOR");
        projector3.setStatus("AVAILABLE");
        projector3.setQuantity(2);
        projector3.setAvailableQuantity(2);
        projector3.setDescription("短焦投影仪，适合小会议室");
        projector3.setCreatedAt(now);
        projector3.setUpdatedAt(now);
        resourceService.save(projector3);

        // 笔记本电脑数据
        Resource laptop1 = new Resource();
        laptop1.setName("MacBook Pro 16寸");
        laptop1.setType("LAPTOP");
        laptop1.setStatus("AVAILABLE");
        laptop1.setQuantity(10);
        laptop1.setAvailableQuantity(6);
        laptop1.setDescription("M3芯片，32GB内存");
        laptop1.setCreatedAt(now);
        laptop1.setUpdatedAt(now);
        resourceService.save(laptop1);

        Resource laptop2 = new Resource();
        laptop2.setName("ThinkPad X1 Carbon");
        laptop2.setType("LAPTOP");
        laptop2.setStatus("IN_USE");
        laptop2.setQuantity(8);
        laptop2.setAvailableQuantity(2);
        laptop2.setDescription("i7处理器，16GB内存");
        laptop2.setCreatedAt(now);
        laptop2.setUpdatedAt(now);
        resourceService.save(laptop2);

        // 会议室数据
        Resource room1 = new Resource();
        room1.setName("301会议室");
        room1.setType("ROOM");
        room1.setStatus("AVAILABLE");
        room1.setQuantity(1);
        room1.setAvailableQuantity(1);
        room1.setDescription("可容纳10人，配备视频会议系统");
        room1.setCreatedAt(now);
        room1.setUpdatedAt(now);
        resourceService.save(room1);

        Resource room2 = new Resource();
        room2.setName("302会议室");
        room2.setType("ROOM");
        room2.setStatus("AVAILABLE");
        room2.setQuantity(1);
        room2.setAvailableQuantity(1);
        room2.setDescription("可容纳6人，小型讨论室");
        room2.setCreatedAt(now);
        room2.setUpdatedAt(now);
        resourceService.save(room2);

        // 软件许可数据
        Resource license1 = new Resource();
        license1.setName("Photoshop License");
        license1.setType("LICENSE");
        license1.setStatus("AVAILABLE");
        license1.setQuantity(20);
        license1.setAvailableQuantity(15);
        license1.setDescription("Adobe Photoshop年度订阅");
        license1.setCreatedAt(now);
        license1.setUpdatedAt(now);
        resourceService.save(license1);

        Resource license2 = new Resource();
        license2.setName("IntelliJ IDEA License");
        license2.setType("LICENSE");
        license2.setStatus("IN_USE");
        license2.setQuantity(15);
        license2.setAvailableQuantity(5);
        license2.setDescription("JetBrains IntelliJ IDEA Ultimate");
        license2.setCreatedAt(now);
        license2.setUpdatedAt(now);
        resourceService.save(license2);

        System.out.println("资源模拟数据生成完成！共生成 " + resourceService.listAll().size() + " 条资源数据");
    }
}
