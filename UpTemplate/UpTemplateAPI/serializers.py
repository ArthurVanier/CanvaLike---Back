from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Template, ShapeShadow, ShapeProps, Rectangle, Circle, Media, Shape, TemplateShapeRelation
from django.shortcuts import get_object_or_404


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate_password(self, value: str) -> str:
        return make_password(value)


class ShapePropsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShapeProps
        fields = '__all__'


class ShadowPropsSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShapeShadow
        fields = '__all__'


class RectangleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rectangle
        fields = '__all__'


class CircleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Circle
        fields = '__all__'


class MediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Media
        fields = '__all__'



class ShapeSerializer(serializers.ModelSerializer):
    object = serializers.SerializerMethodField()

    props = ShapePropsSerializer()
    shadow = ShadowPropsSerializer()

    class Meta:
        model = Shape
        fields = ('id', 'content_type', 'object', 'props', 'shadow', 'template', 'shape_id')

    def get_object(self, obj):
        content_type = obj.content_type

        if content_type.model == 'rectangle':
            serializer = RectangleSerializer(Rectangle.objects.get(pk=obj.shape_id))

        elif content_type.model == 'circle':
            serializer = CircleSerializer(Circle.objects.get(pk=obj.shape_id))

        elif content_type.model == 'media':
            serializer = MediaSerializer(Media.objects.get(pk=obj.shape_id))

        else:
            serializer = None

        return serializer.data if serializer else {}


    def create(self, validated_data):

        props_data = validated_data.pop('props', {})
        props = ShapePropsSerializer(data=props_data)

        shadow_data = validated_data.pop('shadow', {})
        shadow = ShadowPropsSerializer(data=shadow_data)

        if not props.is_valid():
            return props.erros

        if not shadow.is_valid():
            return shadow.erros

        props_instance = props.save()
        shadow_instance = shadow.save()
        shape = Shape.objects.create(props=props_instance, shadow=shadow_instance, **validated_data)
        return shape


class TemplateSerializer(serializers.ModelSerializer):
    shapes = serializers.PrimaryKeyRelatedField(queryset=Shape.objects.all(), many=True)

    def __init__(self, *args, **kwargs):
        super(TemplateSerializer, self).__init__(*args, **kwargs)


    class Meta:
        model = Template
        fields = ['id', 'user', 'name', 'shapes']

    
    def get_shapes(self, obj):

        shape_id_list = [realtion.shape.id for realtion in TemplateShapeRelation.objects.filter(template__pk=obj.id)]
        shape_data_list = Shape.objects.filter(pk__in=shape_id_list)
        shape_serializer = ShapeSerializer(shape_data_list, many=True)

        return shape_serializer.data
    

    def to_representation(self, instance):

        data = super().to_representation(instance)
        data["shapes"] = self.get_shapes(instance)
        return data


    def create(self, validated_data):

        shapes_list = validated_data.pop('shapes')
        template = Template.objects.create(**validated_data)

        for shape in shapes_list:
            TemplateShapeRelation.objects.create(template=template, shape=shape)
        
        return template