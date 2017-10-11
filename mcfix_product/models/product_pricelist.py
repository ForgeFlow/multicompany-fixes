# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(Pricelist, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], rec.company_id.name) if \
                rec.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            if not rec.company_id:
                continue
            pricelist_item = self.env['product.pricelist.item'].search(
                [('base_pricelist_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if pricelist_item:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Pricelist is assigned to Pricelist Item '
                      '%s.' % pricelist_item.name))
            pricelist_item = self.env['product.pricelist.item'].search(
                [('pricelist_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if pricelist_item:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Pricelist is assigned to Pricelist Item '
                      '%s.' % pricelist_item.name))
            template = self.env['product.template'].search(
                [('pricelist_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if template:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Pricelist is assigned to Product Template '
                      '%s.' % template.name))


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(ProductPricelistItem, self).name_get()
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
        self.base_pricelist_id = False
        self.pricelist_id = False

    @api.multi
    @api.constrains('product_tmpl_id', 'company_id')
    def _check_company_product_tmpl_id(self):
        for pricelist_item in self.sudo():
            if pricelist_item.company_id and pricelist_item.product_tmpl_id.\
                    company_id and pricelist_item.company_id != pricelist_item\
                    .product_tmpl_id.company_id:
                raise ValidationError(
                    _('The Company in the Pricelist Item and in '
                      'Product Template must be the same.'))
        return True

    @api.multi
    @api.constrains('base_pricelist_id', 'company_id')
    def _check_company_base_pricelist_id(self):
        for pricelist_item in self.sudo():
            if pricelist_item.company_id and pricelist_item.base_pricelist_id.\
                    company_id and pricelist_item.company_id != pricelist_item\
                    .base_pricelist_id.company_id:
                raise ValidationError(
                    _('The Company in the Pricelist Item and in '
                      'Pricelist must be the same.'))
        return True

    @api.multi
    @api.constrains('pricelist_id', 'company_id')
    def _check_company_pricelist_id(self):
        for pricelist_item in self.sudo():
            if pricelist_item.company_id and pricelist_item.pricelist_id.\
                    company_id and pricelist_item.company_id != pricelist_item\
                    .pricelist_id.company_id:
                raise ValidationError(
                    _('The Company in the Pricelist Item and in '
                      'Pricelist must be the same.'))
        return True
