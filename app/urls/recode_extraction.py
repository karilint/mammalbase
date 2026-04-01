from django.urls import path

from recode_extraction import views

urlpatterns = [
    path('sources/', views.source_document_list, name='recode_source_document_list'),
    path('sources/upload/', views.source_document_upload, name='recode_source_document_upload'),
    path('sources/<int:pk>/', views.source_document_detail, name='recode_source_document_detail'),
    path('sources/<int:pk>/run/', views.source_document_run_extraction, name='recode_source_document_run'),
    path('runs/<int:run_id>/', views.extraction_run_detail, name='recode_extraction_run_detail'),
]
