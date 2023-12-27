from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

# Create your models here.  

class Template(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)

    width = models.FloatField(default=800)
    height = models.FloatField(default=600)

class Layout(models.Model):
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
    


class Shape(models.Model):
    _id = models.AutoField(primary_key=True)
    layout = models.ForeignKey(Layout, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    shape_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'shape_id')

    # Transform
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    offset_x = models.FloatField(default=0)
    offset_y = models.FloatField(default=0)
    scale_x = models.FloatField(default=1)
    scale_y = models.FloatField(default=1)
    rotation = models.FloatField(default=0)


    # Props params
    fill = models.CharField(max_length=32, default='white')
    stroke = models.CharField(max_length=32, default='black')
    stroke_width = models.FloatField(default=1)
    opacity = models.FloatField(default=1.0)

    # Shadow params
    shadow_color = models.CharField(max_length=32, default='black')
    shadow_blurr = models.FloatField(max_length=32, default=0)
    shadow_offset_x = models.FloatField(default=0.0)
    shadow_offset_y = models.FloatField(default=0.0)
    shadow_opacity = models.FloatField(default=0.0)

    draggable = models.CharField(default=True, max_length=16)


class Rectangle(models.Model):
    width = models.FloatField()
    height = models.FloatField()


class Text(models.Model):
    font_family = models.CharField(max_length=32)
    font_size = models.IntegerField()
    text = models.TextField()


class Circle(models.Model):
    radius=models.FloatField()

class MediaContent(models.Model):
    content = models.FileField(upload_to='src/', blank=True, null=True)
    original_width = models.IntegerField(default=100)
    original_height = models.IntegerField(default=100)

    alt = models.CharField(max_length=128, default="Image Description")
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)


class Media(models.Model):
    width = models.FloatField()
    height = models.FloatField()

    media_content = models.ForeignKey(MediaContent, on_delete=models.CASCADE, default="")



class LayoutShapeRelation(models.Model):
    layout = models.ForeignKey(Layout, on_delete=models.CASCADE)
    shape = models.ForeignKey(Shape, on_delete=models.CASCADE)


