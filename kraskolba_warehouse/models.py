# coding=utf-8 #
from odoo import models, api, fields, exceptions, tools

from odoo.tools.translate import _
from odoo.osv.expression import FALSE_DOMAIN, TRUE_DOMAIN

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


# class Document(models.Model):
#     _name = 'kraskolba.warehouse.doc'
# в этой модели предпологается вести документы производящие движение товара


class Price(models.Model):
    _name = 'kraskolba.warehouse.price'

    name = fields.Char(string=u'Название', size=100, required=True)
    value = fields.Float(string=u'Цена', default=0, required=True)
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


class GoodsCategory(models.Model):
    _name = 'kraskolba.warehouse.goodscategory'
    _parent_store = True
    _rec_name = 'complete_name'
    _parent_order = 'name'
    _order = 'parent_left'

    _sql_constraints = [
        ('goodscategory_name_and_parent_idx', 'unique(name, parent_id)', u"Уникальный объект"),
    ]

    parent_id = fields.Many2one(string=u'Родительская категория', comodel_name='kraskolba.warehouse.goodscategory',
                                ondelete='restrict')
    parent_left = fields.Integer(_('Left Parent'), index=True)
    parent_right = fields.Integer(_('Right Parent'), index=True)
    subcategory_ids = fields.One2many(string=u'Подкатегория', comodel_name='kraskolba.warehouse.goodscategory',
                                      inverse_name='parent_id')

    complete_name = fields.Char(string=u'Полное название', compute='_get_complete_name', search='_get_search_name')

    name = fields.Char(string=u'Название', required=True, index=True, size=40)
    code = fields.Char(string=u'Код', required=False, size=50)

    nomenclature_idx = fields.One2many(string=u'Номенклатура', comodel_name='kraskolba.warehouse.nomenclature',
                                       compute='_get_nomenclature')

    @api.one
    def _get_nomenclature(self):
        nomenclature_ids = self.env['kraskolba.warehouse.nomenclature'].search([('category', '=', self.id)])
        if nomenclature_ids:
            self.nomenclature_idx = nomenclature_ids
        else:
            self.nomenclature_idx = None

    @api.one
    @api.depends('name', 'parent_id.name')
    def _get_complete_name(self):
        parents = self.env[self._name].search([
            ('parent_left', '<=', self.parent_left),
            ('parent_right', '>=', self.parent_right),
        ])

        self.complete_name = u' / '.join(x.name for x in parents)

    def _get_search_name(self, operator, value):
        if operator == 'ilike':
            p_ids = self.search([('name', operator, value)])
            return [('id', 'child_of', p_ids.ids)]
        elif operator == 'not ilike':
            p_ids = self.search([('name', 'ilike', value)])
            matched_ids = self.search([('id', 'child_of', p_ids.ids)])
            return [('id', 'not in', matched_ids.ids)]
        elif operator == '=' and value is False:
            return FALSE_DOMAIN
        elif operator == '=' and value is True:
            return TRUE_DOMAIN
        elif operator == '!=' and value is False:
            return TRUE_DOMAIN
        elif operator == '!=' and value is True:
            return FALSE_DOMAIN
        elif operator in ['=', '!=']:
            parts = value.split(u' / ')
            ids = False

            while parts:
                part = parts.pop(0)

                parent_domain = [('parent_id', '=', False)] if ids is False else [('parent_id', 'in', ids)]

                ids = self.search([('name', '=', part)] + parent_domain).ids

            ids = ids or []

            if operator == '=':
                return [('id', 'in', ids)]
            else:
                return [('id', 'not in', ids)]

        raise ValueError('Invalid operator %s' % operator)


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
    image = fields.Binary(string=u'Изображение', )
    image_medium = fields.Binary(compute='_compute_image_medium', inverse='_inverse_image_medium', store=True)
    tax = fields.Integer(string=u'Налог (%)', default=0)
    discount = fields.Integer(string=u'Скидка (%)', default=0)
    description = fields.Text(string=u'Описание')
    comment = fields.Char(string=u'Комментарий', size=300)
    supplier = fields.Many2one(string=u'Поставщик', comodel_name='kraskolba.warehouse.supplier')
    manufacturer = fields.Many2one(string=u'Производитель', comodel_name='kraskolba.warehouse.manufacturer')
    category = fields.Many2one(string=u'Категория', comodel_name='kraskolba.warehouse.goodscategory', required=True)

    @api.multi
    @api.depends('image')
    def _compute_image_medium(self):
        self.image_medium = tools.image_resize_image_medium(self.image)

    @api.one
    @api.depends('image_medium')
    def _inverse_image_medium(self):
        self.image = tools.image_resize_image_big(self.image_medium)


class DocumentGoods(models.Model):
    _name = 'kraskolba.warehouse.document.goods'

    nomenclature = fields.Many2one(string=u'Товар', comodel_name='kraskolba.warehouse.nomenclature', required=True)
    quantity = fields.Integer(default=1, string=u'Количество', required=True)
    document_id = fields.Many2one(string=u'Документ', comodel_name='kraskolba.warehouse.document')

    @api.one
    @api.constrains('quantity')
    def _check_quantity(self):
        if self.quantity < 1:
            raise exceptions.ValidationError(u"Количество не может быть меньше единицы.")


class Document(models.Model):
    _name = 'kraskolba.warehouse.document'
    _rec_name = 'name'

    name = fields.Char(string=u'Название документа', size=100)
    goods = fields.One2many(string=u'Товары', comodel_name='kraskolba.warehouse.document.goods',
                            inverse_name='document_id', ondelete='cascade')
    goods_count = fields.Integer(string=u'Количество товаров', compute='get_goods_count')

    @api.one
    def get_goods_count(self):
        return len(self.goods) or 0


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
