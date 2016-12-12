# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models


class NomenclatureReport(models.Model):
    _name = "nomenclature.report"
    _description = "Nomenclature Report"
    _auto = False

    name = fields.Char('Nomenclature Reference', readonly=True)