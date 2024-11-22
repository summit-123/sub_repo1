from django.utils.deprecation import MiddlewareMixin
import json

class ContextualDataMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if 'application/json' in response['Content-Type']:
            data = json.loads(response.content)
            contextual_data = {
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                } if request.user.is_authenticated else None,
                # Add more contextual data as needed
            }
            data['_context'] = contextual_data
            response.content = json.dumps(data)
        return response