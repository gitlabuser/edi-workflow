from openerp import models, fields, api, _

class res_partner(models.Model):
    _inherit = "res.partner"
    
    expertm_reference = fields.Char(size=64)
