# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.account.tests.account_test_users import AccountTestUsers


class TestAccountInvoiceMC(AccountTestUsers):

    def setUp(self):
        super(TestAccountInvoiceMC, self).setUp()
        self.res_users_model = self.env['res.users']

        # Company
        self.company = self.env.ref('base.main_company')

        # Company 2
        self.company_2 = self.env['res.company'].create({
            'name': 'Company 2',
        })
        # Multi-company access rights
        group_mc = self.env.ref('base.group_multi_company')
        self.account_user.write({
           'groups_id': [(4, group_mc.id)]
        })
        self.account_manager.write({
           'groups_id': [(4, group_mc.id)],
           'company_ids': [(4, self.company_2.id )]
        })
        self.user_2 = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'user_2',
            'email': 'd.u@example.com',
            'signature': '--\ntest',
            'notify_email': 'always',
            'groups_id': [(6, 0, [group_mc.id])],
        })
        self.user_2.write({
            'company_ids': [(4, self.company_2.id)],
        })

        self.pricelist_1 = self._create_pricelist(self.company)
        self.pricelist_2 = self._create_pricelist(self.company_2)

        self.tax_1 = self._create_tax(self.company)
        self.tax_2 = self._create_tax(self.company_2)

        self.fiscal_position_1 = self._create_fiscal_position(self.company)
        self.fiscal_position_2 = self._create_fiscal_position(self.company_2)

        self.payment_terms_1 = self._create_payment_terms(self.company)
        self.payment_terms_2 = self._create_payment_terms(self.company_2)

        self.account_invoice_1 = self._create_account_invoice(self.company)
#        self.account_invoice_2 = self._create_account_invoice(self.company_2)

    def _create_pricelist(self, company):
        pricelist = self.env['product.pricelist'].create({
            'name': 'Test Pricelist',
            'company_id': company.id,
        })
        return pricelist

    def _create_tax(self, company):
        tax = self.env['account.tax'].create({
            'name': 'Test Tax',
            'company_id': company.id,
            'amount': 3.3,
        })
        return tax

    def _create_fiscal_position(self, company):
        fiscal_position = self.env['account.fiscal.position'].create({
            'name': 'Test Fiscal Position',
            'company_id': company.id,
        })
        return fiscal_position

    def _create_payment_terms(self, company):
        terms = self.env['account.payment.term'].create({
            'name': 'Test payment Terms',
            'company_id': company.id,
        })
        return terms

    def _create_account_invoice(self, company):
        invoice = self.env['account.invoice'].create({
            'partner_id': self.main_partner.id,
            'company_id': company.id,
        })
        return invoice

    def test_account_invoice_security(self):
        """ Test Security of Company Account Invoices"""
        # User in company 1
#        self.account_user.write({'company_id': self.company.id})
#        invoices = self.env['account.invoice'].sudo(self.account_user).search([
#            ('company_id', self.company_2.id)
#        ])
#        self.assertEqual(so_ids, [], "A user in company %s shouldn't be able "
#                                     "to see %s Invoices" % (
#            self.user.company_id.name, self.company_2.name))
