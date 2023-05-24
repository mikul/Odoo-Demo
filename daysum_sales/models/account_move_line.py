from odoo import api, fields, models, _ 
from odoo.exceptions import ValidationError

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	#2.b ii. "Quantity" should be required. Show an alert message if a value is entered in "total" while "quantity" is empty.
	@api.constrains('quantity', 'product_uom_id')
	def _check_quantity(self):
		for move in self:
			if move.product_uom_id.category_id.name == 'Weight' and move.quantity == 0 and move.price_total != 0:
				raise ValidationError("Quantity should not be zero for Weight.")

	@api.depends('product_uom_id')
	def _compute_weight_uom(self):
		for record in self:
			if record.product_uom_id.category_id.name == 'Weight':
				record.if_weight_uom = True

	if_weight_uom = fields.Boolean(default=False, compute=_compute_weight_uom, store=True)

	#2.b Make account move line "total" field editable for products that has a UoM of type "weight" only.
	@api.depends('quantity', 'discount', 'price_unit', 'tax_ids', 'currency_id')
	def _compute_totals(self):
		for line in self:
			if not line.if_weight_uom:
				if line.display_type != 'product':
					line.price_total = line.price_subtotal = False
				# Compute 'price_subtotal'.
				line_discount_price_unit = line.price_unit * (1 - (line.discount / 100.0))
				subtotal = line.quantity * line_discount_price_unit

				# Compute 'price_total'.
				if line.tax_ids:
					taxes_res = line.tax_ids.compute_all(
						line_discount_price_unit,
						quantity=line.quantity,
						currency=line.currency_id,
						product=line.product_id,
						partner=line.partner_id,
						is_refund=line.is_refund,
					)
					line.price_subtotal = taxes_res['total_excluded']
					line.price_total = taxes_res['total_included']
				else:
					line.price_total = line.price_subtotal = subtotal

	@api.onchange('price_total')
	def _onchange_compute_price_unit(self):
		for line in self:

			if line.if_weight_uom:
				if line.quantity == 0:
					raise ValidationError("Quantity should not be zero for Weight.")
					
				if line.display_type != 'product':
					line.price_total = line.price_subtotal = False


				if line.tax_ids:
					taxes_res = line.tax_ids.compute_price(
						line.price_total,
						quantity=line.quantity,
						currency=line.currency_id,
						product=line.product_id,
						partner=line.partner_id,
						is_refund=line.is_refund,
					)
					price_subtotal = taxes_res['subtotal']
				else:
					price_subtotal	= line.price_total

				line_discount_price_unit = price_subtotal / line.quantity
				line.price_unit = line_discount_price_unit / (1 - (line.discount / 100.0))
				line.price_subtotal = price_subtotal

	price_subtotal = fields.Monetary(
		string='Subtotal',
		compute='_compute_totals', store=True,
		inverse='_onchange_compute_price_unit',
		currency_field='currency_id'
	)
	price_total = fields.Monetary(
		string='Total',
		# compute='_compute_totals', store=True,
		currency_field='currency_id', readonly=False
	)




class AccountTax(models.Model):
	_inherit = 'account.tax'

	def compute_price(self, total, currency=None, quantity=1.0, product=None, partner=None, is_refund=False, handle_price_include=True, include_caba_tags=False, fixed_multiplicator=1):
		subtotal = total
		tax = 0
		if not self:
			company = self.env.company
		else:
			company = self[0].company_id

		taxes, groups_map = self.flatten_taxes_hierarchy(create_map=True)

		prec = currency.rounding

		round_tax = False if company.tax_calculation_rounding_method == 'round_globally' else True
		if 'round' in self.env.context:
			round_tax = bool(self.env.context['round'])

		if not round_tax:
			prec *= 1e-5
		if not currency:
			currency = company.currency_id


		#subtotal = total / tax_decimal + 1 

		for tax in taxes:
			if tax.type_tax_use == 'sale' and tax.amount_type == 'percent':
				subtotal = currency.round(total / ((tax.amount / 100) + 1))


		return { 'subtotal': subtotal}

