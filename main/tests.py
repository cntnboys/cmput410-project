import calendar
from datetime import timedelta
import random

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Count
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.template import RequestContext, loader
from django.core.context_processors import csrf

import uuid


from django.test import TestCase

from main.models import Authors, Friends, Posts, Comments

# Create your tests here.

class AuthorMethodTests(TestCase):

    def test_create_author(self):
        name = "Ana Marcu"
        username = "anamarcu"
        email = "marcu@ualberta.ca"
        location = "local"
        
        author1 = Authors.objects.get_or_create(name=name, username=username,location=location, email=email, image="", github="", twitter="", facebook="")[0]
        
        #author2 = Authors.
    
        self.assertEqual(Authors.objects.filter(username="anamarcu")[0], author1)

# insert check insert check update check delete check delete check - a few restriction tests in between  -- for all tables