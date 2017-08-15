# -*- coding: utf-8 -*-

import random

from argparse import ArgumentParser
from mitmproxy import ctx
from os import path

from mitm_scripts.alteration import Alteration, NoOpAlteration


class Meddler:
    '''Makes random changes to HTTP responses
    '''

    def __init__(self, alterations):
        self.alterations = alterations

    def response(self, flow):
        '''Function required by mitmproxy to handle a flow.
        '''

        alteration = select_alteration(flow, self.alterations)
        ctx.log.info("Alteration '{}' selected".format(alteration.NAME))
        alteration.response(flow)
        flow.response.headers['X-Tuf-Mitm'] = 'true'


def start():
    '''Function required by mitmproxy to start handling flows.
    '''

    parser = ArgumentParser(path.basename(__file__), description='scripts for mitmproxy')
    parser.add_argument('--alteration', '-a', help='The names of alterations to use (default uses all)',
                        choices=list(sorted(map(lambda x: x.NAME, available_alterations))),
                        default=available_alterations,
                        action='append')
    args = parser.parse_args()

    return Meddler(args.alteration)


def all_subclasses(cls):
    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in all_subclasses(s)]

available_alterations = all_subclasses(Alteration)


def select_alteration(resp, choices=None):
    '''Randomly select one alteration to apply to the HTTP response'''

    alterations = list(filter(lambda x: x.NAME in choices if choices else True \
                              and x.check(flow),
                       available_alterations))

    if not alterations:
        alterations = [NoOpAlteration]

    return random.choice(alterations)
