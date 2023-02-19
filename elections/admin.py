from django.contrib import admin
from elections.models import  Candidate, Election, Vote
from elections.models import Registration

class ElectionList(admin.ModelAdmin):
    list_display=('id','election_title','start_at','end_at','electionCandidates') 
    filter_horizontal = ['candidates']


class Registrationlist(admin.ModelAdmin):
    list_display=('id','full_name','cnic','mother_name','mother_cnic','email','password','address','mobile') 

class CandidateList(admin.ModelAdmin):
    list_display=('id','user_id','title','logo')

class VoteList(admin.ModelAdmin):
    readonly_fields = ["status"]
    list_display=('election_id','user_id','candidate_id','casted_at','status') 

# class McqsList(admin.ModelAdmin):
#     list_display =('id','mcqs_string','user_id','election_id')   
    

admin.site.register(Election, ElectionList)
admin.site.register(Registration, Registrationlist)
admin.site.register(Candidate,CandidateList)
admin.site.register(Vote,VoteList)

 
