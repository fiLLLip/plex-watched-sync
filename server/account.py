# account.py

import json
import falcon
import redis_plex
import server

_r = redis_plex.connection()


class Actions(object):
    @staticmethod
    def get_account_key(account_id):
        return 'account:' + str(account_id)

    @staticmethod
    def get_account_server_relation_key(account_id):
        return 'account:' + str(account_id) + ':servers'

    @staticmethod
    def validate_account_server_access(req, resp, resource, params):
        if 'X-SERVER-ID' not in req.headers:
            raise falcon.HTTPForbidden('Permission Denied', 'Missing header X-server-id')
        server_id = req.headers['X-SERVER-ID']
        account_id = params['account_id']
        servers = Actions.get_servers(account_id)
        try:
            b = servers.index(server_id)
        except ValueError:
            raise falcon.HTTPForbidden('Permission Denied',
                                       'Server ' + server_id + ' has no access to account id ' + account_id)

    @staticmethod
    def get_watched(account_id):
        items = _r.smembers(Actions.get_account_key(account_id))
        return list(items)

    @staticmethod
    def get_account_exists(account_id):
        return _r.exists(Actions.get_account_key(account_id)) == 1

    @staticmethod
    def add_watched_to_account(account_id, items):
        return _r.sadd(Actions.get_account_key(account_id), *items)

    @staticmethod
    def delete_account(account_id):
        return _r.delete(Actions.get_account_key(account_id))

    @staticmethod
    def delete_watched_by_account(account_id, items):
        return _r.srem(Actions.get_account_key(account_id), *items)

    @staticmethod
    def add_server(account_id, server_id):
        return _r.sadd(Actions.get_account_server_relation_key(account_id), server_id)

    @staticmethod
    def remove_server(account_id, server_id):
        return _r.srem(Actions.get_account_server_relation_key(account_id), server_id)

    @staticmethod
    def get_servers(account_id):
        items = _r.smembers(Actions.get_account_server_relation_key(account_id))
        return list(items)


class Resource(object):
    @falcon.before(Actions.validate_account_server_access)
    def on_get(self, req, resp, account_id):
        """Handles GET requests"""
        watched = Actions.get_watched(account_id)
        if watched is None:
            resp.status = falcon.HTTP_404
            return
        servers = Actions.get_servers(account_id)
        resp.status = falcon.HTTP_200  # This is the default status
        json_resp = {'account_id': account_id, 'watched': watched, 'servers': servers}
        resp.body = json.dumps(json_resp)

    @falcon.before(Actions.validate_account_server_access)
    def on_put(self, req, resp, account_id):
        """Handles PUT requests"""
        try:
            raw_json = req.stream.read()
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Error',
                                   ex.message)

        try:
            result_json = json.loads(raw_json, encoding='utf-8')
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect.')

        items = result_json['watched']
        result = Actions.add_watched_to_account(account_id, items)
        resp.status = falcon.HTTP_202
        jsonresp = {'account_id': account_id, 'tried_to_add': items, 'added': result}
        resp.body = json.dumps(jsonresp)

    @falcon.before(Actions.validate_account_server_access)
    def on_delete(self, req, resp, account_id):
        """
        Handles DELETE requests. Deletes the account from the database
        """
        raise falcon.HTTPMethodNotAllowed
        servers = Actions.get_servers(account_id)
        for server_id in servers:
            server.Actions.remove_account(server_id, account_id)
        result = server.Actions.delete_account(account_id)
        resp.status = falcon.HTTP_200
        if result == 1:
            result = 'success'
        else:
            result = 'failed'
        jsonresp = {'deleted': result}
        resp.body = json.dumps(jsonresp)
