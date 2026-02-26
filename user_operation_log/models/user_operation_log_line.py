# -*- coding: utf-8 -*-
from odoo import models, fields


class UserOperationLogLine(models.Model):
    '''
    User operation log line - field change details
    '''
    _name = 'user.operation.log.line'
    _description = 'User Operation Log Line'

    log_id = fields.Many2one(
        'user.operation.log',
        string='Operation Log',
        required=True,
        ondelete='cascade',
        index=True
    )
    field_name = fields.Char(string='Field Name', required=True)
    field_description = fields.Char(string='Field Description')
    old_value = fields.Text(string='Old Value')
    new_value = fields.Text(string='New Value')
