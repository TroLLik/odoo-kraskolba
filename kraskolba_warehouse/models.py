# coding=utf-8 #
from openerp import models, api, fields, exceptions

STATES = [
    ('status1', "Статус1"),
    ('status2', "Статус2"),
    ('status3', "Статус3"),
]

UNITS = [
    ('units', u"шт"),
    ('meters', u"метров"),
    ('kilo', u"кг"),
]


class Depot(models.Model):
    _name = 'kraskolba.warehouse.depot'
    _rec_name = 'name'

    name = fields.Char(string=u'Название', required=True, index=True, size=100)
    location = fields.Char(string=u'Расположение', required=False, size=255)
    description = fields.Text(string=u'Описание')
    is_returning = fields.Boolean(string=u'Возвратный склад')


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


class Price(models.Model):
    _name = 'kraskolba.warehouse.price'

    name = fields.Char(string=u'Название', size=100)
    value = fields.Float(string=u'Цена', default=0)
    nomenclature_id = fields.Many2one(string=u'Номенклатура', comodel_name='kraskolba.warehouse.nomenclature')

    @api.one
    @api.constrains('value')
    def _check_price(self):
        if self.value < 0:
            raise exceptions.ValidationError(u"Цена не может быть меньше нуля.")


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


class Nomenclature(models.Model):
    _name = 'kraskolba.warehouse.nomenclature'
    _rec_name = 'name'

    _sql_constraints = [
        ('article_idx', 'UNIQUE(article)', u'Такой артикул уже существует'),
        ('code_idx', 'UNIQUE(code)', u'Такой код уже существует'),
    ]

    name = fields.Char(string=u'Наименование', required=True, index=True, size=200)
    article = fields.Integer(string=u'Артикул')
    code = fields.Integer(string=u'Код')
    unit = fields.Selection(string=u'Ед.измерения', selection=UNITS, default=UNITS[0][0], required=True)
    price = fields.One2many(string=u'Цены', comodel_name='kraskolba.warehouse.price', inverse_name='nomenclature_id')
    quantity = fields.Integer(default=1, string=u'Количество')
    image = fields.Binary(string=u'Изображение', )
    tax = fields.Integer(string=u'Налог (%)', default=0)
    discount = fields.Integer(string=u'Скидка (%)', default=0)
    description = fields.Text(string=u'Описание')
    comment = fields.Char(string=u'Комментарий', size=300)
    supplier = fields.Many2one(string=u'Поставщик', comodel_name='kraskolba.warehouse.supplier')
    manufacturer = fields.Many2one(string=u'Производитель', comodel_name='kraskolba.warehouse.manufacturer')

    #    category = fields.Many2one(string=u'Поставщик', comodel_name='kraskolba.warehouse.supplier')

    @api.one
    @api.constrains('quantity')
    def _check_quantity(self):
        if self.quantity < 1:
            raise exceptions.ValidationError(u"Количество не может быть меньше единицы.")


class Supplier(models.Model):
    _name = 'kraskolba.warehouse.supplier'
    _rec_name = 'full_name'

    name = fields.Char(string=u'ФИО', size=255)
    organization = fields.Char(string=u'Организация', size=255)
    full_name = fields.Char(string=u'Организация+ФИО', size=510, compute='get_full_name')

    def get_full_name(self):
        self.full_name = u'{0} ({1})'.format(self.organization, self.name)


class Manufacturer(models.Model):
    _name = 'kraskolba.warehouse.manufacturer'
    _rec_name = 'full_name'

    name = fields.Char(string=u'ФИО', size=255)
    organization = fields.Char(string=u'Организация', size=255)
    full_name = fields.Char(string=u'Организация+ФИО', size=510, compute='get_full_name')

    def get_full_name(self):
        self.full_name = u'{0} ({1})'.format(self.organization, self.name)
