# Copyright 2015 ABF OSIELL <https://osiell.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Vin Audit Log',
    'version': '19.0.1.0.0',
    'author': 'Vin',
    'license': 'AGPL-3',
    'website': 'https://github.com/vinwang/odoo-addons',
    'category': 'Tools',
    'depends': [
        'base',
        'crm',
        'sale',
        'account',
        'stock',
        'hr',
        'hr_holidays',
        'hr_timesheet',
        'product',
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'data/vin_vin_vin_auditlog_rules.xml',
        'views/vin_vin_vin_auditlog_view.xml',
        'views/http_session_view.xml',
        'views/http_request_view.xml',
    ],
    'application': True,
    'installable': True,
}