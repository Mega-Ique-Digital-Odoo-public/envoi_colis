from random import random
from datetime import datetime
from odoo import models, fields, api


class Colis(models.Model):
    _name = 'envoi.colis.colis'
    _description = 'Colis dans une expédition'
    _order = 'sequence'

    @api.model
    def _generate_colis_id(self):
        now = datetime.now()
        return now.strftime("%y%m%d%H%M")

    sequence = fields.Integer(string='Séquence', default=1)
    name = fields.Char(string='Colis', compute='_compute_name', readonly=True, store=True)
    colis_id = fields.Char(string='Colis_Id', default=_generate_colis_id, readonly=True )
    expediteur = fields.Char(string='Expediteur', compute='_compute_expeditor', store=True, readonly=False)
    destinataire = fields.Char(string='Destinataire', default='')
    contenu = fields.Text(string='Contenu')
    poids = fields.Float(string='Poids')
    volume = fields.Float(string='Volume')
    statut = fields.Char(string='Statut', default='Enregistre')
    date_enregistrement = fields.Date(string="Date Enregistrement", default=fields.Date.today(), readonly=True)
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id)
    cout = fields.Monetary(string='Coût', currency_field='currency_id', required=True)
    expedition_id = fields.Many2one('envoi.colis.expedition', string='Expédition', required=True,
                                    default = lambda self: self._default_expedition_id())
    photo = fields.Image(string='Image', max_width=50, max_height=50, verify_resolution=True, help='telecharger images du colis')

    @api.depends('expedition_id')
    def _compute_expeditor(self):
        for record in self:
            if record.expedition_id:
                record.expediteur = ''
            else:
                record.expediteur = ''



    @api.depends('sequence')
    def _compute_name(self):
        for record in self:
            record.name = f'colis {record.sequence}'

    def _default_expedition_id(self):
        return self.env.context.get('active_id')

    @api.model
    def create(self, vals):
        if 'sequence' not in vals:
            expedition_id = vals.get('expedition_id', self._default_expedition_id())
            if expedition_id:
                last_colis = self.search([('expedition_id', '=', expedition_id)], order='sequence desc', limit=1)
                vals['sequence'] = last_colis.sequence + 1 if last_colis else 1
        return super(Colis, self).create(vals)

    def save(self):
        """
        Méthode appelée par le bouton Enregistrer.
        """
        return True