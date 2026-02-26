# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    operation_log_count = fields.Integer(
        string='Operation Log Count',
        compute='_compute_operation_log_count',
        help='Number of operation logs for this user'
    )

    login_log_count = fields.Integer(
        string='Login Log Count',
        compute='_compute_login_log_count',
        help='Number of login logs for this user'
    )

    def _compute_operation_log_count(self):
        for user in self:
            count = self.env['user.operation.log'].search_count([('user_id', '=', user.id)])
            user.operation_log_count = count

    def _compute_login_log_count(self):
        for user in self:
            count = self.env['user.login.log'].search_count([('user_id', '=', user.id)])
            user.login_log_count = count

    def action_view_user_operation_logs(self):
        self.ensure_one()
        list_view = self.env.ref('user_operation_log.user_operation_log_list_view', False)
        form_view = self.env.ref('user_operation_log.user_operation_log_form_view', False)
        views = []
        if list_view:
            views.append((list_view.id, 'list'))
        if form_view:
            views.append((form_view.id, 'form'))
        if not views:
            views = [(False, 'list'), (False, 'form')]
        return {
            'type': 'ir.actions.act_window',
            'name': 'User Operation Logs',
            'res_model': 'user.operation.log',
            'view_mode': 'list,form',
            'views': views,
            'domain': [('user_id', '=', self.id)],
            'context': {'create': False},
        }

    def action_view_user_login_logs(self):
        self.ensure_one()
        list_view = self.env.ref('user_operation_log.user_login_log_list_view', False)
        form_view = self.env.ref('user_operation_log.user_login_log_form_view', False)
        views = []
        if list_view:
            views.append((list_view.id, 'list'))
        if form_view:
            views.append((form_view.id, 'form'))
        if not views:
            views = [(False, 'list'), (False, 'form')]
        return {
            'type': 'ir.actions.act_window',
            'name': 'User Login Logs',
            'res_model': 'user.login.log',
            'view_mode': 'list,form',
            'views': views,
            'domain': [('user_id', '=', self.id)],
            'context': {'create': False},
        }