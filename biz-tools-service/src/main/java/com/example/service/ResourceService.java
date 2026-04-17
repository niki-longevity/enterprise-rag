package com.example.service;

import com.example.entity.Resource;
import java.util.List;

/**
 * 资源服务接口
 * 提供资源的查询、管理等功能
 */
public interface ResourceService {

    /**
     * 根据ID查询资源
     */
    Resource getById(Long id);

    /**
     * 查询所有资源
     */
    List<Resource> listAll();

    /**
     * 根据类型查询资源
     */
    List<Resource> listByType(String type);

    /**
     * 根据状态查询资源
     */
    List<Resource> listByStatus(String status);

    /**
     * 根据类型和状态查询资源
     */
    List<Resource> listByTypeAndStatus(String type, String status);

    /**
     * 新增资源
     */
    boolean save(Resource resource);

    /**
     * 更新资源
     */
    boolean updateById(Resource resource);

    /**
     * 删除资源
     */
    boolean removeById(Long id);
}
