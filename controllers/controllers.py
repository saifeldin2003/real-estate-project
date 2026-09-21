# -*- coding: utf-8 -*-
# from odoo import http


# class Real-estate-project(http.Controller):
#     @http.route('/real-estate-project/real-estate-project', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/real-estate-project/real-estate-project/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('real-estate-project.listing', {
#             'root': '/real-estate-project/real-estate-project',
#             'objects': http.request.env['real-estate-project.real-estate-project'].search([]),
#         })

#     @http.route('/real-estate-project/real-estate-project/objects/<model("real-estate-project.real-estate-project"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('real-estate-project.object', {
#             'object': obj
#         })

