from odoo import api, models, _
from odoo.exceptions import UserError


class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.model
    def create(self, values):
        config_id = values.get('config_id') or \
            self.env.context.get('default_config_id')
        if not config_id:
            raise UserError(
                _("You should assign a Point of Sale to your session."))
        pos_config = self.env['pos.config'].browse(config_id)
        ctx = dict(self.env.context, company_id=pos_config.company_id.id)
        if not pos_config.journal_ids:
            journal_model = self.env['account.journal']
            journals = journal_model.with_context(ctx).search(
                [('journal_user', '=', True), ('type', '=', 'cash'),
                 ('company_id', '=', pos_config.company_id.id)])
            if not journals:
                journals = journal_model.with_context(ctx).search(
                    [('type', '=', 'cash'),
                     ('company_id', '=', pos_config.company_id.id)])
                if not journals:
                    journals = journal_model.with_context(ctx).search(
                        [('journal_user', '=', True),
                         ('company_id', '=', pos_config.company_id.id)])
            journals.sudo().write({'journal_user': True})
            pos_config.sudo().write({'journal_ids': [(6, 0, journals.ids)]})

        return super(PosSession, self).create(values)
