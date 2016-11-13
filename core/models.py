from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class addict_user(models.Model):  
    user = models.OneToOneField(User)
    nickname = models.CharField(max_length=100,default="")
    credit=models.IntegerField(default=400)
    past_nickname=models.CharField(max_length=1000,default="")
    
    
class team(models.Model):
    team_name = models.CharField(max_length=30)
    total_money=models.IntegerField(default=0)
    number=models.IntegerField()
    is_now=models.BooleanField(default=0)
    
    def __str__(self):
        
        return self.team_name+" "+str(self.number)+" 번째"
    