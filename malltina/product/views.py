from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Product
from .serializer import ProductRetrieveSerializers

class CheckProductApiView(APIView):
    def get(self, request, *args, **kwargs):
        product_instance = Product.objects.get(code=kwargs['product_code'])
        data = ProductRetrieveSerializers(instance=product_instance)

        return Response(data.data, status=status.HTTP_200_OK)
