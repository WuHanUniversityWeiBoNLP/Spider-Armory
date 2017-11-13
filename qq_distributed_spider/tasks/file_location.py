#! python2
# -*- coding: utf-8 -*-
import os


base_path = os.path.abspath(os.path.dirname(__file__))

init_path = os.path.join(base_path, 'init')

unpack_json_path = os.path.join(base_path, 'unpack_json')

res_path = os.path.join(base_path, 'res')

__all__ = [base_path, init_path, unpack_json_path, res_path]
