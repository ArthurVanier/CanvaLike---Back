from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

# Create your models here.  

class Template(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
        

class ShapeShadow(models.Model):
    shadow_color = models.CharField(max_length=32, default='black')
    shadow_blurr = models.FloatField(max_length=32, default=0)
    shadow_offset_x = models.FloatField(default=0.0)
    shadow_offset_y = models.FloatField(default=0.0)
    shadow_opacity = models.FloatField(default=0.0)


class ShapeProps(models.Model):

    fill_color = models.CharField(max_length=32, default='white')
    stroke = models.CharField(max_length=32, default='black')
    strokeWidth = models.FloatField(default=1)
    opacity = models.FloatField(default=1.0)


class Shape(models.Model):
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='shapes')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    shape_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'shape_id')
    
    props = models.ForeignKey(ShapeProps, on_delete=models.CASCADE)
    shadow = models.ForeignKey(ShapeShadow, on_delete=models.CASCADE)


class TemplateShapeRelation(models.Model):
    template_id = models.ForeignKey(User, on_delete=models.CASCADE)
    shape_id = models.ForeignKey(Shape, on_delete=models.CASCADE)


class Rectangle(models.Model):
    x = models.FloatField()
    y = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()


class Circle(models.Model):
    x = models.FloatField()
    y = models.FloatField()
    radius=models.FloatField()



class Media(models.Model):
    x = models.FloatField()
    y = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()

    content = models.FileField(upload_to='src/', blank=True, null=True)



class TemplateShapeRelation(models.Model):
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
    shape = models.ForeignKey(Shape, on_delete=models.CASCADE)


