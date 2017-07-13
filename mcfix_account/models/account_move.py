from odoo import api, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def _get_default_journal(self):
        if self.env.context.get('default_journal_type'):
            return self.env['account.journal'].search(
                [('type', '=', self.env.context['default_journal_type']),
                 ('company_id', '=', self.env.user.company_id)],
                limit=1).id

    @api.multi
    @api.constrains('company_id')
    def constrain_company(self):
        for move in self:
            for line in move.line_ids:
                if line.account_id.company_id.id != move.company_id.id:
                    raise UserError('Company must be the same for all lines.')


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def auto_reconcile_lines(self):
        return super(AccountMoveLine,
                     self.with_context(check_move_validity=False)).\
                     auto_reconcile_lines()
