# -*- coding: utf-8 -*-

import canonicaljson
import json
import random

from mitmproxy import ctx
from os import path

from mitm_scripts.alteration import TargetFlipBit


class Meddler:

    def __init__(self):
        self.repo_targets = set()
        self.director_targets = set()

    def response(self, flow):
        '''Function request by mitmproxy to handle a flow.
        '''

        self._extract_targets(flow)

        if self._is_target(flow):
            TargetFlipBit.response(flow)

        flow.response.headers['X-Tuf-Mitm'] = 'true'

    def _is_target(self, flow):
        if flow.request.path_components:
            if flow.request.path.startsith('/director/'):
                return flow.request.path[len('/director/'):] in self.director_targets
            elif flow.request.path.startsith('/repo/'):
                return flow.request.path[len('/repo/'):] in self.repo_targets
        return False

    def _extract_targets(self, flow):
        if flow.request.path_components:
            if flow.request.path_components[0] == 'director':
                is_director = True
            elif flow.request.path_components[0] == 'repo':
                is_director = False
            else:
                return
        else:
            return

        try:
            text = flow.response.text
        except ValueError:
            return

        try:
            meta = json.loads(text)
        except json.decoder.JSONDecodeError:
            return

        try:
            targets = set(meta['signed']['targets'].keys())
        except TypeError:
            return
        except AttributeError:
            return

        if is_director:
            self.director_targets = targets
        else:
            self.repo_targets = targets


def start():
    '''Function required by mitmproxy to start handling flows.
    '''
    return Meddler()
