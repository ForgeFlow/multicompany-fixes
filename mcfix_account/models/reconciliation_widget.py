from odoo import api, models


class AccountReconciliation(models.AbstractModel):
    _inherit = "account.reconciliation.widget"

    @api.model
    def get_data_for_manual_reconciliation(
        self, res_type, res_ids=None, account_type=None
    ):
        rows = []
        for company in self.env.companies:
            rows += super(
                AccountReconciliation,
                self.with_context(allowed_company_ids=company.ids),
            ).get_data_for_manual_reconciliation(res_type, res_ids, account_type)
        return [r for r in rows if r["reconciliation_proposition"]] + [
            r for r in rows if not r["reconciliation_proposition"]
        ]
