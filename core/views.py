from core.models import User,team,addict_user
 
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
import json

import redis

# Create your views here.
@login_required(login_url='/login/')
def home(request):
    Usermodel=get_user_model()
    pt=team.objects.get(is_now=1)
    other=team.objects.exclude(is_now=1)
    
    user=get_object_or_404(Usermodel,username=request.user.username)
    return render(request, 'new.html' ,locals())

@login_required(login_url='/login/')
def profile(request):
    user=request.user
    
    return render(request, 'profile.html',locals())

@user_passes_test(lambda u: u.is_superuser)
def master(request):
    
    
    return render(request,'master.html',locals())

    
@csrf_exempt
def ajax_api(request):
    key=request.POST.get('key','')
    if key=="refresh":
        now=team.objects.get(is_now=1)
        response_json={'credit' : now.total_money}
    elif key=="next":
        now=team.objects.get(is_now=1)
        try:
            next_team=team.objects.get(number=now.number+1)
            next_team.is_now=1
            next_team.save()
            now.is_now=0
            now.save()
            response_json={'name' : next_team.team_name}
        except:
            now.is_now=0
            now.save()
            first=team.objects.get(number=1)
            first.is_now=1
            first.save()
            response_json={'name' : "end"}
    else:
        change_user=User.objects.get(username=request.user.username)
        try:
            change_user=addict_user.objects.get(user=change_user)
            change_user.past_nickname=change_user.past_nickname+","+change_user.nickname
            change_user.nickname=request.POST.get('nickname')
            change_user.save()
        except:
            addict_user(user=change_user,nickname=request.POST.get('nickname')).save()
        return HttpResponseRedirect("/addict/")
        
    return HttpResponse(json.dumps(response_json,ensure_ascii=False), content_type=u"application/json; charset=utf-8")