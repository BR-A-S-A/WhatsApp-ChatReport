from django.urls import path
from . import views

urlpatterns = [
    path('index/<file_name>/', views.index, name='index'),
    path('users/<file_name>', views.get_user, name='get_user'),
    path('emojis/<file_name>', views.get_emoji_dist, name='get_emoji_dist'),
    path('word-cloud/<file_name>', views.get_wordcloud, name='get_wordcloud'),
    path('days/<file_name>', views.get_day_of_week, name='get_day_of_week'),
    path('emojis/user/<file_name>', views.get_emoji_dist_by_user, name='get_emoji_dist_by_user'),
    path('upload/', views.upload, name='upload'),
    path('dataframe/<file_name>', views.get_dataframe_json, name='get_dataframe_json')
]
