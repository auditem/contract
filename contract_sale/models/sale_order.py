from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    contract_id = fields.Many2one(
        comodel_name='contract.contract',
        string='Contrato')
    contract_template_id = fields.Many2one(
        comodel_name='contract.template',
        string='Modelos de Contrato')
    
    def action_confirm(self):
        if self.contract_template_id and any(self.order_line.mapped('product_id').mapped('can_rental')):
            self.action_create_contract()

        return super().action_confirm()

    def action_create_contract(self):
        contract_env = self.env['contract.contract']
        if not contract_env.search_count([('sale_order_id', '=', self.id)]):
            contract = contract_env.create(self.get_contract_vals())
        
    def get_contract_vals(self):
        name = "CT{}".format(self.name[2:])
        vals = {
            'partner_id': self.partner_id.id,
            'contract_template_id': self.contract_template_id.id,
            'type': 'invoice',
            'pricelist_id': self.contract_template_id.pricelist_id.id,
            'payment_term_id': self.contract_template_id.payment_term_id.id,
            'fiscal_position_id': self.contract_template_id.fiscal_position_id.id,
            'recurring_interval': self.contract_template_id.recurring_interval,
            'recurring_invoicing_type': self.contract_template_id.recurring_invoicing_type,
            'recurring_rule_type': self.contract_template_id.recurring_rule_type,
            'sale_order_id': self.id,
            'name': name,
            'company_id': self.company_id.id,
            'contract_line_fixed_ids': self.get_contract_line_vals()
        }
        return vals
    
    def get_contract_line_vals(self):
        lines = []
        for line in self.order_line:
            if not line.product_id.can_rental:
                continue
            line_vals = {}
            line_vals = {
                'product_id': line.product_id.id,
                'quantity': line.product_uom_qty,
                'price_unit': line.product_uom.id,
                'name': line.name,
                'date_start': fields.Date.today(),
                'recurring_interval': self.contract_template_id.recurring_interval,
                'recurring_invoicing_type': self.contract_template_id.recurring_invoicing_type,
                'recurring_rule_type': self.contract_template_id.recurring_rule_type
            }
            lines.append([0, 0, line_vals])
        return lines
