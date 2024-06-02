import logging
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Product
from .serializer import ProductRetrieveSerializers
from .amazon_scraper.check_amazon_product import AmazonScraper, AmazonScraperError


logger = logging.getLogger(__name__)

class CheckProductApiView(APIView):
    def get(self, request, *args, **kwargs):
        product_data = cache.get(kwargs['product_code'])
        if product_data:
            serializer = ProductRetrieveSerializers(instance=product_data)
        else:
            try:
                product_instance = Product.objects.get(code=kwargs['product_code'])
                serializer = ProductRetrieveSerializers(instance=product_instance)
            except Product.DoesNotExist:
                try:
                    amazon_scraper = AmazonScraper()
                    product_data = amazon_scraper.get_product(product_code=kwargs['product_code'])
                    if not product_data:
                        return Response(status=status.HTTP_404_NOT_FOUND)
                except AmazonScraperError as e:
                    logger.error(e.message)
                    return Response(data={"message": "The service is not responding"}, status=status.HTTP_400_BAD_REQUEST)
                
                product_data["code"] = kwargs['product_code']
                product_data["name"] = product_data['title']
                product_data["avg_score"] = product_data['score']
                serializer = ProductRetrieveSerializers(data=product_data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

        cache.set(kwargs['product_code'], serializer.data, 60*60*24)
        return Response(serializer.data, status=status.HTTP_200_OK)
