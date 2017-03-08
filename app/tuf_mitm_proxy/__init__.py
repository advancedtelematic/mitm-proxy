# -*- coding: utf-8 -*-

import canonicaljson
import requests

from argparse import ArgumentParser
from flask import Flask, request, Response, current_app
from tuf_mitm_proxy.alteration import select_alteration, available_alterations
from urllib.parse import urlparse, urlunparse


def main_route(proxy_domain, proxy_port, alterations):
    '''The singular route all traffic is piped through'''

    current_app.logger.info('Received request for url: {}'.format(request.url))

    url = list(urlparse(request.url))
    url[1] = '{}:{}'.format(proxy_domain, proxy_port)

    resp = requests.request(request.method, urlunparse(url), data=request.data)
    resp = alter_response(resp, alterations)
    return resp


def alter_response(resp, alterations):
    '''Applies an arbitary alteration to the HTTP response'''

    mod_resp = Response(resp.text, resp.status_code)

    for header, value in resp.headers.items():
        mod_resp.headers[header] = value

    alteration = select_alteration(resp, alterations)
    current_app.logger.info("Alteration '{}' selected".format(alteration.NAME))
    
    return alteration.apply(mod_resp)


def create_app(proxy_domain, proxy_port, alterations):
    '''Function that handles all initializations of the Flask application.'''

    app = Flask(__name__)
    app.debug = False  # sane default

    # using .strip() because of Makefile ugliness
    app.add_url_rule('/', 'main_route',
                     lambda: main_route(proxy_domain.strip(), proxy_port, alterations),
                     methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'CONNECT', 'OPTIONS', 'TRACE'])

    # using .strip() because of Makefile ugliness
    app.add_url_rule('/<path:path>', 'additional_route',
                     lambda path: main_route(proxy_domain.strip(), proxy_port, alterations),
                     methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'CONNECT', 'OPTIONS', 'TRACE'])

    app.logger.info('App initialized')
    return app


def arg_parser(cli_name):
    '''Creates a CLI parser for easy scripting.'''

    parser = ArgumentParser(cli_name, description='runs a MITM proxy')

    parser.add_argument('--proxy-domain', '-D', help='The domain to forward requests to', required=True)
    parser.add_argument('--proxy-port', '-P', help='The port to forward requests to', type=int, default=80)

    parser.add_argument('--bind-interface', '-i', help='The interface to bind this poxy to', default='127.0.0.1')
    parser.add_argument('--bind-port', '-p', help='The port to bind this proxy to', type=int, default=8080)

    parser.add_argument('--alteration', '-a', help='The alterations to use', action='append',
                        choices=sorted(map(lambda x: x.NAME, available_alterations)),
                        default=available_alterations)
    return parser
