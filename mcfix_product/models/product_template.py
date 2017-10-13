# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(ProductTemplate, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

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

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.pricelist_id = False

    @api.multi
    @api.constrains('pricelist_id', 'company_id')
    def _check_company_pricelist_id(self):
        for template in self.sudo():
            if template.company_id and template.pricelist_id.company_id and \
                    template.company_id != template.pricelist_id.company_id:
                raise ValidationError(
                    _('The Company in the Product Template and in '
                      'Pricelist must be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            pricelist_item = self.env['product.pricelist.item'].search(
                [('product_tmpl_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if pricelist_item:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Product Template is assigned to Pricelist Item '
                      '%s.' % pricelist_item.name))
            supplierinfo = self.env['product.supplierinfo'].search(
                [('product_tmpl_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if supplierinfo:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Product Template is assigned to Supplierinfo '
                      '%s.' % supplierinfo.name))
