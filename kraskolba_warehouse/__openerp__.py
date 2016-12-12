# -*- coding: utf-8 -*-
# noinspection PyStatementEffect
{
    'name': "Kraskolba Warehouse",
    'summary': """Система управления складом kraskolba.ru""",

    'description': """
        Модуль для управления складом kraskolba
    """,

    'author': "gravicap software development",
    'website': "http://www.erp.kraskolba.ru",
    'license ': 'Proprietary',

    'application': True,

    'category': 'warehouse',
    'version': '0.1',

    'sequence': 22,

    'auto_install': False,

    # any module necessary for this one to work correctly
    'depends': ['base', 'report', 'web'],

    # always loaded
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',

        'view/kraskolba_warehouse_view.xml',
        'menu/kraskolba_warehouse_menu.xml',

        'reports/kraskolba_warehouse_report.xml',
        # 'reports/nomenclature_report.xml',
    ],

    # demo data
    'demo': [
        'data/demo.xml',
    ],
}