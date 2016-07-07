# server.py
import falcon
import json
import redis_plex
import account

_r = redis_plex.connection()


class Actions(object):
    @staticmethod
    def get_key(server_id):
        return 'server:' + str(server_id)

    @staticmethod
    def add_account(server_id, account_id):
        return _r.sadd(Actions.get_key(server_id), account_id)

    @staticmethod
    def remove_account(server_id, account_id):
        return _r.srem(Actions.get_key(server_id), account_id)

    @staticmethod
    def remove_server(server_id):
        return _r.delete(Actions.get_key(server_id))

    @staticmethod
    def get_accounts(server_id):
        items = _r.smembers(Actions.get_key(server_id))
        return list(items)


class Resource(object):
    def on_get(self, req, resp, server_id):
        """Handles GET requests"""
        accounts = Actions.get_accounts(server_id)
        if accounts is None:
            resp.status = falcon.HTTP_404
            return
        json_response = {'server_id': server_id, 'accounts': accounts}
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = json.dumps(json_response)

    def on_put(self, req, resp, server_id):
        """Handles PUT requests"""
        resp.status = falcon.HTTP_404 # Disabled!
        return

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

        accounts = Actions.get_accounts(server_id)
        if accounts is None:
            resp.status = falcon.HTTP_404
            return

        accounts = result_json['accounts']
        for account_id in accounts:
            Actions.add_account(server_id, account_id)
            account.Actions.add_server(account_id, server_id)

        resp.status = falcon.HTTP_200  # This is the default status
        jsonresp = {'server_id': server_id, 'accounts': Actions.get_accounts(server_id)}
        resp.body = json.dumps(jsonresp)