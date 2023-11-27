from django.contrib import admin
from .models import Rectangle, Circle, Media, Shape, ShapeProps, ShapeShadow, Template

# Register your models here.

admin.site.register(Template)
admin.site.register(Shape)
admin.site.register(ShapeProps)
admin.site.register(ShapeShadow)
admin.site.register(Rectangle)
admin.site.register(Circle)
admin.site.register(Media)

