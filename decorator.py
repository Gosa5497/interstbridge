from django.http import HttpResponse
def allow_user(allow_role=[]):
    def decorator(view_func):
        def wrapper_func(request,*arg,**kwargs):
            group=None
            group=request.user.groups.all()[0].name
            if group in allow_role:
                return view_func(request,*arg,**kwargs)
            else:
                return HttpResponse(f'{request.user}user does not have access to this page')
            return wrapper_func
        return decorator