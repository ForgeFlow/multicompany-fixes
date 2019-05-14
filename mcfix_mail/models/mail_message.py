from odoo import api, fields, models


class Message(models.Model):
    _inherit = 'mail.message'

    company_id = fields.Many2one('res.company', compute='_compute_company_id')

    @api.depends('model', 'res_id')
    def _compute_company_id(self):
        for record in self:
            object = self.env[record.model].browse(record.res_id)
            if 'company_id' in object._fields:
                record.company_id = object.company_id
            else:
                record.company_id = False
