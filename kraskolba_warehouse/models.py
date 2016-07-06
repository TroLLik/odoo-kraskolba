# coding=utf-8 #
from openerp import models, api, fields


class depot(models.Model):
    _name = 'kraskolba.warehouse.depot'
    serialnumber = fields.Char(string=u'Сер. №', required=False, size=100)
    name = fields.Char(string=u'Название', required=True, index=True, size=100)
    address = fields.Char(string=u'Адрес', required=True, index=True, size=100)

    goods = fields.Many2one(string=u'Товар', comodel_name='kraskolba.warehouse.goods')
    
class goods(models.Model)
    _name = 'kraskolba.warehouse.goods'
    name = fields.Char(string=u'Название', required=True, index=True, size=100)
    type = fields.Selection([
        ('type1', "Тип1"),
        ('type2', "Тип2"),
        ('type3', "Тип3"),
    ], default='type1', string=u'Тип склада')
    status = fields.Selection([
        ('status1', "Статус1"),
        ('status2', "Статус2"),
        ('status3', "Статус3"),
    ], default='status1', string=u'Статус склада')
    price = fields.Float(default=0, string=u'Цена')
    quantity = fields.Integer(default=0, string=u'Кол-во')

    depot = fields.One2many(comodel_name='kraskolba.warehouse.depot', inverse_name='goods',
                                   ondelete='restrict')

class Document(models.Model):
    _name = 'kraskolba.warehouse.doc'
    #в этой модели предпологается вести документы производящие движение товара

class Employee(models.Model):
    _name = 'kraskolba.warehouse.employee'
    _rec_name = 'full_name'
    last_name = fields.Char(string=u'Фамилия', required=True, index=True, size=200)
    first_name = fields.Char(string=u'Имя', required=True, size=100)
    middle_name = fields.Char(string=u'Отчество', required=True, size=100)
    full_name = fields.Char(string=u'ФИО', compute="_full_name", search='_search_full_name')
    position = fields.Selection(selection=[
        ('seller', u'Продавец'),
        ('manager', u'Менеджер'),
        ('admin', u'Администратор'),
    ], default='seller',  required=True, string=u'Должность')

#    create_order = fields.One2many(comodel_name='kraskolba.warehouse.order', inverse_name='create_maker', ondelete='restrict')

#    order_executive_engineer = fields.One2many(string=u'Заказы', comodel_name='kraskolba.warehouse.order', inverse_name='executive_engineer', ondelete='restrict')


    @api.one
    @api.depends('last_name', 'first_name', 'middle_name')
    def _full_name(self):
        self.full_name = u'%s %s %s' % (self.last_name, self.first_name, self.middle_name)

    def _search_full_name(self, operator, value):
        if operator == 'like':
            operator = 'ilike'

        return ['|', '|',
                ('last_name', operator, value),
                ('first_name', operator, value),
                ('middle_name', operator, value),
                ]

class User(models.Model):
    _inherit = 'res.users'

#    _sql_constraints = [
#        ('kraskolba.warehouse.employee', 'unique(employee_id)', u"Уникальный сотрудник"),
#    ]
    employee_id = fields.Many2one(string=u'Сотрудник', comodel_name='kraskolba.warehouse.employee', ondelete='set null', required=False, groups="gcap_fix.group_gcap_fix_superuser")