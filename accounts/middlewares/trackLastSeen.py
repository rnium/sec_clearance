class TrackLS:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if hasattr(request.user, 'adminaccount'):
            request.user.adminaccount.lastseen_now()
        return self.get_response(request)