#! python3
# -*- coding: utf-8 -*-
import os
import json
import requests
import subprocess
from random import choice


class Proxy(object):
    @staticmethod
    def trigger_proxy():
        base_path = os.path.abspath(os.path.dirname(__file__))
        subprocess.Popen(['py', '-3', 'run.py'], cwd='%s' % base_path)

    @staticmethod
    def get_proxy():
        five_fastest_proxy = requests.get(
            'http://127.0.0.1:5000/proxy?count=5&anonymity=anonymous&protocol=https').content
        five_fastest_proxy_list = json.loads(five_fastest_proxy)
        sample = choice(five_fastest_proxy_list)
        proxy_ip_address = 'https://' + sample[0] + ':' + sample[1]
        proxy = {"https": "{}".format(proxy_ip_address)}
        return proxy


__all__ = [Proxy]