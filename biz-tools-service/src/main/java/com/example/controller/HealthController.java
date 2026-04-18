package com.example.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

/**
 * 健康检查Controller
 * 提供服务健康检查接口
 */
@RestController
@RequestMapping("/health")
public class HealthController {

    /**
     * 健康检查接口
     *
     * @return 服务状态
     */
    @GetMapping
    public Map<String, Object> healthCheck() {
        Map<String, Object> result = new HashMap<>();
        result.put("status", "ok");
        result.put("service", "biz-tools-service");
        return result;
    }
}
