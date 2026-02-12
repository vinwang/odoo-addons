from odoo import fields, models


class AuditlogLogLineView(models.Model):
    _name = "vin_auditlog.log.line.view"
    _inherit = "vin_auditlog.log.line"
    _description = "Auditlog - Log details (fields updated)"
    _auto = False
    _log_access = True

    name = fields.Char()
    model_id = fields.Many2one("ir.model")
    model_name = fields.Char()
    model_model = fields.Char()
    res_id = fields.Integer()
    user_id = fields.Many2one("res.users")
    method = fields.Char()
    http_session_id = fields.Many2one(
        "vin_auditlog.http.session", string="Session", index=True
    )
    http_request_id = fields.Many2one(
        "vin_auditlog.http.request", string="HTTP Request", index=True
    )
    log_type = fields.Selection(
        selection=lambda r: r.env["vin_auditlog.rule"]._fields["log_type"].selection,
        string="Type",
    )

    def _select_query(self):
        return """
            alogl.id,
            alogl.create_date,
            alogl.create_uid,
            alogl.write_uid,
            alogl.write_date,
            alogl.field_id,
            alogl.log_id,
            alogl.old_value,
            alogl.new_value,
            alogl.old_value_text,
            alogl.new_value_text,
            alogl.field_name,
            alogl.field_description,
            alog.name,
            alog.model_id,
            alog.model_name,
            alog.model_model,
            alog.res_id,
            alog.user_id,
            alog.method,
            alog.http_session_id,
            alog.http_request_id,
            alog.log_type
        """

    def _from_query(self):
        return """
            vin_vin_auditlog_log_line alogl
            JOIN vin_vin_auditlog_log alog ON alog.id = alogl.log_id
        """

    @property
    def _table_query(self):
        return f"SELECT {self._select_query()} FROM {self._from_query()}"
