from odoo import api, fields, models, _ 

class PreOrder(models.Model):
	_name = 'pre.order'
	_description = 'Pre Order Form'

	name = fields.Char(string='Order No.')
	order_date = fields.Date(string='Order Date')
	details = fields.Text(string='Description')

	line_ids = fields.One2many('pre.order.line', 'order_id')


class PreOrderLine(models.Model):
	_name = 'pre.order.line'

	product_id = fields.Many2one('product.product', string='Item')
	qty = fields.Integer(string="Quantity")

	order_id = fields.Many2one('pre.order', ondelete='cascade')
