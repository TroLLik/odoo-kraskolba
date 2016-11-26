# -*- coding: utf-8 -*-
# noinspection PyStatementEffect
{
    'name': "Kraskolba Base",
    'summary': """Базовые записи Kraskolba""",

    'description': """
        В модуле хранятся общие записи и настройки для Kraskolba
    """,

    'author': "TroLL",
    'website': "http://www.kraskolba.ru",
    'license ': 'Proprietary',

    'application': False,

    'category': "Base",
    'version': '0.1',

    'sequence': 1,

    'auto_install': False,

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'data.xml',
    ],
}