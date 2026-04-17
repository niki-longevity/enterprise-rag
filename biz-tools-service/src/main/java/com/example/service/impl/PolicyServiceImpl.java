package com.example.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.example.entity.Policy;
import com.example.mapper.PolicyMapper;
import com.example.service.PolicyService;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;
import java.util.List;

/**
 * 政策文档服务实现类
 */
@Service
public class PolicyServiceImpl implements PolicyService {

    @Autowired
    private PolicyMapper policyMapper;

    @Override
    public Policy getById(Long id) {
        return policyMapper.selectById(id);
    }

    @Override
    public List<Policy> listAll() {
        return policyMapper.selectList(null);
    }

    @Override
    public List<Policy> listByCategory(String category) {
        LambdaQueryWrapper<Policy> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Policy::getCategory, category);
        return policyMapper.selectList(wrapper);
    }

    @Override
    public List<Policy> searchByKeyword(String keyword) {
        LambdaQueryWrapper<Policy> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(Policy::getTitle, keyword)
               .or()
               .like(Policy::getContent, keyword);
        return policyMapper.selectList(wrapper);
    }

    @Override
    public boolean save(Policy policy) {
        return policyMapper.insert(policy) > 0;
    }

    @Override
    public boolean updateById(Policy policy) {
        return policyMapper.updateById(policy) > 0;
    }

    @Override
    public boolean removeById(Long id) {
        return policyMapper.deleteById(id) > 0;
    }
}
