from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
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

## 9/21
    ## work in class
    maintenance_ids = fields.One2many('maintenance.request','lease_id') 
    duration = fields.Integer(string='Duration (Months)', compute='_compute_duration', store=True)
    is_active = fields.Boolean(compute='_compute_is_active', string='Currently is Active')
    next_electric_recharge_date = fields.Date(string='Next Electric Recharge Date')
    maintenance_actual_costs = fields.Float(compute="_compute_maintenance_actual_costs", string='Maintenance Actual Costs')
    ## Task Required
    maintenance_plumbing_costs = fields.Float(compute="_compute_maintenance_types_costs", string='Maintenance Plumbing Actual Costs')
    maintenance_electrical_costs = fields.Float(compute="_compute_maintenance_types_costs", string='Maintenance Electrical Actual Costs')
    maintenance_air_condition_costs = fields.Float(compute="_compute_maintenance_types_costs", string='Maintenance Air Condition Actual Costs')
    maintenance_appliance_costs = fields.Float(compute="_compute_maintenance_types_costs", string='Maintenance Appliance Actual Costs')
    maintenance_other_costs = fields.Float(compute="_compute_maintenance_types_costs", string='Maintenance Other Actual Costs')
    
 ## Way 1 to compute maintenance costs by issue type
    @api.depends(
        'maintenance_ids.actual_cost',
        'maintenance_ids.issue_type'
    )
    def _compute_maintenance_types_costs(self):
        for lease in self:
            lease.maintenance_actual_costs = sum(
                request.actual_cost
                for request in lease.maintenance_ids
            )

            lease.maintenance_plumbing_costs = sum(
                request.actual_cost
                for request in lease.maintenance_ids
                if request.issue_type == 'plumbing'
            )

            lease.maintenance_electrical_costs = sum(
                request.actual_cost
                for request in lease.maintenance_ids
                if request.issue_type == 'electrical'
            )

            lease.maintenance_air_condition_costs = sum(
                request.actual_cost
                for request in lease.maintenance_ids
                if request.issue_type == 'air_condition'
            )

            lease.maintenance_appliance_costs = sum(
                request.actual_cost
                for request in lease.maintenance_ids
                if request.issue_type == 'appliance'
            )

            lease.maintenance_other_costs = sum(
                request.actual_cost
                for request in lease.maintenance_ids
                if request.issue_type == 'other'
            )


 ## Way 2 to compute maintenance costs by issue type
    # @api.depends(
    #     'maintenance_ids.actual_cost', 
    #     'maintenance_ids.issue_type'
    # )
    # def _compute_maintenance_types_costs(self):
    #         for lease in self:
    #             # Initial values
    #             lease.maintenance_plumbing_costs = 0.0
    #             lease.maintenance_electrical_costs = 0.0
    #             lease.maintenance_air_condition_costs = 0.0
    #             lease.maintenance_appliance_costs = 0.0
    #             lease.maintenance_other_costs = 0.0
    #             for maintenance in self.maintenance_ids:
    #                 if maintenance.issue_type == 'plumbing':
    #                     lease.maintenance_plumbing_costs += maintenance.actual_cost
    #                 elif maintenance.issue_type == 'electrical':
    #                     lease.maintenance_electrical_costs += maintenance.actual_cost
    #                 elif maintenance.issue_type == 'air_condition':
    #                     lease.maintenance_air_condition_costs += maintenance.actual_cost
    #                 elif maintenance.issue_type == 'appliance':
    #                     lease.maintenance_appliance_costs += maintenance.actual_cost
    #                 elif maintenance.issue_type == 'other':
    #                     lease.maintenance_other_costs += maintenance.actual_cost
                    
                       
## Task during class 9/21
    def action_submit_request_electricity(self):
            """Create maintenance request and notify manager"""
            self.ensure_one()
            # 1. Create maintenance.request record
            maintenance_request = self.env['maintenance.request'].create({
                'property_id': self.property_id.id,
                'lease_id': self.id,
                'issue_type': 'electrical',
                'description': 'Request for electricity recharge',
                'urgency': 'medium',
                'preferred_date': self.next_electric_recharge_date,
                'tenant_phone': self.tenant_id.phone,
                'state': 'submitted',
            })
            ## Go to the maintenance request form view after submission
            # return {
            #         'type': 'ir.actions.act_window',
            #         'res_model': 'maintenance.request',
            #         'res_id': maintenance_request.id,
            #         'views': [(False, 'form')],
            #         'target': 'current',
            #           }

            # Notify the manager (assuming the manager is a user in the system)
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

    ## Task during class 9/21
    @api.onchange('start_date')
    def next_electric_recharge(self):
        if self.start_date:
            self.next_electric_recharge_date = self.start_date + timedelta(days=30)
        else:
            self.next_electric_recharge_date = False   

    ## Task during class 9/21
    @api.depends('start_date', 'state')
    def _compute_is_active(self):
        today = fields.Date.today()
        for record in self:
            if record.state == 'active' or record.state == 'draft' and record.start_date and record.end_date:
                record.is_active = today >= record.start_date and today <= record.end_date
                record.state = 'active'
            else:
                record.is_active = False
    ## Task during class 9/21            
    @api.onchange('property_id')
    def _onchange_property_id(self):
        if self.property_id and not self.property_id.available:
            raise ValidationError("The selected property is not available for lease. Please choose another property.") 
        if self.property_id and self.property_id.price:
            self.monthly_rent = self.property_id.price
            self.deposit_paid = self.property_id.price * 0.10 
    ## Task during class 9/21
    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for record in self:
            if record.start_date and record.end_date:
                delta = record.end_date - record.start_date
                record.duration = delta.days // 30  # Approximate duration in months
            else:
                record.duration = 0


    ## Task during class 9/21
    @api.depends('maintenance_ids.actual_cost')
    def _compute_maintenance_actual_costs(self):
        for lease in self:
            lease.maintenance_actual_costs = sum(request.actual_cost for request in lease.maintenance_ids if request.actual_cost)
            
           

################## OLD TASKS BEFORE 9/21 ###################
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
    def convert_to_activate(self):
        """Activate the lease"""
        if not self.env.user.has_group('real_estate.group_tenant_manager'):
            raise UserError("You are not allowed to activate this lease it's only for Managers.")
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
    def write(self, vals):
            if not self.env.user.has_group('real_estate.group_lease_manager'):
                raise UserError("You are not allowed to modify this lease it's only for Managers.")
            return super(Lease, self).write(vals)
    def unlink(self):
            if not self.env.user.has_group('real_estate.group_lease_manager'):
                raise UserError("You are not allowed to delete this lease it's only for Managers.")
            return super(Lease, self).unlink()
    





     # for record in self:
            #     for maintenance in record.maintenance_ids:
            #         if maintenance.actual_cost:
            #             record.maintenance_actual_costs += maintenance.actual_cost
            #         else:
            #             record.maintenance_actual_costs += 0
            #  lease_maintenance_ids = self.env['maintenance.request'].search([('lease_id', '=', lease.id)])
            #             for maintenance in lease_maintenance_ids:
            #                 if ()