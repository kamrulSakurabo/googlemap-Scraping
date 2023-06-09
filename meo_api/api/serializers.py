from rest_framework import serializers
from django.utils import timezone
from . models import Condition, Search, Place


class ConditionSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(read_only=True)
    api_key = serializers.CharField(read_only=True)

    class Meta:
        model = Condition
        fields = '__all__'
        #  exclude = ['start_date']


class SearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Search
        fields = '__all__'


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = '__all__'
