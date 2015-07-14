from openerp.osv import osv, fields
from openerp.tools.translate import _

class account_tax_code(osv.Model):
    _name = "account.tax.code"
    _inherit = "account.tax.code"
    _columns = {
        'ventil_code': fields.selection([('1','0%'),
                                         ('2','6%'),
                                         ('3','12%'),
                                         ('4','21%'),
                                         ('11','Btw'),
                                         ('21','Medecontractant'),
                                         ('22','Diversen buiten btw'),
                                         ('23','Korting contant'),
                                         ('24','Marge'),
                                         ('44','0% (artikel 44)'),
                                         ('51','ICL goederen'),
                                         ('52','ICL maakloon'),
                                         ('53','ICL montage'),
                                         ('54','ICL afstand'),
                                         ('55','ICL diensten'),
                                         ('56','ICL driehoek a-B-c'),
                                         ('57','ICL diensten B2B'),
                                         ('70','Export niet-EU'),
                                         ('71','Onrechtstreekse uitvoer'),
                                         ('101','Busreizen'),
                                         ('102','Export via EU'),
                                         ('103','Standaardruil')],'Ventilation Code')
    }
