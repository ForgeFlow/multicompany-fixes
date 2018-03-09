# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class TestPointOfSale(TransactionCase):

    def setUp(self):
        super(TestPointOfSale, self).setUp()
        employees_group = self.env.ref('base.group_user')
        multi_company_group = self.env.ref('base.group_multi_company')
        pos_manager_group = self.env.ref('point_of_sale.group_pos_manager')
        self.pos_model = self.env['pos.order']
        self.journal_model = self.env['account.journal']
        manager_pos_test_group = self.create_full_access(
            ['pos.order', 'pos.order.line', 'product.pricelist',
             'product.pricelist.item', 'account.journal', 'account.move',
             'account.move.line', 'account.reconcile.model',
             'account.payment', 'account.asset.category'])
        self.company = self.env['res.company'].create(
            self.create_company('Test company')
        )
        self.company_2 = self.env['res.company'].create(
            self.create_company('Test company 2', self.company.id)
        )
        self.env.user.company_ids += self.company
        self.env.user.company_ids += self.company_2

        self.user = self.env['res.users'].sudo(self.env.user).with_context(
            no_reset_password=True).create(
            {'name': 'Test User',
             'login': 'test_user',
             'email': 'test@oca.com',
             'groups_id': [(6, 0, [employees_group.id,
                                   pos_manager_group.id,
                                   multi_company_group.id,
                                   manager_pos_test_group.id])],
             'company_id': self.company.id,
             'company_ids': [(4, self.company.id)],
             })

        self.pricelist = self.env['product.pricelist'].sudo(self.user).create({
            'name': 'Pricelist Test',
            'currency_id': self.env.ref('base.EUR').id,
            'company_id': self.company.id,
        })

        self.sale_journal = self.journal_model.sudo(self.user).create({
            'name': 'Sale Journal 1 - Test',
            'code': 'test_sale_1',
            'type': 'sale',
            'company_id': self.company.id,
        })

        self.pos_config = self.env['pos.config'].sudo(self.user).create({
            'name': 'Config Test',
            'company_id': self.company.id,
            'journal_id': self.sale_journal.id,
        })

        self.pos_session = self.env['pos.session'].sudo(self.user).create({
            'user_id': self.user.id,
            'config_id': self.pos_config.id,
        })

    def create_full_access(self, list_of_models):
        manager_pos_test_group = self.env['res.groups'].sudo().create({
            'name': 'group_manager_pos_test'
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
                access.group_id = manager_pos_test_group
        return manager_pos_test_group

    def create_company(self, name, parent_id=False):
        dict_company = {
            'name': name,
            'parent_id': parent_id,
        }
        return dict_company

    def test_constrains(self):
        self.pos_1 = self.pos_model.sudo(self.user).create({
            'name': 'Pos - Test',
            'pricelist_id': self.pricelist.id,
            'company_id': self.company.id,
            'session_id': self.pos_session.id,
        })
        with self.assertRaises(ValidationError):
            self.pos_1.company_id = self.company_2
