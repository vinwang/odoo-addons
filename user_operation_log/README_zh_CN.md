# 用户操作日志模块 - 全局监控模式

> **[English Version](./README_en.md)** | 中文版

## 功能概述

用户登录和操作日志记录模块，用于审计追踪和安全监控。该模块现在支持**全局默认监控**模式，无需为每个模型手动创建规则即可记录所有操作。

## 核心功能

### 登录日志记录
- 记录用户登录/登出时间、IP地址、会话信息、登录状态
- 登录/登出时间、IP地址、浏览器信息、登录状态

### 操作日志记录
- 记录创建、修改、删除、导入、导出等关键操作
- 字段级变更追踪：记录修改前后的字段值变化

### 操作规则配置
- 可配置需要记录的模型和操作类型
- 自动清理：定时任务清理历史日志（默认保留180天）
- 安全过滤：自动排除敏感字段（密码、令牌、API密钥等）

## 工作模式

### 1. 全局监控模式（默认启用）

**路径**: 设置 → 技术 → 系统参数 → `user_operation_log.global_logging_enabled`

当启用全局监控时：
- ✅ 默认记录所有非系统模型的所有操作（Create, Write, Delete, Import, Export）
- ✅ 无需手动创建规则
- ✅ 可通过黑名单规则排除不需要监控的模型/操作

### 2. 规则系统

#### 白名单模式（Include）
- **用途**: 仅记录特定模型/操作
- **场景**: 关闭全局监控，只监控关键业务模型
- **示例**: 只监控 `res.partner` 的创建和修改

#### 黑名单模式（Exclude）  
- **用途**: 排除特定模型/操作
- **场景**: 开启全局监控，但排除某些高频低价值操作
- **示例**: 排除 `mail.message` 的所有操作

## 使用场景

### 场景A: 全面审计（推荐）
```
全局监控: ✅ 启用
规则配置: 黑名单排除高频模型
- Exclude: mail.message (所有操作)
- Exclude: mail.tracking.value (所有操作)
- Exclude: bus.bus (所有操作)
```

### 场景B: 精准监控
```
全局监控: ❌ 禁用
规则配置: 白名单指定核心模型
- Include: res.partner (所有操作)
- Include: crm.lead (所有操作)
- Include: sale.order (所有操作)
- Include: account.move (所有操作)
```

### 场景C: 混合模式
```
全局监控: ✅ 启用
规则配置: 混合使用
- Exclude: mail.* (排除邮件相关)
- Include: res.users (特别关注用户，详细日志)
```

## 配置步骤

### 1. 设置全局开关

进入: **设置 → 通用设置 → User Operation Log Settings**

勾选/取消勾选 **"Enable Global Logging"**

### 2. 创建规则（可选）

进入: **操作日志 → 日志规则 → 创建**

配置项:
- **规则名称**: 描述性名称
- **模型**: 选择要控制的模型
- **操作类型**: Create/Write/Delete/Import/Export
- **规则模式**: 
  - `Include (Whitelist)`: 包含此模型/操作
  - `Exclude (Blacklist)`: 排除此模型/操作
- **特定用户**: 留空=所有用户，指定=仅这些用户
- **排除字段**: 不记录的敏感字段

### 3. 激活规则

创建规则后，点击 **"Activate"** 按钮使其生效。

## 系统模型自动排除

以下系统模型始终不会被记录（硬编码）：
- `ir.*` - 系统内部模型
- `base.*` - 基础系统模型  
- `mail.message` - 邮件消息
- `mail.tracking.value` - 邮件跟踪
- `user.operation.log*` - 日志模型自身
- `user.login.log` - 登录日志

## 性能建议

1. **生产环境**: 建议使用黑名单模式，排除高频低价值操作
2. **开发环境**: 可以全开，便于调试
3. **定期清理**: 启用自动清理任务，保留180天日志

## 示例规则配置

### 排除邮件系统
```xml
<record id="rule_exclude_mail" model="user.operation.rule">
    <field name="name">Exclude Mail Messages</field>
    <field name="model_id" ref="mail.model_mail_message"/>
    <field name="operation_type">write</field>
    <field name="rule_mode">exclude</field>
    <field name="state">active</field>
</record>
```

### 监控用户变更（详细）
```xml
<record id="rule_include_users" model="user.operation.rule">
    <field name="name">Monitor User Changes</field>
    <field name="model_id" ref="base.model_res_users"/>
    <field name="operation_type">write</field>
    <field name="rule_mode">include</field>
    <field name="log_level">detailed</field>
    <field name="state">active</field>
</record>
```

## 安装说明

### 前置要求
- Odoo 19.0+
- base 模块
- web 模块
- http_routing 模块

### 安装步骤
1. 在 Odoo 应用列表中搜索 "User Operation Log"
2. 点击安装
3. 等待安装完成

## 使用说明

### 查看登录日志
1. 导航到 **设置 → 用户操作日志 → 登录日志**
2. 查看所有用户登录记录：
   - 登录/登出时间
   - IP地址和浏览器信息
   - 登录状态

### 查看操作日志
1. 导航到 **设置 → 用户操作日志 → 操作日志**
2. 查看所有操作记录：
   - 操作时间和类型
   - 用户和IP地址
   - 模型和记录
   - 字段变更明细

### 从用户详情查看日志
1. 导航到 **设置 → 用户和公司 → 用户**
2. 打开用户记录
3. 点击 "Operation Logs" 或 "Login Logs" 智能按钮

## 技术细节

### 依赖模块
- `base` - Odoo 基础模块
- `web` - Web 模块
- `http_routing` - HTTP 路由模块

### 数据模型
- `user.login.log` - 登录日志模型
- `user.operation.log` - 操作日志模型
- `user.operation.log.line` - 字段变更明细模型
- `user.operation.rule` - 操作规则模型

### 实现方式
- **登录日志**: 重写 `res.users._login()` 方法和 `/web/session/logout` 路由
- **操作日志**: 重写 `models.Base` 的 `create()`、`write()`、`unlink()` 方法
- **字段追踪**: 通过 `log_line_ids` 记录字段变更前后值

### 敏感字段自动排除
以下字段自动从日志中排除：
- password
- password_crypt
- password_token
- api_key
- token
- secret
- vault

## 常见问题

**Q: 全局监控会影响性能吗?**  
A: 有一定影响，但通过异步写入和批量处理已优化。建议使用黑名单排除高频操作。

**Q: 如何查看当前监控了哪些模型?**  
A: 进入"操作日志 → 日志详情"，按模型分组查看实际记录情况。

**Q: 规则冲突如何处理?**  
A: 优先级: Exclude > Include > Global。黑名单规则优先级最高。

**Q: 可以监控特定用户吗?**  
A: 可以。在规则中指定"特定用户"字段即可。

## 技术实现

核心逻辑位于 `models/user_operation_rule.py`:

```python
def should_log_operation(self, user_id, model_name, operation_type):
    # 1. 检查全局配置
    global_enabled = self._get_global_logging_enabled()
    
    # 2. 检查黑名单规则（优先）
    if has_exclude_rule:
        return False
    
    # 3. 检查白名单规则
    if has_include_rule:
        return True
    
    # 4. 使用全局设置
    return global_enabled
```

## 版本历史

### v19.0.1.0.0 (2026-02-14)
- ✨ 初始版本
- ✨ 登录日志记录
- ✨ 操作日志记录
- ✨ 操作规则配置
- ✨ 字段级变更追踪
- ✨ 自动清理计划任务
- ✨ 预置常用模型规则
- ✨ 新增全局监控模式
- ✨ 新增规则白名单/黑名单支持
- ✨ 新增系统参数配置界面
- 🐛 修复导入导出日志缺失问题
- 📝 完善中文翻译

## 作者
Vin

## 许可证
LGPL-3