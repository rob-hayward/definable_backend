# definable_backend_app urls.py
from django.urls import path
from .views import CreateDefinableView, DefinableDetailView, DefinableDictionaryView, DefinitionVoteView, WordVoteView, \
    CurrentUserView

urlpatterns = [
    path('create_definable/', CreateDefinableView.as_view(), name='create_definable'),
    path('current_user/', CurrentUserView.as_view(), name='current_user'),
    path('definable_dictionary/', DefinableDictionaryView.as_view(), name='definable_dictionary'),
    path('definable_detail/<int:pk>/', DefinableDetailView.as_view(), name='definable_detail'),
    path('definition_vote/<int:definition_id>/', DefinitionVoteView.as_view(), name='definition_vote'),
    path('word_vote/<int:word_id>/', WordVoteView.as_view(), name='word_vote'),
]
