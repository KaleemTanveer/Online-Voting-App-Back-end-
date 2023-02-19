from email.headerregistry import Address, ContentTypeHeader
from multiprocessing import connection
from django.shortcuts import render,redirect
from datetime import datetime
from django.shortcuts import render
from rest_framework import viewsets
from django.db import connection
import elections
from .models import Election, Registration, Vote#, ElectionCandidate
# from .models import Registration
from .models import Candidate

from elections import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import HttpResponse
from .serializers import ElectionSerializer,CandidateSerializer
from django.http import HttpResponse, JsonResponse
from rest_framework import status
import hashlib
import requests
from  .models import Candidate
# from django.core.serializers.json import DjangoJSONEncoder





class all_views ():

    def dictfetchall(cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    def landing(request):
        session_username = request.session.get('kaleem',False)
        context = {
            "title":"Home",
            "session_username":session_username
                 }
        return render(request,'front-end.html',context)

    @api_view(['GET'])
    def ElectionList(request):
        registration_email = request.session.get('login_user',False)
        if not registration_email:
            return JsonResponse({
            'data':{
            }
        }, status=403)
        current_elections = Election.objects.filter(start_at__lt=datetime.now(),end_at__gt=datetime.now()).order_by('start_at').values()
        upcoming_elections = Election.objects.filter(start_at__gt=datetime.now()).order_by('start_at').values()
        past_elections = Election.objects.filter(end_at__lt=datetime.now()).order_by('end_at').values()
        current_elections = list(current_elections)
        upcoming_elections = list(upcoming_elections)
        past_elections = list(past_elections)

        
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id FROM elections_registration 
            WHERE email = '{registration_email}' LIMIT 1
        """.format(registration_email=registration_email))
        db_results = all_views.dictfetchall(cursor)
        
        for election in current_elections:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT id FROM elections_vote 
                WHERE user_id = '{registration_id}' AND election_id = {election_id} LIMIT 1
            """.format(registration_id=db_results[0]['id'],election_id = election['id']))
            votes = all_views.dictfetchall(cursor)
            if len(votes) > 0:
                election['voted'] = True
            else:
                election['voted'] = False
        
        for election in past_elections:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT id FROM elections_vote 
                WHERE user_id = '{registration_id}' AND election_id = {election_id} LIMIT 1
            """.format(registration_id=db_results[0]['id'],election_id = election['id']))
            votes = all_views.dictfetchall(cursor)
            if len(votes) > 0:
                election['voted'] = True
            else:
                election['voted'] = False
        
        for election in upcoming_elections:
            election['voted'] = False

        return JsonResponse({
            'data':{
                'current_elections': current_elections,
                'upcoming_elections':upcoming_elections,
                'past_elections':past_elections,
            }
        }, status=200)

    @api_view(['GET'])
    def electionCandidatesList(request,election_id):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM elections_election where id="+str(election_id)+" ")
        elections = all_views.dictfetchall(cursor)
        if len(elections) == 0:
            return JsonResponse({"message":"Election not found"}, status=404)
        # elections=Election.objects.filter(id=election_id).values()
        elections_list = list(elections)
        for election in elections_list:
            cursor.execute("""
            SELECT elections_election_candidates.id as id, elections_registration.full_name as full_name,
                 elections_candidate.title as title, elections_candidate.logo as logo
            FROM elections_election_candidates 
                LEFT JOIN elections_candidate ON elections_election_candidates.candidate_id = elections_candidate.id 
                LEFT JOIN elections_registration ON elections_candidate.user_id = elections_registration.id 
            WHERE election_id={election_id}""".format(election_id=election_id))
            election['election_candidates'] = all_views.dictfetchall(cursor)
      
        
        return JsonResponse(elections_list[0], status=200)
    
    @api_view(["POST"])
    def Registration(request):
        if request.method == "POST":
            full_name=request.POST.get('full_name','')
            cnic=request.POST.get('cnic','')
            mother_name=request.POST.get('mother_name','')
            mother_cnic=request.POST.get('mother_cnic','')
            email=request.POST.get('email','')
            password=request.POST.get('password','')
            re_password=request.POST.get('re_password','')
            address=request.POST.get('address','')
            mobile=request.POST.get('mobile','')
            errors = {
            }
            if len(full_name) < 3:
                errors["full_name"]="Enter your full name"
            if len(cnic)  != 13:
                errors["cnic"]="Enter correct CNIC"
            elif Registration.objects.filter(cnic=cnic).exists():
                errors["cnic"]='User already Registered'
            if len(mother_name)<3:
                errors["mother_name"]='Enter your Mother name'
            if len(mother_cnic) != 13:
                errors["mother_cnic"]="Enter Your Mother CNIC"
            if len(email)<3:
                errors["email"]='Enter your email'
            elif Registration.objects.filter(email=email).exists():
                errors["email"]='User already Registered'
            if len(password) < 6:
                errors["re_password"] = "Minimum 6 characters"
            elif password != re_password:
                errors["re_password"] = "Enter same password"
            if len(address)<3:
                errors["address"]="Enter your address"  
            if len(mobile) != 11:
                errors["mobile"]="Enter your mobile"
            
            if not errors:                
                newReg = Registration()
                newReg.full_name = full_name
                newReg.cnic = cnic
                newReg.mother_name = mother_name
                newReg.mother_cnic = mother_cnic
                newReg.email = email
                newReg.password = hashlib.sha1(password.encode('utf-8')).hexdigest()
                newReg.address = address
                newReg.mobile = mobile
                newReg.save()
        if errors:
            content = {
                "status":"WRONG PARAMS",
                "errors":errors,
            }
            return JsonResponse(content, status=status.HTTP_403_FORBIDDEN)
        return JsonResponse({
            
            'errors':list(errors),
            
            'data':{
                'full_name':(full_name),
                'cnic':(cnic),
                'mother_name':mother_name,
                'mother_cnic':mother_cnic,
                'email':email,
                'password':password,
                're_password':re_password,
                'address':address,
                'mobile':mobile,
                # 'category':category,
            }
        }, safe=False)
    
    @api_view(["POST"])
    def Login(request):
        session = requests.Session()
        session_username = request.session.get('login_user',False)
        if session_username:
            return JsonResponse({
                'data':{},
                'message': 'User already logged in'
            }, status=400)
        email = request.POST.get('email',None)
        password = request.POST.get('password',None)
        if not email or not password:
            return JsonResponse({
                'data':{},
                'message': 'Please provide username and password'
            }, status=400)
        user = Registration.objects.filter(email=email, password=hashlib.sha1(password.encode('utf-8')).hexdigest())
        if user:
            request.session['login_user'] = email
            return JsonResponse({
                'data': {
                    'user_email':email,
                    'user_key': hashlib.sha1(password.encode('utf-8')).hexdigest()
                },
                'message': 'Login successful'
            }, status=200)
        return JsonResponse({
            'data':{},
            'message': 'Wrong usernaeme or password'
        }, status=404)
    
    @api_view(["GET"])    
    def Logout(request):
        # return {"data":request.session[]}
        if request.session.get('login_user',None):
            request.session.pop('login_user')
            return JsonResponse({
                'data':{},
                'message': 'Logout successful'
            }, status=200)
        return JsonResponse({
            'data':{},
            'message': 'User not logged in'
        }, status=200)
    
    @api_view(["GET"])    
    def checkUser(request):
        if request.session.get('login_user',None):
            return JsonResponse({
                'data':request.session.get('login_user',None),
                'message': 'User retrieved'
            }, status=200)
        return JsonResponse({
            'data':{},
            'message': 'User not logged in'
        }, status=404)

    @api_view(['GET'])
    def MotherMCQList(request):
        registration_email = request.session.get('login_user',False)
        if not registration_email:
            return JsonResponse({
            'data':{
            }
        }, status=403)
        # Read mother's name of voter
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id,mother_name,mother_cnic FROM elections_registration 
            WHERE email = '{registration_email}' LIMIT 1
        """.format(registration_email=registration_email))
        db_results = all_views.dictfetchall(cursor)
        mother_name = list(db_results)[0]['mother_name']
        mother_short_name = list(db_results)[0]['mother_name'].split()[0]
        mother_cnic = list(db_results)[0]['mother_cnic']
        user_id = list(db_results)[0]['id']
        print(mother_name)
        print(mother_short_name)
        #Read random mother names
        cursor = connection.cursor()
        cursor.execute("""
            SELECT mother_name  FROM elections_registration 
            WHERE mother_name NOT LIKE "{mother_short_name}%" AND mother_cnic != "{mother_cnic}" GROUP BY mother_cnic ORDER BY rand({seed}) LIMIT 4
        """.format(mother_short_name=mother_short_name,mother_cnic=mother_cnic,seed=user_id))
        mothers = all_views.dictfetchall(cursor)
        # if len(mothers) == 0:
        #     return JsonResponse({"message":"Election not found"}, status=404)
        mothers_list = list(mothers)
        all_mothers = []
        for mother in mothers_list:
            all_mothers.append(mother['mother_name'])
        all_mothers.append(mother_name)
      
        import random
        random.shuffle(all_mothers)
        return JsonResponse({
            "mothers":all_mothers
        }, status=200)

    @api_view(['POST'])
    def CastVote(request):
        registration_email = request.session.get('login_user',False)
        if not registration_email:
            return JsonResponse({
            'data':{
            }
        }, status=403)
        if request.method!="POST":
            return JsonResponse({
                'data':{},
                'message': 'Wrong params'
            }, status=404)
        mother_name = request.POST.get('mother_name',None)
        candidate_id = request.POST.get('candidate_id',None)
        election_id = request.POST.get('election_id',None)
        if not mother_name or not candidate_id or not election_id:
            return JsonResponse({
                'data':{},
                'message': 'Wrong params'
            }, status=500)
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id, mother_name FROM elections_registration 
            WHERE email = '{registration_email}' LIMIT 1
        """.format(registration_email=registration_email))
        db_results = all_views.dictfetchall(cursor)
        db_results = list(db_results)
        newVote = Vote()
        user_data = db_results[0]
        newVote.user_id = user_data['id']

        cursor = connection.cursor()
        cursor.execute("""
            SELECT id FROM elections_vote 
            WHERE user_id = '{user_id}' AND election_id = '{election_id}' LIMIT 1
        """.format(user_id=user_data['id'], election_id=election_id))
        db_results = all_views.dictfetchall(cursor)
        db_results = list(db_results)

        if len(db_results) > 0:
            return JsonResponse({
                'data':{},
                'message': 'Already casted'
            }, status=401)

        newVote.election_id = election_id
        newVote.candidate_id = candidate_id
        newVote.casted_at = datetime.now()
        if user_data['mother_name'] == mother_name:
            newVote.status = Vote.VoteStatus.ACCEPTED
        else:
            newVote.status = Vote.VoteStatus.REJECTED
        newVote.save()
        #Vote accepted
        return JsonResponse({
            'data':{},
            'message': 'Vote casted'
        }, status=200)

    @api_view(['GET'])
    def VerifySession(request):
        session_username = request.session.get('login_user',False)
        print("VerifySession")
        print(session_username)
        if session_username:
            return JsonResponse({
                'data': {},
                'message': 'Verified'
            }, status=200)
        return JsonResponse({
            'data': {},
            'message': 'Unverified'
        }, status=401)


    @api_view(['POST'])
    def forgetPassword(request):
        email = request.POST.get('email','')
        cnic = request.POST.get('cnic','')
        mother_cnic = request.POST.get('mother_cnic','')
        password = request.POST.get('password','')
        print(email)
        print(cnic)
        print(mother_cnic)
        print(password)
        if not email or not cnic or not mother_cnic or not password or len(password) < 6:
            return JsonResponse({
            'data':{
            }
        }, status=403)
        cursor = connection.cursor()
        cursor.execute("""
            SELECT id,mother_name,mother_cnic FROM elections_registration 
            WHERE email = '{email}' AND cnic = '{cnic}' AND mother_cnic = '{mother_cnic}' LIMIT 1
        """.format(email=email,cnic=cnic, mother_cnic=mother_cnic))
        db_results = all_views.dictfetchall(cursor)
        if len(db_results) <= 0:
            return JsonResponse({
            'data':False
            }, status=403)
        cursor.execute("""
            UPDATE  elections_registration 
            SET password = '{sha1_password}'
            WHERE email = '{email}' AND cnic = '{cnic}' AND mother_cnic = '{mother_cnic}' LIMIT 1
        """.format( sha1_password=hashlib.sha1(password.encode('utf-8')).hexdigest(),
                    email=email,
                    cnic=cnic,
                    mother_cnic=mother_cnic))
        return JsonResponse({
        'data':True
        }, status=200)

    @api_view(['GET'])
    def electionResultsList(request,election_id):
        cursor = connection.cursor()
        cursor.execute("""
            SELECT 
                elections_election_candidates.candidate_id as candidate_id, 
                count(*) as total, 
                SUM(IF(elections_vote.status='ac',1,0)) as accepted, 
                SUM(IF(elections_vote.status='rj',1,0)) as rejected 
            FROM elections_election_candidates
            LEFT JOIN elections_vote
                ON elections_election_candidates.candidate_id = elections_vote.candidate_id
            WHERE elections_election_candidates.election_id = {election_id} 
            GROUP By candidate_id
            ORDER BY accepted DESC, total DESC
            """.format(election_id=election_id))
        candidates_results = all_views.dictfetchall(cursor)
        print("candidates_results")
        print(list(candidates_results))
        candidates = []
        for results in list(candidates_results):    
            cursor = connection.cursor()
            cursor.execute("""
                SELECT 
                    elections_candidate.title as title,elections_candidate.logo as logo, 
                    elections_registration.full_name as full_name
                FROM elections_candidate 
                    LEFT JOIN elections_registration ON elections_candidate.user_id = elections_registration.id 
                WHERE elections_candidate.id= {candidate_id} 
                """.format(candidate_id=results['candidate_id']))
            db_return = list(all_views.dictfetchall(cursor))
            db_return = db_return[0]
            candidates.append({
                "candidate_id" : results['candidate_id'],
                "candidate_title" : db_return['title'],
                "candidate_full_name" : db_return['full_name'],
                "candidate_logo" : db_return['logo'],
                "total_votes" : results['total'],
                "accepted_votes" : results['accepted'],
                "rejected_votes" : results['rejected'],
            })
      
        return JsonResponse({
            'data': candidates,
            'message': 'Results'
        }, status=200)