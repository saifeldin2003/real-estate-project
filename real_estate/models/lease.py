from odoo import models, fields, api
from odoo.exceptions import UserError
class Lease(models.Model):
    _name = 'real_estate.lease'
    _description = 'Property Lease Agreement'
    
    name = fields.Char(string='Lease Reference', required=True, default='New')
    property_id = fields.Many2one(
        'real_estate.property',
        string='Property',
        required=True,
        ondelete='cascade',  # If property deleted, delete lease too
        index=True
    )
    tenant_id = fields.Many2one(
        'real_estate.tenant',
        string='Tenant',
        required=True,
        ondelete='cascade',
        index=True
    )
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    monthly_rent = fields.Float(string='Monthly Rent', required=True)
    deposit_paid = fields.Float(string='Deposit Paid')
    state = fields.Selection([
    ('draft', 'Draft'),
    ('active', 'Active'),
    ('at_risk', 'At Risk'),
    ('expired', 'Expired'),
    ('cancelled', 'Cancelled'),
        ], string='Status', default='draft', required=True)
    
    def convert_to_activate(self):
        """Activate the lease"""
        for record in self:
            record.write({'state': 'active'})
    def convert_to_draft(self):
            """Convert the lease to draft"""
            for record in self:
                record.write({'state': 'draft'})        
    def convert_right(self):
        """Mark the lease as at risk"""
        stages = ['draft', 'active', 'at_risk', 'expired', 'cancelled']
        for record in self:
            if record.state in stages:
                current_index = stages.index(record.state)
                if current_index + 1 < len(stages):
                    record.write({'state': stages[current_index + 1]})
    def convert_left(self):
        """Mark the lease as draft"""
        stages = ['draft', 'active', 'at_risk', 'expired', 'cancelled']
        for record in self:
            if record.state in stages:
                current_index = stages.index(record.state)
                if current_index > 0:
                    record.write({'state': stages[current_index - 1]})
    @api.model
    def create(self, vals):
        """Override create to generate lease reference"""
        # if vals.get('name', 'New') == 'New':
        vals['name'] = self.env['ir.sequence'].next_by_code('real_estate.lease')
        return super(Lease, self).create(vals)                
    
    def copy(self, default=None):
        # raise UserError("You cannot duplicate a lease record.")
         default = default or {}
         default['name'] = self.env['ir.sequence'].next_by_code('real_estate.lease')
         return super().copy(default)