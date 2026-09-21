from odoo import models, fields, api

class TenantWizard(models.TransientModel):
    _name = 'real.estate.tenant.wizard'
    _description = 'Tenant Request Wizard'
    
    lead_id = fields.Many2one('crm.lead',string="CRM", required=True)
    
    name = fields.Char(string='Tenant Name', required=True, index=True, tracking = True)
    email = fields.Char(string='Email', required=True, index=True, tracking = True)
    phone = fields.Char(string='Phone Number', tracking = True)
    mobile = fields.Char(string='Mobile Number', tracking = True)
    crm_lead_id = fields.Many2one('crm.lead', string='CRM Lead', ondelete='set null', index=True) 

    
    def action_submit_request(self):
        """Create maintenance request and notify manager"""
        self.ensure_one()
        
        
        # 1. Create maintenance.request record
        lead = self.env['real_estate.tenant'].sudo().create({
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'mobile': self.mobile,
            'crm_lead_id':self.lead_id.id
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
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': 'Request Submitted',
        #         'message': 'Your maintenance request has been submitted successfully and the manager has been notified.',
        #         'type': 'success',
        #         'sticky': False,
        #         'next': {'type': 'ir.actions.act_window_close'},
        #     },
        # }
         # 4. Opening a Created Record
        return {
        'type': 'ir.actions.act_window',
        'res_model': 'real_estate.tenant',
        'res_id': lead.id,
        'views': [(False, 'form')],
        'target': 'current',
          }