from distutils.command.upload import upload
from email.policy import default
from enum import auto
from django.db import models
import json

class Candidate(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    # voting_secret=models.CharField(max_length=255, default="")
    logo=models.ImageField(upload_to="images/", default="")
    def __str__(self):
        return self.title

    # def toJson(self):
    #     return json.dumps(self, default=lambda o: o.__dict__)


class Election(models.Model):
    id = models.AutoField(primary_key=True)
    election_title = models.CharField(max_length=255)
    start_at = models.DateTimeField(default=None)
    end_at = models.DateTimeField(default=None)
    candidates=models.ManyToManyField(Candidate)
    
    def __str__(self):
        return str(self.id) +": "+ self.election_title

    def electionCandidates(self):
        return ",".join([str(candidate) for candidate in self.candidates.all()])

    # def toJson(self):
    #     return json.dumps(self, default=lambda o: o.__dict__)

class Registration(models.Model):
    id = models.AutoField(primary_key=True)
    full_name=models.CharField(max_length=255)
    cnic=models.CharField(max_length=13)
    mother_name=models.CharField(max_length=255)
    mother_cnic=models.CharField(max_length=13)
    email=models.CharField(max_length=255)
    password=models.CharField(max_length=255)
    address=models.CharField(max_length=50)
    mobile=models.CharField(max_length=50)
    

class Vote(models.Model):
    id = models.AutoField(primary_key=True)
    election_id = models.IntegerField()
    user_id = models.IntegerField()
    candidate_id = models.IntegerField()
    # election_id = models.ForeignKey(Election,on_delete=models.CASCADE,)
    # election_id = models.CharField(max_length=255)
    # user_id = models.CharField(max_length=255)
    # candidate_id = models.CharField(max_length=255)
    casted_at = models.DateTimeField(max_length=255)
    class VoteStatus(models.TextChoices):
        PENDING = 'pn', ('Pending')
        ACCEPTED = 'ac', ('Accepted')
        REJECTED = 'rj', ('Rejected')
    status = models.CharField(max_length=2, choices=VoteStatus.choices,default=VoteStatus.PENDING,)

# class Mcq(models.Model):
#     id = models.AutoField(primary_key=True)
#     mcqs_string = models.CharField( max_length=255)
#     user_id = models.CharField(max_length=255)
#     election_id = models.CharField( max_length=50)
