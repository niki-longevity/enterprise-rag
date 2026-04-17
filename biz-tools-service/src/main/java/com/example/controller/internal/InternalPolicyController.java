package com.example.controller.internal;

import com.example.entity.Policy;
import com.example.service.PolicyService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 内部政策接口Controller
 * 供Agent服务调用的政策文档搜索API
 */
@RestController
@RequestMapping("/api/internal/policies")
public class InternalPolicyController {

    @Autowired
    private PolicyService policyService;

    /**
     * 搜索政策文档
     *
     * @param keyword 搜索关键词
     * @return 匹配的政策文档列表
     */
    @GetMapping("/search")
    public List<Policy> searchPolicies(@RequestParam String keyword) {
        return policyService.searchByKeyword(keyword);
    }

    /**
     * 根据分类查询政策文档
     *
     * @param category 分类：IT, HR, ADMIN
     * @return 政策文档列表
     */
    @GetMapping
    public List<Policy> listByCategory(@RequestParam(required = false) String category) {
        if (category != null) {
            return policyService.listByCategory(category);
        }
        return policyService.listAll();
    }

    /**
     * 根据ID查询政策文档详情
     *
     * @param id 政策文档ID
     * @return 政策文档详情
     */
    @GetMapping("/{id}")
    public Policy getById(@PathVariable Long id) {
        return policyService.getById(id);
    }
}
