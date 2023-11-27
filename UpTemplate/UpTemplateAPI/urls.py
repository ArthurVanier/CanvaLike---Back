from django.contrib import admin
from .views import UserView, TemplateView, ShapeShadowView, ShapePropsView, ShapeView, RectangleView, CircleView, MediaView
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserView)
router.register(r'templates', TemplateView)
router.register(r'shapes', ShapeView)
router.register(r'shape_props', ShapePropsView)
router.register(r'shape_shadows', ShapeShadowView)
router.register(r'rectangles', RectangleView)
router.register(r'circles', CircleView)
router.register(r'medias', MediaView)


urlpatterns = [
    path('', include(router.urls))
]
