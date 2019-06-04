class UserAgentMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        user_agent = request.headers['User-Agent']
        if user.is_authenticated and user.last_user_agent != user_agent:
            user.last_user_agent = user_agent
            user.save()

        return self.get_response(request)
