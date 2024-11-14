from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import FillCredit
from .serializers import FillCreditSerializer


# Create your views here.


class FillCreditListCreate(generics.ListCreateAPIView):
    queryset = FillCredit.objects.all().order_by('created_at')
    serializer_class = FillCreditSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(f"request.data: {request.data}")
        print(f"serializer: {serializer}")
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({"message": "Fill Credit has been Added."}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
