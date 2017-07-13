from odoo import models, api, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    @api.one
    def get_current_company(self):
        self.current_company_id = self.env['res.company'].\
            browse(self._context.get('force_company') or
                   self.env.user.company_id.id).ensure_one()

    current_company_id = fields.Many2one(
        comodel_name='res.company',
        default=get_current_company,
        compute='get_current_company',
        store=False
    )


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.one
    def get_current_company(self):
        self.current_company_id = self.env['res.company'].\
            browse(self._context.get('force_company') or
                   self.env.user.company_id.id).ensure_one()

    current_company_id = fields.Many2one(
        comodel_name='res.company',
        default=get_current_company,
        compute='get_current_company',
        store=False
    )
