from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.one
    def _compute_current_company_id(self):
        self.current_company_id = self.env['res.company'].browse(
            self._context.get('force_company') or
            self.env.user.company_id.id).ensure_one()

    current_company_id = fields.Many2one(
        comodel_name='res.company',
        default=_compute_current_company_id,
        compute='_compute_current_company_id',
        store=False
    )
