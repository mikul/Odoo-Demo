from odoo import api, fields, models, _ 

#3. In the customer (partner) form view add a smart button that displays the total of "quantity" column billed to that customer that has UoM of type "weight". 
#Behaves similar to the "invoiced" button so it should show the invoices when you click on it. Only invoices that has lines with UoM of type "weight" should appear.

class ResPartner(models.Model):
	_inherit = 'res.partner'

	def _invoice_total(self):
		self.total_invoiced = 0
		if not self.ids:
			return True

		all_partners_and_children = {}
		all_partner_ids = []
		for partner in self.filtered('id'):
			# price_total is in the company currency
			all_partners_and_children[partner] = self.with_context(active_test=False).search([('id', 'child_of', partner.id)]).ids
			all_partner_ids += all_partners_and_children[partner]

		domain = [
			('partner_id', 'in', all_partner_ids),
			('state', 'not in', ['draft', 'cancel']),
			('move_type', 'in', ('out_invoice', 'out_refund')),
		]
		price_totals = self.env['account.invoice.report'].read_group(domain, ['price_subtotal'], ['partner_id'])
		for partner, child_ids in all_partners_and_children.items():
			partner.total_invoiced = sum(price['price_subtotal'] for price in price_totals if price['partner_id'][0] in child_ids)

	def _count_invoice_total_weight(self):

		self.total_invoiced = 0
		if not self.ids:
			return True

		all_partners_and_children = {}
		all_partner_ids = []
		for partner in self.filtered('id'):
			# price_total is in the company currency
			all_partners_and_children[partner] = self.with_context(active_test=False).search([('id', 'child_of', partner.id)]).ids
			all_partner_ids += all_partners_and_children[partner]

		domain = [
			('partner_id', 'in', all_partner_ids),
			('state', 'not in', ['draft', 'cancel']),
			('move_type', 'in', ('out_invoice', 'out_refund')),
			('with_weight', '=', True)
		]
		price_totals = self.env['account.move'].read_group(domain, ['total_weight'], ['partner_id'])
		for partner, child_ids in all_partners_and_children.items():
			partner.invoice_total_weight_count = sum(price['total_weight'] for price in price_totals if price['partner_id'][0] in child_ids)



	invoice_total_weight_count = fields.Integer(string='Total Invoice Weight Count', compute='_count_invoice_total_weight', readonly=True)

	def action_view_invoice_total_weight(self):

		self.ensure_one()
		action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
		all_child = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
		action['domain'] = [
			('move_type', 'in', ('out_invoice', 'out_refund')),
			('partner_id', 'in', all_child.ids),
			('with_weight', '=', True)
		]
		action['context'] = {'default_move_type': 'out_invoice', 'move_type': 'out_invoice', 'journal_type': 'sale', 'search_default_unpaid': 1}
		return action

