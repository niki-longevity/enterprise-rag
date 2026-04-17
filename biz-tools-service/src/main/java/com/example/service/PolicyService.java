package com.example.service;

import com.example.entity.Policy;
import java.util.List;

/**
 * 政策文档服务接口
 * 提供政策文档的搜索、管理等功能
 */
public interface PolicyService {

    /**
     * 根据ID查询政策文档
     */
    Policy getById(Long id);

    /**
     * 查询所有政策文档
     */
    List<Policy> listAll();

    /**
     * 根据分类查询政策文档
     */
    List<Policy> listByCategory(String category);

    /**
     * 关键词搜索政策文档
     */
    List<Policy> searchByKeyword(String keyword);

    /**
     * 新增政策文档
     */
    boolean save(Policy policy);

    /**
     * 更新政策文档
     */
    boolean updateById(Policy policy);

    /**
     * 删除政策文档
     */
    boolean removeById(Long id);
}
