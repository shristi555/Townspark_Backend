from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, 
    DepartmentViewSet, 
    StatusOptionsView, 
    UrgencyLevelsView,
    PlatformStatsView
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'departments', DepartmentViewSet, basename='department')

urlpatterns = [
    path('', include(router.urls)),
    path('status-options/', StatusOptionsView.as_view(), name='status-options'),
    path('urgency-levels/', UrgencyLevelsView.as_view(), name='urgency-levels'),
    path('platform/stats/', PlatformStatsView.as_view(), name='platform-stats'),
]
