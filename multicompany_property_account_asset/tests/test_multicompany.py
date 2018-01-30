# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.multicompany_property_account.tests import test_multicompany


class TestMulticompanyProperty(test_multicompany.TestMulticompanyProperty):
    def test_product_template(self):
        super().test_product_template()
        category = self.env['account.asset.category'].search([
            ('type', '=', 'purchase'),
            ('company_id', '=', self.company_1.id)
        ], limit=1)
        if not category:
            account = self.env['account.account'].search([
                ('deprecated', '=', False),
                ('company_id', '=', self.company_1.id)
            ], limit=1)
            journal = self.env['account.journal'].search([
                ('company_id', '=', self.company_1.id)
            ], limit=1)
            category = self.env['account.asset.category'].create({
                'type': 'purchase',
                'company_id': self.company_1.id,
                'name': 'asset category',
                'account_asset_id': account.id,
                'account_depreciation_id': account.id,
                'account_depreciation_expense_id': account.id,
                'journal_id': journal.id
            })
        self.product_template.property_ids.filtered(
            lambda r: r.company_id == self.company_1
        ).asset_category_id = category
        self.assertEqual(
            self.product_template.with_context(
                force_company=self.company_1.id
            ).asset_category_id,
            category
        )
