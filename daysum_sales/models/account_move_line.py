from odoo import api, fields, models, _ 
from odoo.exceptions import ValidationError

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	#2.b ii. "Quantity" should be required. Show an alert message if a value is entered in "total" while "quantity" is empty.
	@api.constrains('quantity', 'product_uom_id')
	def _check_quantity(self):
		for move in self:
			if move.product_uom_id.category_id.name == 'Weight' and move.quantity == 0:
				raise ValidationError("Quantity should not be zero for Weight.")

