from django.shortcuts import redirect

def onlyxhr(view):

    def __onlyxhr(request, *args, **kwargs):
        """ :type request  HttpResponse"""
        if request.is_ajax():
            return view(request, *args, **kwargs)
        return redirect("/")  # redirect to index

    return __onlyxhr

