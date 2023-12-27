from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from django.contrib.auth.models import User
from .models import Rectangle, Circle, Media, Shape, Template, Layout, Text, MediaContent
from .serializers import (
    RectangleSerializer, CircleSerializer, MediaSerializer,
    ShapeSerializer, TextSerializer, MediaContentSerializer,
    UserSerializer, TemplateSerializer, LayoutSerializer, CLASSNAME_TO_MODELS, CONTENT_TYPE_TO_CLASSNAME
)
from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import MethodNotAllowed
from .utils import camel_to_snake, flattern_to_nested
from rest_framework.decorators import action
import json
import traceback



class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class TemplateView(viewsets.ModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = [IsAuthenticated]


    def create(self, request):

        request_data = dict(request.data)
        request_data["user"] = request.user.id
        template_serializer = TemplateSerializer(data=request_data)
        if not template_serializer.is_valid():
            return Response(template_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        template = template_serializer.save()
        layout = Layout.objects.create(template=template)
        res = dict(template_serializer.data)
        res.update({"layout": {"_id": layout.id}})
        return Response(res, status=status.HTTP_201_CREATED)
    

    def update(self, request, *args, **kwargs):
        pk = kwargs['pk']
        try:
            instance = Template.objects.get(pk=pk)  
        except Template.DoesNotExist:
            return Response(status=404)

        serializer = TemplateSerializer(instance, data=request.data, partial=True)  

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save() 
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    

    @action(detail=False, methods=['GET'])
    def mine(self, request):
        return Response(TemplateSerializer(instance=Template.objects.filter(user=request.user) ,many=True).data)
    

    @action(detail=True, methods=['GET'])
    def medias(self, request, pk=None):
        images_shapes = Shape.objects.filter(layout__in=Layout.objects.filter(template=pk), content_type=3)
        media_contents = [media.media_content for media in Media.objects.filter(pk__in=[image.shape_id for image in images_shapes])]
        return Response(MediaContentSerializer(instance=media_contents, many=True).data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['GET'])
    def data(self, request, pk=None, *args, **kwargs):
        template_serializer = TemplateSerializer(instance=Template.objects.get(pk=pk)).data
        layouts = Layout.objects.filter(template=pk)

        layouts_data = LayoutSerializer(instance=layouts, many=True).data

        res = {
            "name": template_serializer["name"],
            "layouts": layouts_data,
            "stage_width": template_serializer["width"],
            "stage_height": template_serializer["height"]
        }


        return Response(res)
    

def get_model_fields(model):
    model_fields = model._meta.get_fields()
    field_names = [field.name for field in model_fields]
    return field_names


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


class MediaContentView(viewsets.ModelViewSet):
    queryset = MediaContent.objects.all()
    serializer_class = MediaContentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        user = request.user
        request_data = dict(request.data)
        request_data["user"] = user.id

        formatted_data = {}
        for key, value in request_data.items():
            formatted_data.update({key: value[0]} if type(value) is list else {key:value})

        print(request_data)
        print(formatted_data)
        serializer = self.serializer_class(data=formatted_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        image_content_instance = serializer.save()
        
        
        media_data = {
            "media_content": image_content_instance.id,
            "width": float(formatted_data['width']),
            "height": float(formatted_data['height'])
        }
        image_serializer = MediaSerializer(data=media_data)
        if not image_serializer.is_valid():
            return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        image_instance = image_serializer.save()

        shape_media_data = {
            "content_type": CLASSNAME_TO_MODELS['Image']['content_type'],
            "shape_id": image_instance.id,
            "layout": formatted_data['layout']
        }

        shape_serializer = ShapeSerializer(data=shape_media_data)
        if not shape_serializer.is_valid():
            return Response(shape_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        shape_serializer.save()

        return Response(shape_serializer.data, status=status.HTTP_201_CREATED)
    

class ShapeView(viewsets.ModelViewSet):
    queryset = Shape.objects.all()
    serializer_class = ShapeSerializer
    permission_classes = [IsAuthenticated]

    @classmethod
    def create_shape(cls, data, serializer_class):

        layout_id = data.pop("layout", None)

        generic_shape_serializer = serializer_class(data=data)

        if not generic_shape_serializer.is_valid():
            return Response(generic_shape_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        generic_shape = generic_shape_serializer.save()

        shape_dict = {
            "layout": layout_id,
            "content_type": ContentType.objects.get_for_model(generic_shape).id,
            "shape_id": generic_shape.id,
            "object": generic_shape.id,
        }
        shape_serializer = ShapeSerializer(data=shape_dict)

        if shape_serializer.is_valid():
            shape_serializer.save()
            return Response(shape_serializer.data, status=status.HTTP_201_CREATED)

        return Response(shape_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            

    def create(self, request, *args, **kwargs):
        layout_id = kwargs['layout_pk']

        request_data = request.data
        request_data = camel_to_snake(request_data)
        shape_type = request_data.pop('type', None)
        model_data = CLASSNAME_TO_MODELS.get(shape_type, None)
        if not model_data:
            return Response("Error")

        data_object = dict()
        for field in model_data["fields"]:
            data_object[field] = request_data.pop(field, None)
        
        serializer_class = model_data["serializer"]
        serializer = serializer_class(data=data_object)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        obj = serializer.save()


        shape_dict = {
            "layout": layout_id,
            "content_type": ContentType.objects.get_for_model(obj).id,
            "shape_id": obj.id,
            "object": obj.id,
        }
        request_data["draggable"] = str(request_data["draggable"])
        shape_dict.update(request_data)
        shape_dict = camel_to_snake(shape_dict)
        print('--->', shape_dict)
        shape_serializer = ShapeSerializer(data=shape_dict) 

        if shape_serializer.is_valid():
            shape_serializer.save()
            return Response(shape_serializer.data, status=status.HTTP_201_CREATED)

        return Response(shape_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def update(self, request, *args, **kwargs):
        request_data = request.data
        request_data["draggable"] = str(request_data["draggable"])
        
        snake_case_data = camel_to_snake(request_data)

        shape_instance = Shape.objects.get(pk=kwargs['pk'])
        fields = [field.name for field in shape_instance.content_object._meta.fields if field.name != "id"]

        snake_case_data = flattern_to_nested(snake_case_data, fields, "updated_object")
        nested_object_data = snake_case_data.pop('updated_object')
        nested_serializer = CLASSNAME_TO_MODELS[CONTENT_TYPE_TO_CLASSNAME[str(shape_instance.content_type.id)]]["serializer"]

        updated_nested_object = nested_serializer(shape_instance.content_object, data=nested_object_data)
        if updated_nested_object.is_valid():
            updated_nested_object.save()


        serializer = ShapeSerializer(instance=shape_instance, data=snake_case_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class LayoutView(viewsets.ModelViewSet):
    queryset = Layout.objects.all()
    serializer_class = LayoutSerializer
    permission_classes = [IsAuthenticated]


