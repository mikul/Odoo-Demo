from odoo import api, fields, models, _ 


#Metal Price Table
class MetalPrice(models.Model):
	_name = 'metal.price'
	_description = 'Metal Price Table'
	_order = 'date desc'

	date = fields.Date(string='Date', index=True, copy=False, default=fields.Datetime.now)
	price = fields.Float(string='Metal Price')
