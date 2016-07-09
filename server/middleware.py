class Crossdomain(object):
    def process_response(self, req, resp, resource):
        resp.set_header("Access-Control-Allow-Origin", "*")
        resp.set_header("Access-Control-Allow-Credentials", "true")
        resp.set_header("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS,POST,PUT")
        resp.set_header("Access-Control-Allow-Headers", "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers, X-token")