# -*- coding: utf-8 -*-
# Copyright 2026, Your Name
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

{
    'name': 'User Operation Log',
    'version': '19.0.1.0.0',
    'author': 'Vin',
    'category': 'Tools',
    'summary': 'User operation and login log recording',
    'description': '''
User Operation Log Module
=========================

This module provides comprehensive user activity tracking features:

* Login log recording
* Key operation recording (create, write, delete, import, export, etc.)
* Field-level change tracking
* Advanced search and filtering
* Seamless integration with existing system
    ''',
    'depends': [
        'base',
        'web',
        'http_routing',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'data/ir_cron.xml',
        'data/user_operation_rule_data.xml',
        'views/user_operation_log_views.xml',
        'views/user_login_log_views.xml',
        'views/user_operation_rule_views.xml',
        'views/res_users_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}