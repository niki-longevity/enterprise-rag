package com.example.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.example.entity.Resource;
import com.example.mapper.ResourceMapper;
import com.example.service.ResourceService;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import java.util.List;

/**
 * 资源服务实现类
 * 提供资源的增删改查功能，包括投影仪、笔记本电脑、会议室、软件许可等资源管理
 */
@Service
public class ResourceServiceImpl implements ResourceService {

    @Autowired
    private ResourceMapper resourceMapper;

    /**
     * 根据ID查询资源
     *
     * @param id 资源ID
     * @return 资源信息，不存在则返回null
     */
    @Override
    public Resource getById(Long id) {
        return resourceMapper.selectById(id);
    }

    /**
     * 查询所有资源
     *
     * @return 资源列表
     */
    @Override
    public List<Resource> listAll() {
        return resourceMapper.selectList(null);
    }

    /**
     * 根据类型查询资源
     *
     * @param type 资源类型（PROJECTOR, LAPTOP, ROOM, LICENSE）
     * @return 该类型的资源列表
     */
    @Override
    public List<Resource> listByType(String type) {
        LambdaQueryWrapper<Resource> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Resource::getType, type);
        return resourceMapper.selectList(wrapper);
    }

    /**
     * 根据状态查询资源
     *
     * @param status 资源状态（AVAILABLE, IN_USE, MAINTENANCE）
     * @return 该状态的资源列表
     */
    @Override
    public List<Resource> listByStatus(String status) {
        LambdaQueryWrapper<Resource> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Resource::getStatus, status);
        return resourceMapper.selectList(wrapper);
    }

    /**
     * 根据类型和状态查询资源
     *
     * @param type 资源类型
     * @param status 资源状态
     * @return 符合条件的资源列表
     */
    @Override
    public List<Resource> listByTypeAndStatus(String type, String status) {
        LambdaQueryWrapper<Resource> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Resource::getType, type)
               .eq(Resource::getStatus, status);
        return resourceMapper.selectList(wrapper);
    }

    /**
     * 新增资源
     *
     * @param resource 资源信息
     * @return 是否成功
     */
    @Override
    public boolean save(Resource resource) {
        return resourceMapper.insert(resource) > 0;
    }

    /**
     * 更新资源
     *
     * @param resource 资源信息（需包含ID）
     * @return 是否成功
     */
    @Override
    public boolean updateById(Resource resource) {
        return resourceMapper.updateById(resource) > 0;
    }

    /**
     * 删除资源
     *
     * @param id 资源ID
     * @return 是否成功
     */
    @Override
    public boolean removeById(Long id) {
        return resourceMapper.deleteById(id) > 0;
    }
}
