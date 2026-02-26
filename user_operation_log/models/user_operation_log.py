# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
from datetime import datetime, timedelta
from odoo.tools import html2plaintext


# Default sensitive fields that should not be logged
SENSITIVE_FIELDS = {
    'password', 'password_crypt', 'password_hash', 'api_key', 'api_secret',
    'secret', 'token', 'access_token', 'refresh_token', 'private_key',
    'api_key_id', 'apikey', 'auth_token', 'session_id', 'csrf_token',
}


class UserOperationLog(models.Model):
    '''
    User Operation Log
    '''
    _name = 'user.operation.log'
    _description = 'User Operation Log'
    _order = 'operation_time desc'

    def _get_operation_types(self):
        return [
            ('login', _('Login')),
            ('create', _('Create')),
            ('read', _('Read')),
            ('write', _('Write')),
            ('unlink', _('Delete')),
            ('import', _('Import')),
            ('export', _('Export')),
            ('action', _('Action')),
        ]

    user_id = fields.Many2one('res.users', string='User', required=True, ondelete='restrict', index=True)
    user_name = fields.Char(related='user_id.name', string='User Name', store=False)
    operation_type = fields.Selection(_get_operation_types, string='Operation Type', required=True, index=True)
    model_name = fields.Char(string='Model Name', required=True, index=True)
    model_description = fields.Char(string='Model Description', compute='_compute_model_description')
    record_id = fields.Integer(string='Record ID', index=True)
    record_name = fields.Char(string='Record Name')
    operation_time = fields.Datetime(string='Operation Time', required=True, default=fields.Datetime.now, index=True)
    ip_address = fields.Char(string='IP Address', index=True)
    user_agent = fields.Char(string='User Agent')
    old_values = fields.Text(string='Old Values')
    new_values = fields.Text(string='New Values')
    operation_summary = fields.Text(string='Operation Summary')
    http_request_id = fields.Char(string='HTTP Request ID')
    http_session_id = fields.Char(string='HTTP Session ID')
    log_line_ids = fields.One2many('user.operation.log.line', 'log_id', string='Field Change Details')

    @api.depends('model_name')
    def _compute_model_description(self):
        '''Compute model description'''
        for record in self:
            description = False
            if record.model_name:
                try:
                    model = self.env['ir.model'].sudo().search([('model', '=', record.model_name)], limit=1)
                    description = model.name if model else record.model_name
                except Exception:
                    description = record.model_name
            record.model_description = description

    @api.model
    def log_operation(self, user_id, operation_type, model_name, record_id=None,
                      record_name=None, old_values=None, new_values=None,
                      operation_summary=None, ip_address=None, user_agent=None,
                      exclude_fields=None):
        '''
        Record operation log
        :param exclude_fields: Additional fields to exclude from logging
        '''
        # Filter out sensitive fields and clean HTML
        exclude_set = SENSITIVE_FIELDS.copy()
        if exclude_fields:
            exclude_set.update(exclude_fields)

        # Get field types to know which ones are HTML
        html_fields = []
        try:
            model_obj = self.env[model_name].sudo()
            html_fields = [f for f in model_obj._fields if model_obj._fields[f].type == 'html']
        except Exception:
            pass

        filtered_old = self._filter_and_clean_values(old_values, exclude_set, html_fields)
        filtered_new = self._filter_and_clean_values(new_values, exclude_set, html_fields)

        # Get model description in user lang
        model_desc = model_name
        try:
            model = self.env['ir.model'].sudo().with_context(lang=self.env.lang).search([('model', '=', model_name)], limit=1)
            model_desc = model.name if model else model_name
        except Exception:
            pass

        values = {
            'user_id': user_id,
            'operation_type': operation_type,
            'model_name': model_name,
            'model_description': model_desc, # Pre-compute to avoid issues
            'record_id': record_id,
            'record_name': record_name,
            'operation_time': fields.Datetime.now(),
            'ip_address': ip_address,
            'user_agent': user_agent,
            'operation_summary': operation_summary,
        }

        if filtered_old:
            values['old_values'] = json.dumps(filtered_old, ensure_ascii=False, default=str)
        if filtered_new:
            values['new_values'] = json.dumps(filtered_new, ensure_ascii=False, default=str)

        return self.create(values)

    @api.model
    def _filter_and_clean_values(self, values, exclude_set, html_fields):
        '''Filter out sensitive fields and clean HTML from values dict'''
        if not values or not isinstance(values, dict):
            return values

        result = {}
        for k, v in values.items():
            if k in exclude_set:
                continue
            
            clean_v = v
            if k in html_fields and isinstance(v, str):
                clean_v = html2plaintext(v)
            
            result[k] = clean_v
            
        return result

    @api.model
    def log_field_changes(self, log_record, old_values, new_values, exclude_fields=None):
        '''Record field change details'''
        if not old_values or not new_values:
            return

        # Filter sensitive fields
        exclude_set = SENSITIVE_FIELDS.copy()
        if exclude_fields:
            exclude_set.update(exclude_fields)

        line_model = self.env['user.operation.log.line'].sudo()
        
        # Ensure we have the field translations by using the correct context
        model_obj = self.env[log_record.model_name].sudo().with_context(lang=self.env.lang)
        
        for field_name, new_val in new_values.items():
            if field_name in exclude_set:
                continue

            old_val = old_values.get(field_name)
            
            # Smart comparison
            is_changed = False
            if old_val != new_val:
                is_changed = True
                if not old_val and not new_val:
                    is_changed = False
            
            if is_changed:
                # Get field description with translation
                field_desc = field_name
                field_type = 'char'
                try:
                    if field_name in model_obj._fields:
                        field_def = model_obj._fields[field_name]
                        field_desc = field_def.string or field_name
                        field_type = field_def.type
                except Exception:
                    pass

                # Strip HTML for log clarity
                clean_old = old_val
                clean_new = new_val
                
                if field_type == 'html':
                    if isinstance(old_val, str):
                        clean_old = html2plaintext(old_val)
                    if isinstance(new_val, str):
                        clean_new = html2plaintext(new_val)

                line_model.create({
                    'log_id': log_record.id,
                    'field_name': field_name,
                    'field_description': field_desc,
                    'old_value': str(clean_old) if clean_old is not None else '',
                    'new_value': str(clean_new) if clean_new is not None else '',
                })

    def cleanup_old_logs(self, days=180):
        '''
        Clean up logs older than specified days
        :param days: Number of days to keep logs (default 180)
        :return: Number of deleted records
        '''
        cutoff_date = fields.Datetime.now() - timedelta(days=days)
        old_logs = self.search([('operation_time', '<', cutoff_date)])
        count = len(old_logs)
        old_logs.unlink()
        return count

    @api.model
    def get_sensitive_fields(self):
        '''Get list of sensitive fields that should not be logged'''
        return list(SENSITIVE_FIELDS)