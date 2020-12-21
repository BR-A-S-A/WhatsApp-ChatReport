from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.files.storage import FileSystemStorage

import Statistcs.controller
import time


def upload(request):
    ts = time.time()
    context = {}
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        name = fs.save(str(ts) + "_" + uploaded_file.name, uploaded_file)
        context['url'] = fs.url(name)
    return render(request, 'upload.html', context)

def index(request, file_name):
    controller = Statistcs.controller.StatistcsController(file_name)
    return JsonResponse(controller.get_all())

def get_user(request, file_name):
    controller = Statistcs.controller.StatistcsController(file_name)
    return JsonResponse(controller.get_user())

def get_emoji_dist(request, file_name):
    controller = Statistcs.controller.StatistcsController(file_name)
    return FileResponse(open(controller.emojiDistCall(), 'rb'))

def get_wordcloud(request, file_name):
    controller = Statistcs.controller.StatistcsController(file_name)
    return FileResponse(open(controller.wordcloudTextCall(), 'rb'))

def get_day_of_week(request, file_name):
    format = request.GET.get('format')
    controller = Statistcs.controller.StatistcsController(file_name)
    if (format == 'json'):
        return HttpResponse(controller.get_day_of_week(format))
    return FileResponse(open(controller.get_day_of_week(), 'rb'))

def get_emoji_dist_by_user(request, file_name):
    controller = Statistcs.controller.StatistcsController(file_name)
    name = request.GET.get('name')
    format = request.GET.get('format')
    if format == 'json':
        return controller.get_emoji_by_user(name, format)
    return FileResponse(open(controller.get_emoji_by_user(name), 'rb'))

def get_dataframe_json(request, file_name):
    controller = Statistcs.controller.StatistcsController(file_name)
    response = controller.get_dataframe_json_format()
    return HttpResponse(response)