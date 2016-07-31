"""
Profile serializers for model data.
"""
from rest_framework import serializers
from .models import Profile


# pylint: disable=R0903
class ProfileSerializer(serializers.ModelSerializer):
    """ Serialize profile object. """
    class Meta(object):
        """ Define what is in a serialize response. """
        model = Profile
        fields = ('id', 'name')
