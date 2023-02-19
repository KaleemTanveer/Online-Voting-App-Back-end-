"""onlinevotingsystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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

from django.urls import path,include
from rest_framework import routers
from .views import all_views



urlpatterns = [
    path('electionlist', all_views.ElectionList),
    path('registration', all_views.Registration),
    path('login', all_views.Login),
    path('logout', all_views.Logout),
    path('forget-password',all_views.forgetPassword),
    path('electioncandidate/<int:election_id>/',all_views.electionCandidatesList),
    path('election-results/<int:election_id>/',all_views.electionResultsList),
    path('mother-mcq-list', all_views.MotherMCQList),
    path('cast-vote', all_views.CastVote),
    path('verify-session', all_views.VerifySession),
]