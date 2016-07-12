# coding=utf-8 #
from openerp import models, api, fields

STATES = [
    ('status1', "Статус1"),
    ('status2', "Статус2"),
    ('status3', "Статус3"),
]


class Depot(models.Model):
    _name = 'kraskolba.warehouse.depot'
    _rec_name = 'name'

    name = fields.Char(string=u'Название', required=True, index=True, size=100)
    serial_number = fields.Char(string=u'Сер. №', required=False, size=100)
    address = fields.Char(string=u'Адрес', required=True, index=True, size=100)
    goods = fields.One2many(string=u'Товары', comodel_name='kraskolba.warehouse.goods', compute='_get_goods')

    @api.one
    def _get_goods(self):
        goods_ids = self.env['kraskolba.warehouse.goods'].search([('depot', '=', self.id)])
        if goods_ids:
            self.goods = goods_ids
        else:
            self.goods = None


class GoodType(models.Model):
    _name = 'kraskolba.warehouse.goodtype'
    _rec_name = 'name'

    name = fields.Char(string=u'Название', required=True, size=100)
    goods = fields.One2many(string=u'Товары', comodel_name='kraskolba.warehouse.goods', compute='_get_goods')
    count = fields.Integer(string=u'Количество', compute='_count_goods')

    @api.one
    def _get_goods(self):
        goods_ids = self.env['kraskolba.warehouse.goods'].search([('type', '=', self.id)])
        if goods_ids:
            self.goods = goods_ids
        else:
            self.goods = None

    @api.one
    def _count_goods(self):
        self.count = len(self.goods)
        # Подсчет количества единиц товаров
        # self.count = sum(x.count for x in self.goods)


class Goods(models.Model):
    _name = 'kraskolba.warehouse.goods'
    _rec_name = 'name'
    _constraints = [
        (_check_quantity, u'Неверное значение', ['quantity']),
        (_check_price, u'Неверное значение', ['price'])
    ]

    name = fields.Char(string=u'Название', required=True, index=True, size=100)
    type = fields.Many2one(string=u'Категория', comodel_name='kraskolba.warehouse.goodtype')
    state = fields.Selection(STATES, default='status1', string=u'Статус товара')
    price = fields.Float(default=0, string=u'Цена')
    quantity = fields.Integer(default=1, string=u'Кол-во')
    depot = fields.Many2one(string=u'Склад', comodel_name='kraskolba.warehouse.depot',
                            ondelete='restrict')
    note = fields.Text(string=u'Примечание')

    # Запрещаем вводить отрицательные числа в количество товара
    @api.one
    @api.constrains('quantity')    
    def _check_quantity(self):
        if self.quantity < 0:
            raise exceptions.ValidationError("Неверное значение.")


    # Запрещаем вводить отрицательные числа в стоимость товара
    @api.one
    @api.constrains('price')    
    def _check_price(self):
        if self.price < 0:
            raise exceptions.ValidationError("Неверное значение.")


# class Document(models.Model):
#     _name = 'kraskolba.warehouse.doc'
# в этой модели предпологается вести документы производящие движение товара


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
    ], default='seller', required=True, string=u'Должность')

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
    employee_id = fields.Many2one(string=u'Сотрудник', comodel_name='kraskolba.warehouse.employee', ondelete='set null',
                                  required=False, groups="gcap_fix.group_gcap_fix_superuser")
