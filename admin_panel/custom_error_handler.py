from django.shortcuts import render

def error_404(request, *args, **argv):
    data = {}
    return render(request,'adminpanel/404.html', data)

def error_500(request):
    data = {}
    return render(request,'adminpanel/500.html', data)

def error_403(request, exception):
    data = {}    
    return render(request,'adminpanel/404.html', data)



