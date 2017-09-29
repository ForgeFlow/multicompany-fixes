# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.multi
    @api.depends('company_id')
    def name_get(self):
        res = []
        names = super(StockQuant, self).name_get()
        multicompany_group = self.env.ref('base.group_multi_company')
        if multicompany_group not in self.env.user.groups_id:
            return names
        for name in names:
            rec = self.browse(name[0])
            name = '%s [%s]' % (name[1], name.company_id.name) if \
                name.company_id else name[1]
            res += [(rec.id, name)]
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.consumed_quant_ids = False
        self.produced_quant_ids = False
        self.location_id = False
        self.propagated_from_id = False
        self.negative_dest_location_id = False

    @api.multi
    @api.constrains('consumed_quant_ids', 'company_id')
    def _check_company_consumed_quant_ids(self):
        for quant in self.sudo():
            for stock_quant in quant.consumed_quant_ids:
                if quant.company_id and \
                        quant.company_id != stock_quant.company_id:
                    raise ValidationError(
                        _('The Company in the Quant and in '
                          'Consumed Quant must be the same.'))
        return True

    @api.multi
    @api.constrains('produced_quant_ids', 'company_id')
    def _check_company_produced_quant_ids(self):
        for quant in self.sudo():
            for stock_quant in quant.produced_quant_ids:
                if quant.company_id and \
                        quant.company_id != stock_quant.company_id:
                    raise ValidationError(
                        _('The Company in the Quant and in '
                          'Produced Quant must be the same.'))
        return True

    @api.multi
    @api.constrains('location_id', 'company_id')
    def _check_company_location_id(self):
        for quant in self.sudo():
            if quant.company_id and quant.location_id and \
                    quant.company_id != quant.location_id.company_id:
                raise ValidationError(_('The Company in the Quant and in '
                                        'Location must be the same.'))
        return True

    @api.multi
    @api.constrains('propagated_from_id', 'company_id')
    def _check_company_propagated_from_id(self):
        for quant in self.sudo():
            if quant.company_id and quant.propagated_from_id and \
                    quant.company_id != quant.propagated_from_id.company_id:
                raise ValidationError(_('The Company in the Quant and in '
                                        'Linked Quant must be the same.'))
        return True

    @api.multi
    @api.constrains('negative_dest_location_id', 'company_id')
    def _check_company_negative_dest_location_id(self):
        for quant in self.sudo():
            if quant.company_id and quant.negative_dest_location_id and \
                    quant.company_id != quant.negative_dest_location_id.\
                    company_id:
                raise ValidationError(_('The Company in the Quant and in '
                                        'Negative Destination Location must '
                                        'be the same.'))
        return True

    @api.constrains('company_id')
    def _check_company_id(self):
        for rec in self:
            quant = self.search(
                [('consumed_quant_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if quant:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Consumed Quant is assigned to Quant '
                      '%s.' % quant.name))
            quant = self.search(
                [('produced_quant_ids', 'in', [rec.id]),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if quant:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Produced Quant is assigned to Quant '
                      '%s.' % quant.name))
            quant = self.search(
                [('propagated_from_id', '=', rec.id),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if quant:
                raise ValidationError(
                    _('You cannot change the company, as this '
                      'Linked Quant is assigned to Quant '
                      '%s.' % quant.name))
