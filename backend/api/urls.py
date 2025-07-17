from django.urls import path
from .views import UploadLabReport
from .views import ReportListAPIView, ReportDeleteView
from django.conf import settings
from django.conf.urls.static import static
from .views import FirebaseLoginView
#endpoints
urlpatterns = [
    path('upload/', UploadLabReport.as_view(), name='upload-lab'),
    path('reports/', ReportListAPIView.as_view(), name='report-list'),
    path('reports/<int:pk>/', ReportDeleteView.as_view()),
    path('login/', FirebaseLoginView.as_view(), name='firebase-login'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
