from django.http.response import Http404
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.relations import ManyRelatedField
from rest_framework.response import Response

from base.models import Product, Order, OrderItem, ShippingAddress
from base.serializers import ProductSerializer, OrderSerializer

from rest_framework import status


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOrder(request):
    user = request.user
    data = request.data
    orderItems = data['orderItems']
    if not orderItems:
        message = {'detail': 'No items in the order'}
        return Response({'detail': 'No items in the order'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        # 1. create order
        order = Order.objects.create(
            user=user,
            paymentMethod=data['paymentMethod'],
            taxPrice=data['taxPrice'],
            shippingPrice=data['shippingPrice'],
            totalPrice=data['totalPrice']
        )
        # 2. create shipping object
        shipping = ShippingAddress.objects.create(
            order=order,
            address=data['shippingAddress']['address'],
            city=data['shippingAddress']['city'],
            country=data['shippingAddress']['country'],
            postalCode=data['shippingAddress']['postalCode']
        )

        # 3. create order items and set order-item relationship
        for i in orderItems:
            product = Product.objects.get(_id=i['product'])
            item = OrderItem.objects.create(
                product=product,
                order=order,
                name=product.name,
                qty=i['qty'],
                price=i['price'],
                image=product.image.url,
            )
            product.countInStock -= item.qty
            product.save()
        serializer = OrderSerializer(order, many=False)
        return Response(serializer.data)
