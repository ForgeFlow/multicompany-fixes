# Copyright 2018 ForgeFlow, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import time
import logging
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class TestPurchaseOrder(TransactionCase):

    def setUp(self):
        super(TestPurchaseOrder, self).setUp()
        employees_group = self.env.ref('base.group_user')
        multi_company_group = self.env.ref('base.group_multi_company')
        purchase_manager_group = self.env.ref(
            'purchase.group_purchase_manager')
        self.po_model = self.env['purchase.order']
        self.pol_model = self.env['purchase.order.line']
        manager_purchase_test_group = self.create_full_access(
            ['purchase.order'])
        self.company = self.env['res.company'].create(
            self.create_company('Test company')
        )
        self.company_2 = self.env['res.company'].create(
            self.create_company('Test company 2', self.company.id)
        )
        self.env.user.company_ids += self.company
        self.env.user.company_ids += self.company_2

        self.user = self.env['res.users'].with_user(self.env.user).with_context(
            no_reset_password=True).create(
            {'name': 'Test User',
             'login': 'test_user',
             'email': 'test@oca.com',
             'groups_id': [(6, 0, [employees_group.id,
                                   purchase_manager_group.id,
                                   multi_company_group.id,
                                   manager_purchase_test_group.id])],
             'company_id': self.company.id,
             'company_ids': [(4, self.company.id), (4, self.company_2.id)],
             })

        self.partner = self.env['res.partner'].with_user(self.user).create({
            'name': 'Partner Test',
            'company_id': self.company.id,
            'is_company': True,
        })

    def create_full_access(self, list_of_models):
        manager_purchase_test_group = self.env['res.groups'].sudo().create({
            'name': 'group_manager_purchase_test'
        })
        for model in list_of_models:
            model_id = self.env['ir.model'].sudo().search(
                [('model', '=', model)])
            if model_id:
                access = self.env['ir.model.access'].sudo().create({
                    'name': 'full_access_%s' % model.replace(".", "_"),
                    'model_id': model_id.id,
                    'perm_read': True,
                    'perm_write': True,
                    'perm_create': True,
                    'perm_unlink': True,
                })
                access.group_id = manager_purchase_test_group
        return manager_purchase_test_group

    def create_company(self, name, parent_id=False):
        dict_company = {
            'name': name,
            'parent_id': parent_id,
        }
        return dict_company

    def test_onchanges(self):
        self.po_1 = self.po_model.with_user(self.user).new({
            'name': 'Purchase - Test',
            'partner_id': self.partner.id,
            'company_id': self.company_2.id,
            'currency_id': self.env.ref('base.EUR').id,
            'date_planned': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        })
        self.po_1._onchange_company_id()
        self.assertFalse(self.po_1.partner_id)

    def test_constrains(self):
        self.po_1 = self.po_model.with_user(self.user).create({
            'name': 'Asset - Test',
            'partner_id': self.partner.id,
            'company_id': self.company.id,
            'currency_id': self.env.ref('base.EUR').id,
            'date_planned': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        })
        with self.assertRaises(UserError):
            self.po_1.company_id = self.company_2
