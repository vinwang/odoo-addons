# User Operation Log - Global Logging Mode

> **[中文版](./README_zh_CN.md)** | English Version

## Overview

User login and operation logging module for audit tracking and security monitoring. This module supports **Global Default Monitoring** mode - no need to manually create rules for each model.

## Core Features

### Login Log Recording
- Record user login/logout time, IP address, session info, login status
- Login/logout time, IP address, browser info, login status

### Operation Log Recording
- Record create, modify, delete, import, export and other key operations
- Field-level change tracking: record field value changes before and after modification

### Operation Rule Configuration
- Configurable models and operation types to log
- Auto cleanup: scheduled task to clean old logs (default: 180 days)
- Security filter: auto-exclude sensitive fields (passwords, tokens, API keys, etc.)

## Working Modes

### 1. Global Monitoring Mode (Default Enabled)

**Path**: Settings → Technical → System Parameters → `user_operation_log.global_logging_enabled`

When enabled:
- ✅ Log all operations (Create, Write, Delete, Import, Export) on all non-system models by default
- ✅ No manual rule creation required
- ✅ Can exclude specific models/operations using blacklist rules

### 2. Rule Modes

#### Include Mode (Whitelist)
- **Purpose**: Log only specific models/operations
- **Scenario**: Disable global monitoring, only monitor critical business models
- **Example**: Only log `res.partner` create and write

#### Exclude Mode (Blacklist)  
- **Purpose**: Exclude specific models/operations
- **Scenario**: Enable global monitoring but exclude high-frequency low-value operations
- **Example**: Exclude all `mail.message` operations

## Usage Scenarios

### Scenario A: Comprehensive Audit (Recommended)
```
Global Monitoring: ✅ Enabled
Rule Config: Blacklist exclude high-frequency models
- Exclude: mail.message (all operations)
- Exclude: mail.tracking.value (all operations)
- Exclude: bus.bus (all operations)
```

### Scenario B: Precise Monitoring
```
Global Monitoring: ❌ Disabled
Rule Config: Whitelist specify core models
- Include: res.partner (all operations)
- Include: crm.lead (all operations)
- Include: sale.order (all operations)
- Include: account.move (all operations)
```

### Scenario C: Mixed Mode
```
Global Monitoring: ✅ Enabled
Rule Config: Mixed usage
- Exclude: mail.* (exclude mail related)
- Include: res.users (special attention, detailed logs)
```

## Configuration Steps

### 1. Set Global Switch

Go to: **Settings → General Settings → User Operation Log Settings**

Check/Uncheck **"Enable Global Logging"**

### 2. Create Rules (Optional)

Go to: **Operation Logs → Log Rules → Create**

Configure:
- **Rule Name**: Descriptive name
- **Model**: Select model to control
- **Operation Type**: Create/Write/Delete/Import/Export
- **Rule Mode**: 
  - `Include (Whitelist)`: Include this model/operation
  - `Exclude (Blacklist)`: Exclude this model/operation
- **Specific Users**: Empty=all users, specific=only these users
- **Excluded Fields**: Fields not to log

### 3. Activate Rule

After creating rule, click **"Activate"** button.

## System Models Auto-Excluded

The following system models are always excluded (hardcoded):
- `ir.*` - Internal system models
- `base.*` - Base system models
- `mail.message` - Mail messages
- `mail.tracking.value` - Mail tracking
- `user.operation.log*` - Log models themselves
- `user.login.log` - Login log

## Performance Recommendations

1. **Production**: Use blacklist mode, exclude high-frequency low-value operations
2. **Development**: Can enable all for easier debugging
3. **Regular Cleanup**: Enable auto cleanup task, retain 180 days logs

## Example Rule Configuration

### Exclude Mail System
```xml
<record id="rule_exclude_mail" model="user.operation.rule">
    <field name="name">Exclude Mail Messages</field>
    <field name="model_id" ref="mail.model_mail_message"/>
    <field name="operation_type">write</field>
    <field name="rule_mode">exclude</field>
    <field name="state">active</field>
</record>
```

### Monitor User Changes (Detailed)
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

## Installation

### Prerequisites
- Odoo 19.0+
- base module
- web module
- http_routing module

### Installation Steps
1. Search for "User Operation Log" in Odoo Apps
2. Click Install
3. Wait for installation to complete

## Usage

### View Login Logs
1. Navigate to **Settings → User Operation Log → Login Logs**
2. View all user login records:
   - Login/logout time
   - IP address and browser info
   - Login status

### View Operation Logs
1. Navigate to **Settings → User Operation Log → Operation Logs**
2. View all operation records:
   - Operation time and type
   - User and IP address
   - Model and record
   - Field change details

### View Logs from User Detail
1. Navigate to **Settings → Users & Companies → Users**
2. Open user record
3. Click "Operation Logs" or "Login Logs" smart button

## Technical Details

### Dependencies
- `base` - Odoo Base Module
- `web` - Web Module
- `http_routing` - HTTP Routing Module

### Data Models
- `user.login.log` - Login Log Model
- `user.operation.log` - Operation Log Model
- `user.operation.log.line` - Field Change Detail Model
- `user.operation.rule` - Operation Rule Model

### Implementation
- **Login Log**: Override `res.users._login()` method and `/web/session/logout` route
- **Operation Log**: Override `models.Base` `create()`, `write()`, `unlink()` methods
- **Field Tracking**: Record field changes via `log_line_ids`

### Sensitive Fields Auto-Excluded
The following fields are automatically excluded from logs:
- password
- password_crypt
- password_token
- api_key
- token
- secret
- vault

## FAQ

**Q: Does global monitoring affect performance?**  
A: There is some impact, but it's optimized with async writes and batch processing. Use blacklist to exclude high-frequency operations.

**Q: How to see which models are currently monitored?**  
A: Go to "Operation Logs → Log Details", group by model to see actual recorded items.

**Q: How to handle rule conflicts?**  
A: Priority: Exclude > Include > Global. Blacklist rules have highest priority.

**Q: Can I monitor specific users?**  
A: Yes. Specify "Specific Users" in the rule.

## Technical Implementation

Core logic in `models/user_operation_rule.py`:

```python
def should_log_operation(self, user_id, model_name, operation_type):
    # 1. Check global config
    global_enabled = self._get_global_logging_enabled()
    
    # 2. Check blacklist rules (priority)
    if has_exclude_rule:
        return False
    
    # 3. Check whitelist rules
    if has_include_rule:
        return True
    
    # 4. Use global setting
    return global_enabled
```

## Version History

### v19.0.1.0.0 (2026-02-14)
- ✨ Initial release
- ✨ Login log recording
- ✨ Operation log recording
- ✨ Operation rule configuration
- ✨ Field-level change tracking
- ✨ Auto cleanup scheduled task
- ✨ Pre-configured common model rules
- ✨ New: Global monitoring mode
- ✨ New: Rule whitelist/blacklist support
- ✨ New: System parameter configuration interface
- 🐛 Fix import/export log missing issue
- 📝 Complete Chinese translations

## Author
Vin

## License
LGPL-3
