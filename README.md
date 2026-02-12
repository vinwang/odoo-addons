# Odoo Addons

A collection of custom Odoo modules for Odoo 19.0.

## Modules

| Module | Description |
| ------ | ----------- |
| vin_auditlog | Based on OCA/server-tools. Audit Log module for tracking model operations. Provides comprehensive logging of create, read, write, and delete operations on configured models. |
| vin_partner_relation | Based on OCA/partner-contact. Module for managing various types of relations between partners. Supports custom relation types, partner type constraints, reflexive and symmetric relations. |

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
