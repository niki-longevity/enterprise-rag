package com.example.controller.internal;

import com.example.entity.Resource;
import com.example.service.ResourceService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 内部资源接口Controller
 * 供Agent服务调用的资源查询API
 */
@RestController
@RequestMapping("/api/internal/resources")
public class InternalResourceController {

    @Autowired
    private ResourceService resourceService;

    /**
     * 查询资源列表
     *
     * @param type   资源类型（可选）
     * @param status 资源状态（可选）
     * @return 资源列表
     */
    @GetMapping
    public List<Resource> listResources(
            @RequestParam(required = false) String type,
            @RequestParam(required = false) String status) {
        if (type != null && status != null) {
            return resourceService.listByTypeAndStatus(type, status);
        } else if (type != null) {
            return resourceService.listByType(type);
        } else if (status != null) {
            return resourceService.listByStatus(status);
        }
        return resourceService.listAll();
    }

    /**
     * 根据ID查询资源详情
     *
     * @param id 资源ID
     * @return 资源详情
     */
    @GetMapping("/{id}")
    public Resource getById(@PathVariable Long id) {
        return resourceService.getById(id);
    }
}
