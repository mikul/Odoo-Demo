from odoo import api, fields, models, _ 


class AccountMove(models.Model):
	_inherit = 'account.move'

	@api.model
	def _show_price(self):

		#2.a. Add a field that shows today's "metal price" (if it was added in the wizard)
		return self.env['metal.price'].search([('date','=',fields.Datetime.now().strftime('%Y-%m-%d')) ], limit=1).price

	metal_price = fields.Float(string='Metal Price', default=_show_price)

	def write(self, vals):
		#2.a. and it'll be saved along with the current date and it should appear in the metal price table.
		if 'metal_price' in vals:
			if vals.get('metal_price', 0) != 0:
				price_obj = self.env['metal.price'].search([('date','=',fields.Datetime.now().strftime('%Y-%m-%d'))])
				if price_obj:
					price_obj.write({'price':float(vals.get('metal_price', 0))})
				else:
					self.env['metal.price'].create({'date': fields.Datetime.now().strftime('%Y-%m-%d'), 'price': float(vals.get('metal_price', 0)) })

		return super(AccountMove, self).write(vals)

	@api.model_create_multi
	def create(self, vals_list):
		#2.a. and it'll be saved along with the current date and it should appear in the metal price table.
		for vals in vals_list:
			if 'metal_price' in vals:
				if vals.get('metal_price', 0) != 0:			
					price_obj = self.env['metal.price'].search([('date','=',fields.Datetime.now().strftime('%Y-%m-%d'))])
					if price_obj:
						price_obj.write({'price':float(vals.get('metal_price', 0))})
					else:
						self.env['metal.price'].create({'date': fields.Datetime.now().strftime('%Y-%m-%d'), 'price': float(vals.get('metal_price', 0)) })

		return super(AccountMove, self).create(vals_list)

	#3 In the customer (partner) form view add a smart button that displays the total of "quantity" column billed to that customer that has UoM of type "weight".
	@api.depends('line_ids')
	def _compute_with_weight_and_total(self):
		for record in self:
			with_weight = False
			total_weight = 0
			for x in record.line_ids:
				if x.product_uom_id.category_id.name == 'Weight':
					with_weight = True
					total_weight += x.quantity

			record.with_weight = with_weight
			record.total_weight = total_weight

	with_weight = fields.Boolean(default=False, compute='_compute_with_weight_and_total', store=True)


	total_weight = fields.Float(compute='_compute_with_weight_and_total', store=True)



