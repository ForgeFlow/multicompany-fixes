# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class StockLocation(models.Model):
    _inherit = 'stock.location'

    @api.onchange('company_id')
    def onchange_company_id(self):
        super(StockLocation, self)._check_company_id()
        self.valuation_in_account_id = False
        self.valuation_out_account_id = False

    @api.multi
    @api.constrains('valuation_in_account_id', 'company_id')
    def _check_company_valuation_in_account_id(self):
        for location in self.sudo():
            if location.company_id and location.valuation_in_account_id and \
                    location.company_id != location.valuation_in_account_id.\
                    company_id:
                raise ValidationError(_('The Company in the Location and in '
                                        'Valuation Account must be the same.'))
        return True

    @api.multi
    @api.constrains('valuation_out_account_id', 'company_id')
    def _check_company_valuation_out_account_id(self):
        for location in self.sudo():
            if location.company_id and location.valuation_out_account_id and \
                    location.company_id != location.valuation_out_account_id.\
                    company_id:
                raise ValidationError(_('The Company in the Location and in '
                                        'Valuation Account must be the same.'))
        return True
