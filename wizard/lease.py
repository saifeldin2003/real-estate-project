from odoo import models, fields, api

class LeaseWizard(models.TransientModel):
    _name = 'real.estate.lease.wizard'
    _description = 'Maintenance Request Wizard'
    
    property_id = fields.Many2one('real_estate.property',string="Property", required=True)
    tenant_id = fields.Many2one(
            'real_estate.tenant',
            string='Tenant',
            required=True,
            ondelete='cascade',
            index=True
        )    
    name = fields.Char(string='Lease Reference', required=True, default='New')
    
    user_id = fields.Many2one('res.users', string='Related User', index=True)
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
        
    def action_view_tenant(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tenant',
            'res_model': 'real_estate.tenant',
            'view_mode': 'form',
            'res_id': self.tenant_id.id,
            'target': 'current',
        }
    def action_submit_request(self):
        """Create maintenance request and notify manager"""
        self.ensure_one()
        
        # 1. Create maintenance.request record
        lease = self.env['real_estate.lease'].create({
            'property_id': self.property_id.id,
            'tenant_id': self.tenant_id.id,
            'user_id': self.user_id.id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'monthly_rent': self.monthly_rent,
            'deposit_paid': self.deposit_paid,
            'state': self.state,
        })
        
        # 2. Send notification to property manager (Agent)
        # if self.property_id.agent_id:
        #     maintenance_request.activity_schedule(
        #         'mail.mail_activity_data_todo',
        #         user_id=self.property_id.agent_id.id,
        #         summary=f"New {self.issue_type.capitalize()} Maintenance Request",
        #         note=f"Urgency: {self.urgency}\nDescription: {self.description}"
        #     )
        
        # 3. Return action to close wizard and show confirmation
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Request Submitted',
                'message': 'Your maintenance request has been submitted successfully and the manager has been notified.',
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }