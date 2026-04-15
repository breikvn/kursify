class SimpleCorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'OPTIONS':
            response = self._build_preflight_response()
        else:
            response = self.get_response(request)
        self._add_cors_headers(response)
        return response

    def _build_preflight_response(self):
        from django.http import HttpResponse

        return HttpResponse(status=200)

    def _add_cors_headers(self, response):
        response['Access-Control-Allow-Origin'] = 'http://localhost:4200'
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
