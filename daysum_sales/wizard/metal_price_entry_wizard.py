from datetime import date, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

# 1.  has a table that takes a daily "Metal price" and current date "Date". It should display historical data from previous days. "Date" should by default show the current date but it could be edited.
class MetalPriceEntryWizard(models.TransientModel):
	_name = 'metal.price.entry.wizard'
	_description = 'Metal Price Entry'

	date = fields.Date(string='Date', default=fields.Datetime.now)
	price = fields.Float(string='Metal Price')

	#1. by default show the current date but it could be edited.
	@api.model
	def _show_prices(self):
		return [{'date':x.date, 'price':x.price} for x in self.env['metal.price'].search([])]


	metal_price_lines = fields.One2many('metal.price.line.entry.wizard', 'metal_line_id', string='Metal Prices', default=_show_prices)

	def do_action(self):
		self.env['metal.price'].create({
				'price': self.price,
				'date': self.date})




class MetalPriceEntryLineWizard(models.TransientModel):
	_name = 'metal.price.line.entry.wizard'
	_description = 'Metal Price Line Entry'

	date = fields.Date(string='Date')
	price = fields.Float(string='Metal Price')

	metal_line_id = fields.Many2one('metal.price.entry.wizard', 'Metal Price Entry')

