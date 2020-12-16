from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    can_rental = fields.Boolean(string='Pode ser Alugado')
    
