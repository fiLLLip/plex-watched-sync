# serve.py

import falcon
import account
import server
import redis_plex
import user

# Falcon follows the REST architectural style, meaning (among
# other things) that you think in terms of resources and state
# transitions, which map to HTTP verbs.


# Init Redis
redis_instance = redis_plex.connection()


def crossdomain(req, resp):
    resp.set_header('Access-Control-Allow-Origin', '*')


# falcon.API instances are callable WSGI apps
api = falcon.API(middleware=[crossdomain])

# things will handle all requests to the '/things' URL path
app.add_route('/account/{account_id}', account.Resource())
app.add_route('/server/{server_id}', server.Resource())
app.add_route('/user/login', user.ResourceLogin())
app.add_route('/user/{account_id}', user.ResourceUser())
