
from unittest import mock
from rest_framework import serializers
from .models import Candidate, Election#,Registration


class ElectionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Election
        field='__all__'

class CandidateSerializer(serializers.Serializer):
    class Meta:
        model= Candidate
        field='__all__'


        

# class RegistrationSerializer(serializers.Serializer):
#     class Meta:
#         model=Registration
#         field='__all__'

# class LoginSerializer(serializers.Serializer):
#     class Meta:
#         model=Login
#         field='__all__'