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
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({"message": "Fill Credit has been Added."}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FillCreditRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = FillCredit.objects.all()
    serializer_class = FillCreditSerializer

    def put(self, request, *args, **kwargs):
        try:
            fill_credit = FillCredit.objects.get(pk=kwargs['pk'])
        except FillCredit.DoesNotExist:
            return Response({"message": "Fill Credit does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Update the serializer with game_day if provided
        serializer = self.get_serializer(fill_credit, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Fill Credit has been updated."}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)