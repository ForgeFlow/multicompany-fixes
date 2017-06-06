from odoo import models


class MulticomanyPropertyAbstract(models.AbstractModel):
    _name = 'multicompany.abstract'

    @staticmethod
    def get_property(prop, field, default):
        return getattr(prop, field, default) or default if prop else default
