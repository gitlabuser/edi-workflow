from openerp import models, fields, api, _


class stock_picking(models.Model):
  _inherit = 'stock.picking'

  desadv_name = fields.Char(size=64)