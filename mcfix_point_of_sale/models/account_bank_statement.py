# Copyright 2018 Creu Blanca
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    @api.multi
    @api.constrains('company_id', 'pos_statement_id')
    def _check_company_id_pos_statement_id(self):
        for rec in self.sudo():
            if not rec.pos_statement_id.check_company(rec):
                raise ValidationError(
                    _('The Company in the Account Bank Statement Line and in '
                      'Pos Order must be the same.'))
