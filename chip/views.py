from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from .models import ChipModel
from .serializers import ChipModelSerializer


class ChipListCreate(generics.ListCreateAPIView):
    queryset = ChipModel.objects.all().order_by('denomination')
    serializer_class = ChipModelSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({"message": "Chip has been Added."}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChipDetailUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = ChipModel.objects.all()
    serializer_class = ChipModelSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Chip deleted successfully"}, status=status.HTTP_200_OK)


