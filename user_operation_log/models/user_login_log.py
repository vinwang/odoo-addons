# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class UserLoginLog(models.Model):
    '''
    User Login Log
    '''
    _name = 'user.login.log'
    _description = 'User Login Log'
    _order = 'login_time desc'

    def _get_status_selection(self):
        return [
            ('success', _('Success')),
            ('failed', _('Failed')),
        ]

    user_id = fields.Many2one('res.users', string='User', required=True, ondelete='restrict', index=True)
    user_name = fields.Char(related='user_id.name', string='User Name', store=False)
    login_time = fields.Datetime(string='Login Time', required=True, default=fields.Datetime.now, index=True)
    logout_time = fields.Datetime(string='Logout Time', index=True)
    ip_address = fields.Char(string='IP Address', index=True)
    session_id = fields.Char(string='Session ID', index=True)
    status = fields.Selection(_get_status_selection, string='Status', required=True, default='success', index=True)
    failure_reason = fields.Char(string='Failure Reason')
    user_agent = fields.Char(string='User Agent')

    @api.model
    def log_user_login(self, user_id, status='success', failure_reason=None):
        '''Record user login log'''
        http_info = self._get_http_info()
        values = {
            'user_id': user_id,
            'login_time': fields.Datetime.now(),
            'status': status,
            'failure_reason': failure_reason,
            'ip_address': http_info.get('ip_address'),
            'user_agent': http_info.get('user_agent'),
            'session_id': http_info.get('session_id'),
        }
        return self.create(values)

    @api.model
    def log_user_logout(self, user_id):
        '''Record user logout log'''
        # Update the most recent login record with logout time
        login_record = self.search([
            ('user_id', '=', user_id),
            ('logout_time', '=', False)
        ], order='login_time desc', limit=1)

        if login_record:
            login_record.write({
                'logout_time': fields.Datetime.now()
            })
        else:
            _logger.warning("No active login record found for user_id: %s to update logout time", user_id)

    @api.model
    def _get_http_info(self):
        '''Get HTTP request info using base model method'''
        return self._get_http_request_info()