# -*- coding: utf-8 -*-
from odoo import models, api, fields
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    '''
    Extend res.users to add login logging
    '''
    _inherit = 'res.users'

    def _login(self, credential, user_agent_env):
        '''Override _login to record login attempts'''
        # Store request info before authentication
        ip = request.httprequest.environ.get('REMOTE_ADDR', 'n/a') if request else 'n/a'
        
        # Get session_id safely (compatible with dict and object)
        def get_session_id(req):
            if not req or not hasattr(req, 'session'):
                return False
            session = req.session
            sid = None
            if isinstance(session, dict):
                sid = session.get('sid')
            else:
                sid = getattr(session, 'sid', None)
            # Ensure we return a string or False, not dict
            if sid is None:
                return False
            if isinstance(sid, dict):
                return False
            return str(sid)
        
        # Get user_agent safely (ensure it's a string)
        def get_user_agent(req):
            if not req or not hasattr(req, 'httprequest'):
                return ''
            ua = req.httprequest.environ.get('HTTP_USER_AGENT', '')
            if isinstance(ua, dict):
                return ''
            return str(ua) if ua else ''
        
        # Get ip safely (ensure it's a string)
        def get_ip(req):
            if not req or not hasattr(req, 'httprequest'):
                return ''
            ip_val = req.httprequest.environ.get('REMOTE_ADDR', '')
            if isinstance(ip_val, dict):
                return ''
            return str(ip_val) if ip_val else ''
        
        try:
            # Call original _login method
            auth_info = super()._login(credential, user_agent_env)
            
            # Login successful - record login log
            if auth_info and 'uid' in auth_info:
                uid = auth_info['uid']
                try:
                    self.env['user.login.log'].sudo().create({
                        'user_id': uid,
                        'login_time': fields.Datetime.now(),
                        'status': 'success',
                        'ip_address': get_ip(request),
                        'user_agent': get_user_agent(request),
                        'session_id': get_session_id(request),
                    })
                except Exception as e:
                    _logger.warning("Failed to record login log: %s", e)
            
            return auth_info

            
        except Exception as e:
            # Login failed - record failed login attempt
            try:
                login = credential.get('login')
                if login:
                    # Find user by login
                    user = self.sudo().search([('login', '=', login)], limit=1)
                    if user and user.id:
                        self.env['user.login.log'].sudo().create({
                            'user_id': user.id,
                            'login_time': fields.Datetime.now(),
                            'status': 'failed',
                            'failure_reason': 'Invalid credentials',
                            'ip_address': get_ip(request),
                            'user_agent': get_user_agent(request),
                            'session_id': get_session_id(request),
                        })
            except Exception:
                pass
            raise