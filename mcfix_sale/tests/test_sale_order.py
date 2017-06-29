# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.addons.sale.tests.test_sale_common import TestSale


class TestSaleOrderMC(TestSale):

    def setUp(self):
        super(TestSaleOrderMC, self).setUp()
        self.res_users_model = self.env['res.users']

        # Company
        self.company = self.env.ref('base.main_company')

        # Company 2
        self.company_2 = self.env['res.company'].create({
            'name': 'Company 2',
        })
        # Multi-company access rights
        group_mc = self.env.ref('base.group_multi_company')
        self.manager.write({
           'groups_id': [(0, _, group_mc)]
        })
        self.user.write({
           'groups_id': [(0, _, group_mc)]
        })

        # Create crm teams for both companies
        self.crm_team_model = self.env['crm.team']
        self.team1 = self._create_crm_team(self.user1.id, self.company)
        self.team2 = self._create_crm_team(self.user2.id, self.company_2)


        self.pricelist_1 = self._create_pricelist(self.company)
        self.pricelist_2 = self._create_pricelist(self.company_2)

        self.tax_1 = self._create_tax(self.company)
        self.tax_2 = self._create_tax(self.company_2)

        self.fiscal_position_1 = self._create_tax(self.company)
        self.fiscal_position_2 = self._create_tax(self.company_2)

        self.payment_terms_1 = self._create_tax(self.company)
        self.payment_terms_2 = self._create_tax(self.company_2)

    def _create_crm_team(self, uid, company):
        """Create a crm team."""
        context = {'mail_create_nosubscribe': True}
        crm = self.crm_team_model.create(self, uid,
                                         {'name': 'CRM team',
                                          'company_id': company.id},
                                         context=context)
        return crm

    def _create_pricelist(self, company):
        pricelist = self.env['product.pricelist'].create({
            'name': 'Test Pricelist',
            'company_id': company.id,
        })
        return pricelist

    def _create_tax(self, company):
        pricelist = self.env['account.tax'].create({
            'name': 'Test tax',
            'company_id': company.id,
        })
        return pricelist

    def _create_fiscal_position(self, company):
        pricelist = self.env['account.fiscal.position'].create({
            'name': 'Test Fiscal Position',
            'company_id': company.id,
        })
        return pricelist

    def _create_payment_terms(self, company):
        terms = self.env['account.payment.term'].create({
            'name': 'Test payment Terms',
            'company_id': company.id,
        })
        return terms
