from rest_framework import generics, mixins, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Condition, Search
from front_shop.models import RangingCondition
from .serializers import ConditionSerializer
from .search import search_in_google_map
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
import hashlib
import jwt
import uuid
import requests
import json

# Create your views here.


class ConditionViewSet(viewsets.ModelViewSet):
    queryset = Condition.objects.all()
    serializer_class = ConditionSerializer
    lookup_field = 'api_key'
    # permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        api_key = self.generate_api_key(self.request.data)
        serializer.save(api_key=api_key)

    def perform_update(self, serializer):
        condition = self.get_object()
        if condition.api_key != condition.api_key:
            return Response({'error': 'Invalid API Key'}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        print(self.request.data)

    def get_object(self):
        return get_object_or_404(Condition, api_key=self.kwargs.get('api_key'))

    def generate_api_key(self, data):
        api_key_payload = {
            'key_words': data['key_words'],
            'latitude': data['latitude'],
            'longitude': data['longitude'],
            'scheduled_start_time': data['scheduled_start_time'],
            'scheduled_end_time': data['scheduled_end_time'],
            'random_string': uuid.uuid4().hex
        }
        jwt_token = jwt.encode(api_key_payload, 'secret', algorithm='HS256')
        api_key = hashlib.sha256(jwt_token.encode()).hexdigest()[:32]
        return api_key


class GoogleMapView(APIView):
    def get(self, request, api_key=None):
        print("API KEY:", ('api_key'))
        try:
            condition = Condition.objects.get(api_key=api_key)
            print("Condition:", condition.__dict__)
            search_instance = Search.objects.filter(condition=condition)
            search_result = search_in_google_map(condition)
            data_list = []
            for search_instance in search_instance:
                search_result = search_in_google_map(condition)
                data = {
                    'condition': condition.id,
                    'key_words': condition.key_words,
                    'latitude': condition.latitude,
                    'longitude': condition.longitude,
                    'search_result': search_result,
                    'start_datetime': search_instance.start_datetime,
                    'end_datetime': search_instance.end_datetime,
                    'search_date': search_instance.search_date,
                }
                data_list.append(data)

                for data in data_list:
                    response = requests.post(f'http://localhost:8000/search/{condition.api_key}/', json=data)
                    if response.status_code != 200:
                        print(f"Response content: {response.content}")
                        return Response({'error':'Failed to send data to front_shop server'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
                return Response(data_list)
        
        except ObjectDoesNotExist:
            return Response({'Error':'Invalid API key'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
                print(f"Error: {str(e)}")
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # response = requests.post(f'http://localhost:8000/search/{condition.api_key}/', json=search_result)
        # if response.status_code != 200:
        #     return Response({'error':'Failed to send data to front_shop server'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        # return Response({'Search result': search_result})
