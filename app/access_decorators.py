from django.shortcuts import redirect



def authenticated_user(Wrapped):
    def wrapper(request, *args, **kwargs):
        
        print(f'User :: {request.user}')
        if request.user.is_authenticated:
            return Wrapped(request, *args, **kwargs)
        else:
            return redirect('/')

    return wrapper



def guest_user(Wrapped):
    def wrapper(request, *args, **kwargs):
        
        print(f'User :: {request.user}')
        if not request.user.is_authenticated:
            return Wrapped(request, *args, **kwargs)
        else:
            return redirect('/')

    return wrapper




