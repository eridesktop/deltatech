# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Deltatech All Rights Reserved
#                    Dorin Hongu <dhongu(@)gmail(.)com       
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, tools, _
from odoo.exceptions import except_orm, Warning, RedirectWarning
import odoo.addons.decimal_precision as dp
from odoo.api import Environment




class mail_send_to(models.TransientModel):
    """ Wizard to send document to partners and make them followers. """
    _name = 'mail.send.to'
    _description = 'Mail Send To'

    action_id = fields.Many2one('ir.actions.act_window', string = 'Documents to send')
    domain = fields.Char(string='Domain', help="Optional domain for further data filtering")
    
    partner_ids = fields.Many2many('res.partner', 'send_mail_to_partener_rel', 'send_mail_id','partner_id', 
                                      string='Recipients',help="List of partners that will be added as follower of the current document." )
    
    subject = fields.Char(string='Subject')
    message = fields.Html(string='Message')


    def go_step_1(self, cr, uid, ids, selected_ids, context=None):
        wizard_data = self.browse(cr,uid,ids,context)[0]

        model, res_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'deltatech_mail', 'action_mail_send_to_step1')
        action = self.pool[model].read(cr, uid, [res_id], context=context)[0]
        action['res_id'] = ids[0]
 
        action['context'] = "{'active_ids': [" +','.join(map(str,selected_ids)) + "]}"   
        return action


    @api.model
    def has_follower(self, res_model):
        document = self.env[res_model]
        res = False

        track = getattr(document, '_track','none')  
        if track != 'none':
            res = True

        return res

    @api.multi
    def do_send(self):
        for wizard in self:
            active_ids = self.env.context.get('active_ids', [])       
 
            #model = self.env[wizard.action_id.res_model]  #['ir.model'].search([('model','=', wizard.action_id.res_model)])
          
            documents = self.env[wizard.action_id.res_model].browse(active_ids)
            for document in documents: 
                new_follower_ids = [p.id for p in wizard.partner_ids]
                
                track = getattr(document, '_track','none')  
                if track != 'none':
                        document.message_subscribe(new_follower_ids)
                 
                message = self.env['mail.message'].with_context({'default_starred':True, 'mail_notify_noemail': False}).create({
                    'model': wizard.action_id.res_model,
                    'res_id': document.id,
                    'record_name': document.name_get()[0][1],
                    'email_from': self.env['mail.message']._get_default_from( ),
                    #'reply_to': self.env['mail.message']._get_default_from( ),
                    'subject': wizard.subject or '',
                    'body': wizard.message or wizard.subject,
                     
                    'message_id': self.env['mail.message']._get_message_id(  {'no_auto_thread': True} ),
                    'partner_ids': [(4, id) for id in new_follower_ids],
                    #'notified_partner_ids': [(4, id) for id in new_follower_ids]
                })
                


        return {'type': 'ir.actions.act_window_close'} 
    
 
     

    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:





