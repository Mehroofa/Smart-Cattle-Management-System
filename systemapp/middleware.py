class NoCacheMiddleware:
    """
    Middleware that adds no-cache headers to all responses for authenticated users.
    This prevents the browser from caching pages so that after logout,
    pressing the back button will not show protected pages from the cache.
    Instead, the browser will make a fresh request, which Django's @login_required
    decorator will intercept and redirect to the login page.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

        return response
