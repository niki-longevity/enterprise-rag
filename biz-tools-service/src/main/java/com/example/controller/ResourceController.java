package com.example.controller;

import com.example.entity.Resource;
import com.example.service.ResourceService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 资源管理Controller
 * 提供资源查询和管理API
 */
@RestController
@RequestMapping("/api/resources")
public class ResourceController {

    @Autowired
    private ResourceService resourceService;

    /**
     * 查询所有资源
     */
    @GetMapping
    public List<Resource> listAll() {
        return resourceService.listAll();
    }

    /**
     * 根据ID查询资源
     */
    @GetMapping("/{id}")
    public Resource getById(@PathVariable Long id) {
        return resourceService.getById(id);
    }

    /**
     * 根据类型查询资源
     */
    @GetMapping("/type/{type}")
    public List<Resource> listByType(@PathVariable String type) {
        return resourceService.listByType(type);
    }

    /**
     * 根据状态查询资源
     */
    @GetMapping("/status/{status}")
    public List<Resource> listByStatus(@PathVariable String status) {
        return resourceService.listByStatus(status);
    }

    /**
     * 查询可用资源（状态为AVAILABLE）
     */
    @GetMapping("/available")
    public List<Resource> listAvailable() {
        return resourceService.listByStatus("AVAILABLE");
    }

    /**
     * 新增资源
     */
    @PostMapping
    public boolean save(@RequestBody Resource resource) {
        return resourceService.save(resource);
    }

    /**
     * 更新资源
     */
    @PutMapping("/{id}")
    public boolean updateById(@PathVariable Long id, @RequestBody Resource resource) {
        resource.setId(id);
        return resourceService.updateById(resource);
    }

    /**
     * 删除资源
     */
    @DeleteMapping("/{id}")
    public boolean removeById(@PathVariable Long id) {
        return resourceService.removeById(id);
    }
}
