from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from .models import Table, CloseFloot
from .serializers import TableSerializer, CloseFlootSerializer

class TableListCreate(generics.ListCreateAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({"message": "Table has been Added."}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TableRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Table.objects.all()
    serializer_class = TableSerializer

class CloseFlootListCreate(generics.ListCreateAPIView):
    queryset = CloseFloot.objects.all()
    serializer_class = CloseFlootSerializer

class CloseFlootRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = CloseFloot.objects.all()
    serializer_class = CloseFlootSerializer
