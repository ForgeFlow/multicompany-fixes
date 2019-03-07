# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def get_mcfix_domain(self, company):
        return [
            '|', ('company_id', '=', False),
            ('company_id', '=', company),
        ]

    @api.model
    def _multicompany_args(self, args):
        if self.env.context.get(
            'mcfix_widget_company', False
        ) and 'company_id' in self._fields and self._fields[
            'company_id'
        ].store:
            add_company = True
            for arg in args:
                if isinstance(arg, (list, tuple)):
                    if arg[0] == 'company_id':
                        add_company = False
                        break
            if add_company:
                args += self.get_mcfix_domain(self.env.context.get(
                    'mcfix_widget_company'))
        return args

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        args = self._multicompany_args(args)
        return super().search(
            args, offset=offset, limit=limit, order=order, count=count)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = self._multicompany_args(list(args or []))
        return super().name_search(
            name=name, args=args, operator=operator, limit=limit)
