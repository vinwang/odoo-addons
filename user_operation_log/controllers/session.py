# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.session import Session as WebSession
import logging

_logger = logging.getLogger(__name__)

class Session(WebSession):
    '''
    Override logout route to add logout logging
    '''

    @http.route('/web/session/logout', type='http', auth='user', readonly=True)
    def logout(self, redirect='/odoo'):
        # Get user before logout
        uid = request.session.uid
        # Record logout log BEFORE clearing session
        if uid:
            try:
                request.env['user.login.log'].sudo().log_user_logout(uid)
                # Ensure changes are committed before redirect/session clear
                request.env.cr.commit()
            except Exception as e:
                _logger.warning("Failed to record logout log: %s", e)
        
        # Call original logout
        return super().logout(redirect=redirect)
