from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from .models import Customer
from rest_framework.views import APIView
from .serializers import CustomerSerializer
from rest_framework import generics


# Create your views here.

class CustomerListCreateView(APIView):

    def post(self, request, *args, **kwargs):
        print(request.data)
        try:
            customer_quantity = int(request.data.get('quantity', 0))
            if customer_quantity <= 0:
                return Response({'message': 'Quantity must be greater than zero'}, status=status.HTTP_400_BAD_REQUEST)

            customers = [Customer() for _ in range(customer_quantity)]
            Customer.objects.bulk_create(customers)

            return Response({'message': f'{customer_quantity} customers created successfully'}, status=status.HTTP_201_CREATED)

        except Exception:
            return Response({"message": "Invalid count provided."}, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, *args, **kwargs):
        try:
            customers = Customer.objects.all().order_by('id')
            serializer = CustomerSerializer(customers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response({"message": "Error fetching customers."}, status=status.HTTP_400_BAD_REQUEST)
