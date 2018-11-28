"""electives URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import logout
from django.views.generic import RedirectView

from schema.views import login, list_relations, table_data, edit_record,create_record, delete_record, sql_query
from schema.sql_views import *

urlpatterns = [
	path('', RedirectView.as_view(pattern_name='login', permanent=False)),
	path('login/', login, name='login'),
    path('logout/', logout, {'next_page': 'login'}, name='logout'),

	path('relations/', list_relations, name='relations'),
	path('relations/<slug:modelName>/new/', create_record),
	path('relations/<slug:modelName>/<int:recordNum>/delete/', delete_record),
	path('relations/<slug:modelName>/<int:recordNum>/', edit_record),
	path('relations/<slug:modelName>/', table_data),
	#path('<slug:model>', crud_records),
    path('sql/', sql_query),
    path('sql_views/', sql_view),
    path('sql_views/<slug:viewName>/', sql_view)
]
