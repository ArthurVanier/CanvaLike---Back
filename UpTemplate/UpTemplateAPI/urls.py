from django.contrib import admin
from .views import UserView, TemplateView, LayoutView, ShapeView, RectangleView, CircleView, MediaContentView
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

router = DefaultRouter()
router.register(r'users', UserView)
router.register(r'templates', TemplateView)

template_router = routers.NestedSimpleRouter(router, r'templates', lookup='template')
template_router.register(r'layouts', LayoutView, basename="template-layout")

layout_router = routers.NestedSimpleRouter(template_router, r'layouts', lookup='layout')
layout_router.register(r'shapes', ShapeView, basename="layout-shape")


router.register(r'rectangles', RectangleView)
router.register(r'circles', CircleView)
router.register(r'medias', MediaContentView)


urlpatterns = urlpatterns = router.urls + template_router.urls + layout_router.urls
