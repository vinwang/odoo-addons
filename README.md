# Odoo Addons

A collection of custom Odoo modules for Odoo 19.0.

## Modules

### auditlog

Audit Log module for tracking model operations. It provides comprehensive logging of create, read, write, and unlink operations on configured models.

**Features:**
- Track create, read, write, and delete operations
- Configure which models to audit
- HTTP request and session logging
- Auto-vacuum for old logs

### partner_multi_relation

Module for managing various types of relations between partners.

**Features:**
- Define custom relation types with bidirectional names
- Constrain relations by partner type (Person/Company)
- Support for reflexive and symmetric relations
- Search partners by their relations
- Smart button on partner form view

## Requirements

- Odoo 19.0
- Python 3.10+

## Installation

1. Clone this repository to your Odoo addons directory:
   ```bash
   git clone https://github.com/vinwang/odoo-addons.git
   ```

2. Update the addons path in your Odoo configuration file.

3. Restart Odoo and install the modules from the Apps menu.

## License

All modules are licensed under AGPL-3.

## Author

vinwang
