from django.contrib import admin
from .models import Rectangle, Circle, Media, Shape, Layout, Template, LayoutShapeRelation, Text, MediaContent
from django.contrib.auth.models import User

# Register your models here.

admin.site.register(Template)
admin.site.register(Layout)
admin.site.register(Shape)
admin.site.register(Rectangle)
admin.site.register(Circle)
admin.site.register(Text)
admin.site.register(Media)
admin.site.register(MediaContent)
admin.site.register(LayoutShapeRelation)



