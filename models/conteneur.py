from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
import logging 
import random

_logger = logging.getLogger(__name__)


class Conteneur(models.Model):
    _name = 'envoi.colis.conteneur'
    _description = 'Conteneur pour envoi de colis'
    _rec_name = 'display_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    display_name = fields.Char(string='Nom d\'affichage', compute='_compute_display_name', store=True, readonly=False)
    conteneur_id = fields.Char(string='ID Conteneur', default=lambda self: 'CON' + str(random.randint(100000, 999999)), readonly=True)
    matricule = fields.Char(string='Matricule', required=True)
    
    type = fields.Char(string="Type")
    capacite_totale = fields.Integer(string="Poids total")
    poids_disponibles = fields.Float(string='Poids disponible', compute='_compute_poids_disponibles')
    expedition_ids = fields.One2many('envoi.colis.expedition', 'conteneur_id', string='Expéditions')
    total_expeditions = fields.Integer(string='Expéditions', compute='_compute_totals')
    total_colis = fields.Integer(string='Colis', compute='_compute_totals')
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.ref('base.EUR').id)
    date_depart = fields.Date(string='Date de départ')
    date_arrivee = fields.Date(string="Date d'arrivée")
    state = fields.Selection (selection=[
        ('default', 'Default'),
        ('prepare', 'Prepare'), 
        ('expedie', 'Expedie'), 
        ('transit', 'En Transit'), 
        ('arrive', 'Arrive')], string='Suivi du statut', tracking=True, default='default')
    
    
    @api.depends('conteneur_id')
    def _compute_display_name(self):
        for record in self:
            if record.conteneur_id:
                record.display_name = f"Container {record.conteneur_id} - {record.matricule}"
            else:
                record.display_name = f"New Container"

    @api.depends('expedition_ids')
    def _compute_totals(self):
        for record in self:
            record.total_expeditions = len(record.expedition_ids)
            record.total_colis = sum(expedition.nombre_colis for expedition in record.expedition_ids)
            #record.total_cout = sum(expedition.cout_final for expedition in record.expedition_ids)

    @api.depends('capacite_totale', 'expedition_ids')
    def _compute_poids_disponibles(self):
        for record in self :
            record.poids_disponibles = record.capacite_totale - sum(expedition.colis_id.poids for expedition in record.expedition_ids)


    @api.depends('expedition_ids.invoice_line_id.move_id')
    def _compute_invoices_generated(self):
        for rec in self:
            rec.invoices_generated_ids = rec.expedition_ids.mapped('invoice_line_id.move_id')


    def action_create_expedition(self):
        return {
            'name': 'Nouvelle Expédition',
            'type': 'ir.actions.act_window',
            'res_model': 'envoi.colis.expedition',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_conteneur_id': self.id},
        }
    
    def action_statut_prepare(self):
        self.ensure_one()
        if self.state == 'default':
            self.write({'state': 'prepare'})
        else:
            raise UserError("le conteneur doit etre exister...")


    def action_statut_expedie(self):
        self.ensure_one()
        if self.conteneur_id and self.state == 'prepare' and self.total_expeditions >=1 and self.total_colis >=1 :
            self.write({'state': 'expedie'})
            self._send_status_email()
        else:
            raise UserError("un conteneur doit etre prepare et doit avoir au moins une expedition avant d'etre expedie, qui doit avoir au moins un colis")
           


    def action_statut_en_transit(self):
        self.ensure_one()
        if self.state == 'expedie':  
            #expedition_status_list = [exp.state for exp in self.expedition_ids]  
            #if 'pending' not in expedition_status_list:
            #if 1==1:            
            self.write({'state': 'transit'})
            self._send_status_email()
            #raise UserError("Les factures doivent etre reglees en totalite")
        raise UserError("un conteneur doit etre expedie, pour etre en transit")
          
            
    def action_statut_arrive(self):
        self.ensure_one()
        if self.state == 'transit':
            #current_date = datetime.now()
            #to_string_date = current_date.strftime("%y%m%d%H%M")
            #if self.date_arrivee >= to_string_date:
            self.write({'state': 'arrive'})
            self._send_status_email()
        else:
            raise UserError("un conteneur doit etre en transit, avant d'arriver a destination")


    def _send_status_email(self):   
        self.ensure_one() # S'assure qu'il n'y a qu'un seul enregistrement
        #if self.client_id and self.client_id.email:
        for record in self:
            template = self.env.ref('envoi_colis.email_conteneur_template')
            if template:
                template.send_mail(record.id, force_send=True)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': "Email de notification envoyé au client.",
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError("Le template d'email de notification de statut n'a pas été trouvé.")
        #else:
        #   raise UserError("Aucun client ou adresse email client trouvée pour envoyer la notification.")
            

    
