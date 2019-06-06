# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from ..tests import test_multicompany


class TestAccountCompanyConfig(test_multicompany.TestMulticompanyProperty):

    def test_company_config_defaults(self):
        purchase_tax = self.env['account.tax'].search([
            ('type_tax_use', 'in', ('purchase', 'all')),
            ('company_id', '=', self.company_1.id),
            ('id', 'not in', self.company_1.default_purchase_tax_id.ids),
        ], limit=1)
        sale_tax = self.env['account.tax'].search([
            ('type_tax_use', 'in', ('purchase', 'all')),
            ('company_id', '=', self.company_1.id),
            ('id', 'not in', self.company_1.default_sale_tax_id.ids),
        ], limit=1)
        ap_account = self.env['account.account'].create({
            'name': 'New default AR',
            'code': 'NAP',
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id,
            'reconcile': True,
            'company_id': self.company_1.id,
        })
        ar_account = self.env['account.account'].create({
            'name': 'New default AR',
            'code': 'NAR',
            'user_type_id': self.env.ref(
                'account.data_account_type_receivable').id,
            'reconcile': True,
            'company_id': self.company_1.id,
        })
        self.company_1.write({
            'default_purchase_tax_id': purchase_tax.id,
            'default_sale_tax_id': sale_tax.id,
            'partner_account_payable_id': ap_account.id,
            'partner_account_receivable_id': ar_account.id,
        })
        self.assertEqual(self.company_1.default_purchase_tax_id, purchase_tax)
        self.assertEqual(self.company_1.default_sale_tax_id, sale_tax)
        partner = self.env['res.partner'].create({
            'name': 'Test partner',
        })
        prop = partner.property_ids.filtered(
            lambda r: r.company_id == self.company_1
        )
        self.assertEqual(prop.property_account_payable_id, ap_account)
        self.assertEqual(prop.property_account_receivable_id, ar_account)
