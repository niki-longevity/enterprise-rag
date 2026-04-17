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
 */
@Service
public class ResourceServiceImpl implements ResourceService {

    @Autowired
    private ResourceMapper resourceMapper;

    @Override
    public Resource getById(Long id) {
        return resourceMapper.selectById(id);
    }

    @Override
    public List<Resource> listAll() {
        return resourceMapper.selectList(null);
    }

    @Override
    public List<Resource> listByType(String type) {
        LambdaQueryWrapper<Resource> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Resource::getType, type);
        return resourceMapper.selectList(wrapper);
    }

    @Override
    public List<Resource> listByStatus(String status) {
        LambdaQueryWrapper<Resource> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Resource::getStatus, status);
        return resourceMapper.selectList(wrapper);
    }

    @Override
    public List<Resource> listByTypeAndStatus(String type, String status) {
        LambdaQueryWrapper<Resource> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Resource::getType, type)
               .eq(Resource::getStatus, status);
        return resourceMapper.selectList(wrapper);
    }

    @Override
    public boolean save(Resource resource) {
        return resourceMapper.insert(resource) > 0;
    }

    @Override
    public boolean updateById(Resource resource) {
        return resourceMapper.updateById(resource) > 0;
    }

    @Override
    public boolean removeById(Long id) {
        return resourceMapper.deleteById(id) > 0;
    }
}
