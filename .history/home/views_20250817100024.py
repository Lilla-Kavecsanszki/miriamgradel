from django.http import HttpResponse

def trigger_error(request):
    # force an error
    1 / 0  
    return HttpResponse("This will never be seen")
