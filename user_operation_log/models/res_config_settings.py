# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    user_operation_log_global_enabled = fields.Boolean(
        string='Enable Global Logging',
        config_parameter='user_operation_log.global_logging_enabled',
        default=True,
        help='When enabled, all operations on all models will be logged by default. '
             'You can still use rules to exclude specific models/operations.'
    )
