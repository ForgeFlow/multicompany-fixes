# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    @api.one
    def _compute_current_company(self):
        self.current_company_id = self.env['res.company'].\
            browse(self._context.get('force_company') or
                   self.env.user.company_id.id).ensure_one()

    current_company_id = fields.Many2one(
        comodel_name='res.company',
        default=_compute_current_company,
        compute='_compute_current_company',
        store=False
    )


class ProductPriceHistory(models.Model):
    _inherit = 'product.price.history'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(ProductPriceHistory, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res


class Supplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(Supplierinfo, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.product_tmpl_id = False

    @api.multi
    @api.constrains('product_tmpl_id', 'company_id')
    def _check_company_product_tmpl_id(self):
        for supplierinfo in self.sudo():
            if supplierinfo.company_id and supplierinfo.product_tmpl_id.\
                    company_id and supplierinfo.company_id != supplierinfo.\
                    product_tmpl_id.company_id:
                raise ValidationError(
                    _('The Company in the Supplierinfo and in '
                      'Product Template must be the same.'))
        return True
