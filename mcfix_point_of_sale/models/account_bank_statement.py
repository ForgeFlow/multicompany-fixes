# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    @api.onchange('company_id')
    def onchange_company_id(self):
        super(AccountBankStatement, self).onchange_company_id()
        self.account_id = False

    @api.multi
    @api.constrains('account_id', 'company_id')
    def _check_company_account_id(self):
        for bank_statement in self.sudo():
            if bank_statement.company_id and bank_statement.account_id.\
                    company_id and bank_statement.company_id != bank_statement\
                    .account_id.company_id:
                raise ValidationError(
                    _('The Company in the Bank Statement and in '
                      'Account must be the same.'))
        return True


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    @api.onchange('company_id')
    def onchange_company_id(self):
        super(AccountBankStatementLine, self).onchange_company_id()
        self.pos_statement_id = False

    @api.multi
    @api.constrains('pos_statement_id', 'company_id')
    def _check_company_pos_statement_id(self):
        for bank_statement_line in self.sudo():
            if bank_statement_line.company_id and bank_statement_line.\
                    pos_statement_id.company_id and bank_statement_line.\
                    company_id != bank_statement_line.pos_statement_id.\
                    company_id:
                raise ValidationError(
                    _('The Company in the Bank Statement Line and in '
                      'POS statement must be the same.'))
        return True
