from openerp.exceptions import except_orm

class EdiIgnorePartnerError(except_orm):
    def __init__(self, msg):
        super(EdiIgnorePartnerError, self).__init__('EdiIgnorePartnerError', msg)

class EdiValidationError(except_orm):
    def __init__(self, msg):
        super(EdiValidationError, self).__init__('EdiValidationError', msg)
