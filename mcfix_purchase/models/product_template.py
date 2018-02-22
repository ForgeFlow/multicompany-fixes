from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # @api.onchange('company_id')
    # def _onchange_company_id(self):
    #     super(ProductTemplate, self)._onchange_company_id()
    #     if self.company_id and self.route_ids:
    #         self.route_ids = self.env['stock.location.route'].search(
    #                 [('product_ids', 'in', [self.id]),
    #                  ('company_id', '=', False),
    #                  ('company_id', '=', self.company_id.id)])

    @api.multi
    @api.constrains('company_id', 'route_ids')
    def _check_company_id_route_ids(self):
        for rec in self.sudo():
            for line in rec.route_ids:
                if rec.company_id and line.company_id and\
                        rec.company_id != line.company_id:
                    raise ValidationError(
                        _('The Company in the Product Template and in '
                          'Stock Location Route (%s) must be the same.'
                          ) % line.name_get()[0][1])
