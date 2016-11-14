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
    response_json={}
    if key=="reset":
        all=addict_user.objects.all()
        for user in all:
            user.credit=400
            user.save()
    elif key=="give":
        all=addict_user.objects.all()
        for user in all:
            user.credit=user.credit+100
            user.save()
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
    
@csrf_exempt
def node_api(request):
    session = Session.objects.get(session_key=request.POST.get('sessionid'))
    user_id = session.get_decoded().get('_auth_user_id')
    user = User.objects.get(id=user_id)
    key_value=request.POST.get('key')
    
    if key_value=='credit':
        credit_value=request.POST.get('content')
        now=team.objects.get(is_now=1)
        
        if (int(credit_value)<0):
            response_json={
                'key' : key_value,
                'user' : user.addict_user.nickname,
                'credit' : 0,
                'total' : now.total_money,
            }
        elif user.addict_user.credit-int(credit_value)>=0:
            now.total_money=now.total_money+int(credit_value)
            now.save()
            user.addict_user.credit=user.addict_user.credit-int(credit_value)
            user.addict_user.save()
            response_json={
                'key' : key_value,
                'user' : user.addict_user.nickname,
                'credit' : credit_value,
                'total' : now.total_money,
            }
        else:
            response_json={
                'key' : 'poor',
                'user' : user.addict_user.nickname,
            }
    elif key_value=='clear':
        value=1 if user.is_superuser else 0
        response_json={
            'key' : key_value,
            'value' : value,
        }
    elif key_value=='reset':
        if user.is_superuser:
            addict_user.objects.update(credit=400)
            response_json={
                'key' : key_value,
            }
    elif key_value=='give':
        if user.is_superuser:
            all=addict_user.objects.all()
            for user in all:
                user.credit=user.credit+100
                user.save()
            response_json={
                'key' : key_value,
            }
    else:
        if user.is_superuser:
            now=team.objects.get(is_now=1)
            try:
                next_team=team.objects.get(number=now.number+1)
                next_team.is_now=1
                next_team.save()
                now.is_now=0
                now.save()
                name=next_team.team_name
            except:
                now.is_now=0
                now.save()
                first=team.objects.get(number=1)
                first.is_now=1
                first.save()
                name="end"
            value=1
            response_json={
                'key' : key_value,
                'value' : value,
                'name' : name,
            }

    
    r=redis.Redis()
    r.publish('chat', json.dumps(response_json,ensure_ascii=False))
    return HttpResponse("Everything worked :)")