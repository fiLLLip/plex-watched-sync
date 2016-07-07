# user.py

import account
import server
import requests
import falcon
import json
from xml.etree import ElementTree


def plex_get_request(url, token, data=None):
    r = requests.get(url, data=json.dumps(data), headers={'X-Plex-Token': token})
    if r.status_code == 404:
        return None
    return r


class ResourceUser(object):
    def on_get(self, req, resp, account_id):
        """Checks whether the user exists or not"""
        if account.Actions.get_account_exists(account_id):
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_404


class ResourceLogin(object):
    def on_post(self, req, resp):
        """Check with plex web api the user id and server to have access"""
        if 'X-TOKEN' not in req.headers:
            raise falcon.HTTPForbidden('Permission Denied', 'Missing header X-token')

        token = req.headers['X-TOKEN']
        result = plex_get_request('https://plex.tv/users/account.json', token)

        if result.status_code == 401 or result.status_code == 422:
            raise falcon.HTTPForbidden('Permission Denied', 'Provided token is not valid')

        account_id = result.json()['user']['id']
        result = plex_get_request('https://plex.tv/pms/servers', token)
        media_container_element = ElementTree.fromstring(result.content)
        servers = set()
        for server_element in media_container_element:
            servers.add(server_element.attrib['machineIdentifier'])

        for server_id in servers:
            server.Actions.add_account(server_id, account_id)
            account.Actions.add_server(account_id, server_id)
