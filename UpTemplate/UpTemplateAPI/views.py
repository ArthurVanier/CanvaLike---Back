from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from django.contrib.auth.models import User
from .models import Rectangle, Circle, Media, Shape, ShapeProps, ShapeShadow, Template, TemplateShapeRelation
from .serializers import (
    RectangleSerializer, CircleSerializer, MediaSerializer,
    ShapeSerializer, ShapePropsSerializer, ShadowPropsSerializer,
    UserSerializer, TemplateSerializer
)
from django.contrib.contenttypes.models import ContentType

class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class TemplateView(viewsets.ModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = [IsAuthenticated]


    def create(self, request):

        request_data = dict(request.data)

        #request_data.update({"user": request.user.id})
        template_serializer = TemplateSerializer(data=request_data)
        if not template_serializer.is_valid():
            return Response(template_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        template_serializer.save()
        
        return Response(template_serializer.data, status=status.HTTP_201_CREATED)



class RectangleView(viewsets.ModelViewSet):
    queryset = Rectangle.objects.all()
    serializer_class = RectangleSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        return ShapeView.create_shape(dict(request.data), self.serializer_class)


class CircleView(viewsets.ModelViewSet):
    queryset = Circle.objects.all()
    serializer_class = CircleSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        return ShapeView.create_shape(dict(request.data), self.serializer_class)


class MediaView(viewsets.ModelViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticated]


class ShapeView(viewsets.ModelViewSet):
    queryset = Shape.objects.all()
    serializer_class = ShapeSerializer
    permission_classes = [IsAuthenticated]

    @classmethod
    def create_shape(cls, data, serializer_class):

        template_id = data.pop("template", None)
        props = data.pop("props", None)
        shadow = data.pop("shadow", None)

        generic_shape_serializer = serializer_class(data=data)

        if not generic_shape_serializer.is_valid():
            return Response(generic_shape_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        generic_shape = generic_shape_serializer.save()

        shape_dict = {
            "template": template_id,
            "content_type": ContentType.objects.get_for_model(generic_shape).id,
            "shape_id": generic_shape.id,
            "object": generic_shape.id,
            "props": props,
            "shadow": shadow
        }
        shape_serializer = ShapeSerializer(data=shape_dict)

        if shape_serializer.is_valid():
            shape_serializer.save()
            return Response(shape_serializer.data, status=status.HTTP_201_CREATED)

        return Response(shape_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShapePropsView(viewsets.ModelViewSet):
    queryset = ShapeProps.objects.all()
    serializer_class = ShapePropsSerializer
    permission_classes = [IsAuthenticated]


class ShapeShadowView(viewsets.ModelViewSet):
    queryset = ShapeShadow.objects.all()
    serializer_class = ShadowPropsSerializer
    permission_classes = [IsAuthenticated]
