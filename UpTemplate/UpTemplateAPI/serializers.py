from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Template, Rectangle, Circle, Media, Shape, Layout, Text, MediaContent
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from .utils import flatten_dict
import re



class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate_password(self, value: str) -> str:
        return make_password(value)


class RectangleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rectangle
        fields = '__all__'
    

    def __init__(self, *args, **kwargs):
        super(RectangleSerializer, self).__init__(*args, **kwargs)

        if self.instance:
            for field in self.fields.values():
                field.required = False


class CircleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Circle
        fields = '__all__'
    

    def __init__(self, *args, **kwargs):
        super(CircleSerializer, self).__init__(*args, **kwargs)

        if self.instance:
            for field in self.fields.values():
                field.required = False


class MediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Media
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(MediaSerializer, self).__init__(*args, **kwargs)

        if self.instance:
            for field in self.fields.values():
                field.required = False
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        media_content = int(representation["media_content"])
        media = MediaContentSerializer(instance=MediaContent.objects.get(pk=media_content))
        representation["media_content"] = media.data
        return representation


class TextSerializer(serializers.ModelSerializer):

    class Meta:
        model = Text
        fields = '__all__'
    

    def __init__(self, *args, **kwargs):
        super(TextSerializer, self).__init__(*args, **kwargs)

        if self.instance:
            for field in self.fields.values():
                field.required = False


CONTENT_TYPE_TO_TYPE = {
    "4": "v-rect",
    "1": "v-circle",
    "3": "v-image",
    "5": "v-text"
}


class ShapeSerializer(serializers.ModelSerializer):
    object = serializers.SerializerMethodField()

    class Meta:
        model = Shape
        fields = '__all__'
        
        extra_kwargs = {
            'shape_id': {'write_only': True},
            'layout': {'write_only': True},
        }
    

    def __init__(self, *args, **kwargs):
        super(ShapeSerializer, self).__init__(*args, **kwargs)

        if self.instance:
            for field in self.fields.values():
                field.required = False
        

    def get_object(self, obj):
        content_type = obj.content_type

        if content_type.model == 'rectangle':
            serializer = RectangleSerializer(Rectangle.objects.get(pk=obj.shape_id))

        elif content_type.model == 'circle':
            serializer = CircleSerializer(Circle.objects.get(pk=obj.shape_id))

        elif content_type.model == 'media':
            serializer = MediaSerializer(Media.objects.get(pk=obj.shape_id))

        elif content_type.model == 'text':
            serializer = TextSerializer(Text.objects.get(pk=obj.shape_id))
        else:
            serializer = None

        return serializer.data if serializer else {}
    

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation = flatten_dict(representation, "object")

        content_type = str(representation.pop('content_type', None))
        shape_type = CONTENT_TYPE_TO_TYPE[content_type]

        
        formated_representation = format_complex_fields(dict(representation), content_type)
        camel_case_representation = dict_keys_snake_to_camel(formated_representation)

        res = {
            "type": shape_type,
            "config": camel_case_representation
        }
        
        return res


def snake_to_camel(string):
    return re.sub(r'_([a-zA-Z])', lambda x: x.group(1).upper(), string) if string != "_id" else string


def dict_keys_snake_to_camel(d):    
    return {snake_to_camel(k): v for k, v in d.items()}


def format_complex_fields(representation, content_type):
    representation["shadow_offset"] = {"x": representation["shadow_offset_x"], "y": representation["shadow_offset_y"]}
    del representation["shadow_offset_x"]
    del representation["shadow_offset_y"]

    return representation



class LayoutSerializer(serializers.ModelSerializer):

    class Meta:
        model = Layout
        fields = '__all__'
    

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['shapes'] = ShapeSerializer(instance=Shape.objects.filter(layout=representation['id']), many=True).data
        return representation

class TemplateSerializer(serializers.ModelSerializer):
    layouts = LayoutSerializer(many=True, read_only=True)

    def __init__(self, *args, **kwargs):
        super(TemplateSerializer, self).__init__(*args, **kwargs)

        if self.instance:
            for field in self.fields.values():
                field.required = False


    class Meta:
        model = Template
        fields = ['id', 'user', 'name', 'layouts', 'width', 'height']
    

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation


    def update(self, instance, validated_data):

        field_to_exclude = ['user', 'shapes']
        for field in field_to_exclude:
            if field in validated_data:
                del validated_data[field]
        
        return super().update(instance, validated_data)


class MediaContentSerializer(serializers.ModelSerializer):

    class Meta:
        model = MediaContent
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation
    



CLASSNAME_TO_MODELS = {
    "Rect": {
        "content_type": 4,
        "model": Rectangle,
        "fields": ["width", "height"],
        "serializer": RectangleSerializer
    },
    "Circle": {
        "content_type": 1,
        "model": Circle,
        "fields": ["radius"],
        "serializer": CircleSerializer
    },
    "Text": {
        "content_type": 5,
        "model": Text,
        "fields": ["font_family", "font_size", "text"],
        "serializer": TextSerializer
    },
    "Image": {
        "content_type": 3,
        "model": Media,
        "fields": ["width", "height", "media_content"],
        "serializer": MediaSerializer
    }
}

CONTENT_TYPE_TO_CLASSNAME = {
    "4": "Rect",
    "1": "Circle",
    "5": "Text",
    "3": "Image"
}
