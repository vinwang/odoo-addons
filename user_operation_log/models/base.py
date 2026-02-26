# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.http import request


class Base(models.AbstractModel):
    '''
    Add base functionality to all models
    '''
    _inherit = 'base'

    @api.model_create_multi
    def create(self, vals_list):
        '''Override create to log operation'''
        records = super(Base, self).create(vals_list)
        
        # Check rules and log
        rule_model = self.env['user.operation.rule'].sudo()
        if rule_model.should_log_operation(self.env.uid, self._name, 'create'):
            log_model = self.env['user.operation.log'].sudo()
            http_info = self._get_http_request_info()
            
            # Use request context to avoid duplicate logging in the same request
            request_log_id = 'user_op_log_%s_%s_create' % (self._name, self.env.uid)
            logged_ids = getattr(request, request_log_id, set()) if request else set()

            log_level = rule_model.get_log_level(self._name, 'create')

            for record in records:
                if record.id in logged_ids:
                    continue
                    
                try:
                    # Use sudo() to get record details for logging safely
                    sudo_record = record.sudo()
                    log_model.log_operation(
                        user_id=self.env.uid,
                        operation_type='create',
                        model_name=self._name,
                        record_id=record.id,
                        record_name=sudo_record.display_name,
                        new_values=vals_list[0] if len(vals_list) == 1 and log_level == 'detailed' else None,
                        ip_address=http_info.get('ip_address'),
                        user_agent=http_info.get('user_agent'),
                        exclude_fields=rule_model.get_fields_to_exclude(self._name)
                    )
                    logged_ids.add(record.id)
                except Exception:
                    pass
            
            if request:
                setattr(request, request_log_id, logged_ids)
                
        return records

    def write(self, vals):
        '''Override write to log operation'''
        # Skip logging if we are updating the log model itself or internal odoo fields
        if self._name in ['user.operation.log', 'user.operation.log.line', 'user.login.log', 'mail.message', 'mail.tracking.value']:
            return super(Base, self).write(vals)

        rule_model = self.env['user.operation.rule'].sudo()
        should_log = rule_model.should_log_operation(self.env.uid, self._name, 'write')
        
        # Check for duplication within request
        request_log_id = 'user_op_log_%s_%s_write' % (self._name, self.env.uid)
        logged_ids = getattr(request, request_log_id, set()) if request else set()
        
        # Filter records that haven't been logged in this request yet
        records_to_log = self.filtered(lambda r: r.id not in logged_ids) if should_log else self.env[self._name]
        
        old_values_dict = {}
        if records_to_log:
            # Pre-fetch old values for detailed logging using sudo to avoid AccessError
            fields_to_read = [f for f in vals.keys() if f in self._fields]
            if fields_to_read:
                # Use sudo() to ensure we can read the old values regardless of user permissions
                # We only do this if should_log is True, and the results are only for logging.
                for record in records_to_log.sudo():
                    try:
                        old_data = record.read(fields_to_read, load=False)[0]
                        # Clean up many2one values to be IDs only
                        for f in fields_to_read:
                            if self._fields[f].type == 'many2one' and isinstance(old_data.get(f), tuple):
                                old_data[f] = old_data[f][0]
                        old_values_dict[record.id] = old_data
                    except Exception:
                        pass

        res = super(Base, self).write(vals)

        if records_to_log:
            log_model = self.env['user.operation.log'].sudo()
            http_info = self._get_http_request_info()
            log_level = rule_model.get_log_level(self._name, 'write')
            
            for record in records_to_log:
                try:
                    log_record = log_model.log_operation(
                        user_id=self.env.uid,
                        operation_type='write',
                        model_name=self._name,
                        record_id=record.id,
                        record_name=record.display_name,
                        old_values=old_values_dict.get(record.id) if log_level == 'detailed' else None,
                        new_values=vals,
                        ip_address=http_info.get('ip_address'),
                        user_agent=http_info.get('user_agent'),
                        exclude_fields=rule_model.get_fields_to_exclude(self._name)
                    )
                    if log_record and old_values_dict.get(record.id) and log_level == 'detailed':
                        log_model.log_field_changes(
                            log_record, 
                            old_values_dict.get(record.id), 
                            vals,
                            exclude_fields=rule_model.get_fields_to_exclude(self._name)
                        )
                    logged_ids.add(record.id)
                except Exception:
                    pass
            
            if request:
                setattr(request, request_log_id, logged_ids)
                
        return res

    def unlink(self):
        '''Override unlink to log operation'''
        # Skip logging if we are deleting the log model itself or internal odoo fields
        if self._name in ['user.operation.log', 'user.operation.log.line', 'user.login.log', 'mail.message', 'mail.tracking.value']:
            return super(Base, self).unlink()

        rule_model = self.env['user.operation.rule'].sudo()
        should_log = rule_model.should_log_operation(self.env.uid, self._name, 'unlink')
        
        # Check for duplication within request
        request_log_id = 'user_op_log_%s_%s_unlink' % (self._name, self.env.uid)
        logged_ids = getattr(request, request_log_id, set()) if request else set()
        
        records_to_log = self.filtered(lambda r: r.id not in logged_ids) if should_log else self.env[self._name]
        
        records_info = []
        if records_to_log:
            # Use sudo() to fetch display names safely before deletion
            for record in records_to_log.sudo():
                try:
                    records_info.append({
                        'id': record.id,
                        'name': record.display_name,
                    })
                except Exception:
                    records_info.append({'id': record.id, 'name': _('Deleted Record')})

        res = super(Base, self).unlink()

        if records_to_log:
            log_model = self.env['user.operation.log'].sudo()
            http_info = self._get_http_request_info()
            
            for info in records_info:
                try:
                    log_model.log_operation(
                        user_id=self.env.uid,
                        operation_type='unlink',
                        model_name=self._name,
                        record_id=info['id'],
                        record_name=info['name'],
                        ip_address=http_info.get('ip_address'),
                        user_agent=http_info.get('user_agent'),
                        operation_summary=_('Record deleted')
                    )
                    logged_ids.add(info['id'])
                except Exception:
                    pass
            
            if request:
                setattr(request, request_log_id, logged_ids)
                
        return res

    @api.model
    def load(self, fields, data):
        '''Override load to log import operation'''
        res = super(Base, self).load(fields, data)
        
        # Skip logging for log models
        if self._name in ['user.operation.log', 'user.operation.log.line', 'user.login.log', 'mail.message', 'mail.tracking.value']:
            return res

        rule_model = self.env['user.operation.rule'].sudo()
        if rule_model.should_log_operation(self.env.uid, self._name, 'import'):
            log_model = self.env['user.operation.log'].sudo()
            http_info = self._get_http_request_info()
            
            import_ids = res.get('ids') if isinstance(res, dict) else []
            count = len(import_ids) if import_ids else len(data)
            
            log_model.log_operation(
                user_id=self.env.uid,
                operation_type='import',
                model_name=self._name,
                operation_summary=_('Imported %d records') % count,
                ip_address=http_info.get('ip_address'),
                user_agent=http_info.get('user_agent'),
            )
        return res

    def export_data(self, fields_to_export):
        '''Override export_data to log export operation'''
        res = super(Base, self).export_data(fields_to_export)
        
        # Skip logging for log models
        if self._name in ['user.operation.log', 'user.operation.log.line', 'user.login.log', 'mail.message', 'mail.tracking.value']:
            return res

        rule_model = self.env['user.operation.rule'].sudo()
        if rule_model.should_log_operation(self.env.uid, self._name, 'export'):
            log_model = self.env['user.operation.log'].sudo()
            http_info = self._get_http_request_info()
            
            log_model.log_operation(
                user_id=self.env.uid,
                operation_type='export',
                model_name=self._name,
                operation_summary=_('Exported %d records') % len(self),
                ip_address=http_info.get('ip_address'),
                user_agent=http_info.get('user_agent'),
            )
        return res

    def _get_http_request_info(self):
        '''Get HTTP request information'''
        if request:
            return {
                'ip_address': self._get_real_ip(),
                'user_agent': request.httprequest.environ.get('HTTP_USER_AGENT', ''),
                'session_id': request.session.sid if hasattr(request, 'session') else None,
            }
        return {
            'ip_address': '',
            'user_agent': '',
            'session_id': None,
        }

    def _get_real_ip(self):
        '''
        Get client real IP address
        '''
        if not request:
            return ''

        # Check IP headers by priority
        forwarded_for = request.httprequest.environ.get('HTTP_X_FORWARDED_FOR')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()

        real_ip = request.httprequest.environ.get('HTTP_X_REAL_IP')
        if real_ip:
            return real_ip.strip()

        remote_addr = request.httprequest.environ.get('REMOTE_ADDR')
        if remote_addr:
            return remote_addr

        return ''