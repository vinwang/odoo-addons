# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
from collections import defaultdict


class UserOperationRule(models.Model):
    '''
    User Operation Rule
    Defines which models and operations need to be logged
    '''
    _name = 'user.operation.rule'
    _description = 'User Operation Rule'
    _order = 'model_name, operation_type'

    name = fields.Char(string='Rule Name', required=True)
    model_id = fields.Many2one(
        'ir.model',
        string='Model',
        help='Select the model to log',
        ondelete='cascade',
        required=True
    )
    model_name = fields.Char(related='model_id.model', string='Model Name', store=True)
    model_description = fields.Char(related='model_id.name', string='Model Description', store=False)

    def _get_operation_types(self):
        return [
            ('create', _('Create')),
            ('read', _('Read')),
            ('write', _('Write')),
            ('unlink', _('Delete')),
            ('import', _('Import')),
            ('export', _('Export')),
            ('action', _('Action')),
        ]

    def _get_log_levels(self):
        return [
            ('basic', _('Basic Log')),
            ('detailed', _('Detailed Log')),
        ]

    def _get_rule_modes(self):
        return [
            ('include', _('Include (Whitelist)')),
            ('exclude', _('Exclude (Blacklist)')),
        ]

    def _get_state_selection(self):
        return [
            ('draft', _('Draft')),
            ('active', _('Active')),
        ]

    operation_type = fields.Selection(
        _get_operation_types,
        string='Operation Type',
        required=True
    )

    user_ids = fields.Many2many(
        'res.users',
        'user_operation_rule_users_rel',
        'rule_id',
        'user_id',
        string='Specific Users',
        help='If users are specified, only log operations by these users; leave empty to log all users'
    )

    log_level = fields.Selection(_get_log_levels, string='Log Level', default='detailed', required=True)

    active = fields.Boolean(string='Active', default=True)

    rule_mode = fields.Selection(
        _get_rule_modes,
        string='Rule Mode',
        default='include',
        required=True,
        help='Include: Only log this model/operation when rule exists\n'
             'Exclude: Do NOT log this model/operation (blacklist)'
    )

    fields_to_exclude_ids = fields.Many2many(
        'ir.model.fields',
        relation='user_operation_rule_fields_excluded_rel',
        column1='rule_id',
        column2='field_id',
        domain=lambda self: [('model_id', '=', self.model_id.id)],
        string='Excluded Fields',
        help='Fields to exclude from logging'
    )

    state = fields.Selection(_get_state_selection, string='State', default='draft', required=True)

    def action_activate(self):
        '''Activate rule'''
        self.write({'state': 'active'})

    def action_deactivate(self):
        '''Deactivate rule'''
        self.write({'state': 'draft'})

    @api.model
    def should_log_operation(self, user_id, model_name, operation_type):
        '''Check if operation should be logged
        
        Logic:
        1. Skip log-related models to prevent recursion
        2. Check global config (if enabled, log everything by default)
        3. Check exclude rules (blacklist) - if matched, skip logging
        4. Check include rules (whitelist) - if matched, do logging
        5. If no rules exist and global mode disabled, don't log
        '''
        # Skip log-related models to prevent recursion
        LOG_MODELS = [
            'user.operation.log', 
            'user.operation.log.line', 
            'user.login.log',
            'user.operation.rule',
            'ir.config_parameter',
            'mail.message', 
            'mail.tracking.value',
            # Core system models that should never be logged to avoid recursion/performance issues
            'ir.ui.menu',
            'ir.ui.view',
            'ir.model.data',
            'ir.model',
            'ir.model.fields',
            'ir.model.access',
            'ir.module.module',
            'res.groups',
            'ir.actions.act_window',
            'ir.actions.server',
            'ir.actions.report',
            'bus.bus'
        ]
        
        if model_name in LOG_MODELS:
            return False
            
        # Skip system-internal users (Root/__system__, Public user)
        if self._is_system_user(user_id):
            return False
        
        # Prevent recursion during rule search using context
        if self.env.context.get('_checking_operation_log_rules'):
            return False
        
        # Get global configuration
        global_enabled = self._get_global_logging_enabled()
        
        # Search for active rules with recursion protection
        try:
            rules = self.with_context(_checking_operation_log_rules=True).search([
                ('model_name', '=', model_name),
                ('operation_type', '=', operation_type),
                ('state', '=', 'active'),
                ('active', '=', True)
            ])
        except Exception:
            # If rule search fails, use global setting
            return global_enabled
        
        # Check for exclude rules (blacklist)
        exclude_rules = rules.filtered(lambda r: r.rule_mode == 'exclude')
        for rule in exclude_rules:
            if not rule.user_ids or user_id in rule.user_ids.ids:
                # Explicitly excluded
                return False
        
        # Check for include rules (whitelist)
        include_rules = rules.filtered(lambda r: r.rule_mode == 'include')
        if include_rules:
            for rule in include_rules:
                if not rule.user_ids or user_id in rule.user_ids.ids:
                    # Explicitly included
                    return True
            # Has include rules but user not matched
            return False if not global_enabled else True
        
        # No rules found - use global setting
        return global_enabled
    
    @api.model
    def _is_system_user(self, user_id):
        '''Check if the user is a system-internal user (Odoo Root or Public User)'''
        if not user_id:
            return True
            
        # Use cache/context to avoid repeated DB lookups for system users
        system_user_ids = self.env.registry._system_user_ids if hasattr(self.env.registry, '_system_user_ids') else None
        
        if system_user_ids is None:
            # Resolve system users (usually IDs 1, 2 etc. but ref is safer)
            system_user_ids = []
            try:
                # Root / __system__
                root_user = self.env.ref('base.user_root', raise_if_not_found=False)
                if root_user:
                    system_user_ids.append(root_user.id)
                
                # Public User
                public_user = self.env.ref('base.public_user', raise_if_not_found=False)
                if public_user:
                    system_user_ids.append(public_user.id)
                
                # Odoo Bot (if exists)
                odoobot = self.env.ref('base.user_demo', raise_if_not_found=False) # Not usually system
                # Better: just check for login __system__ and website public user
                
                # Cache it in the registry to persist across searches
                self.env.registry._system_user_ids = system_user_ids
            except Exception:
                # Fallback to standard IDs if registry not ready
                return user_id in [1, 2]
                
        return user_id in system_user_ids

    @api.model
    def _get_global_logging_enabled(self):
        '''Get global logging configuration
        
        Returns True if global logging is enabled (log everything by default)
        Can be configured via system parameter
        '''
        try:
            # Use context to prevent recursion when reading config
            IrConfigParam = self.env['ir.config_parameter'].with_context(
                _checking_operation_log_rules=True
            ).sudo()
            return IrConfigParam.get_param('user_operation_log.global_logging_enabled', 'True') == 'True'
        except Exception:
            # If config read fails, default to True (enabled)
            return True

    @api.model
    def get_log_level(self, model_name, operation_type):
        '''Get log level for a specific model and operation
        
        If rules exist, use the one from rule.
        Otherwise, default to 'detailed' for global logging.
        '''
        rules = self.with_context(_checking_operation_log_rules=True).search([
            ('model_name', '=', model_name),
            ('operation_type', '=', operation_type),
            ('state', '=', 'active'),
            ('active', '=', True)
        ])
        
        if rules:
            # If multiple rules, use the highest level
            levels = rules.mapped('log_level')
            return 'detailed' if 'detailed' in levels else 'basic'
            
        return 'detailed'

    @api.model
    def get_fields_to_exclude(self, model_name):
        '''Get fields to exclude for a specific model'''
        # Prevent recursion
        if self.env.context.get('_checking_operation_log_rules'):
            return []
            
        rules = self.with_context(_checking_operation_log_rules=True).search([
            ('model_name', '=', model_name),
            ('state', '=', 'active'),
            ('active', '=', True)
        ])

        fields_to_exclude = set()
        for rule in rules:
            fields_to_exclude.update(rule.fields_to_exclude_ids.mapped('name'))

        return list(fields_to_exclude)