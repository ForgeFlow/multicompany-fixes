from odoo import api, fields, models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"
    _check_company_auto = True

    journal_id = fields.Many2one(check_company=True)
    company_id = fields.Many2one("res.company", required=True, readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super(AccountMoveReversal, self).default_get(fields_list)
        move_ids = (
            self.env["account.move"].browse(self.env.context["active_ids"])
            if self.env.context.get("active_model") == "account.move"
            else self.env["account.move"]
        )
        res["company_id"] = move_ids.company_id.id or self.env.company.id
        return res
