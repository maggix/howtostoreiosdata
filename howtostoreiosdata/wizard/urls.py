from django.conf.urls import patterns, url
from .views import QuestionStorageView, QuestionBackgroundView, QuestionSharingView, ResultView

urlpatterns = patterns('',
    url(r'^storage/$', QuestionStorageView.as_view(), name="question_storage"),
    url(r'^background/$', QuestionBackgroundView.as_view(), name="question_background"),
    url(r'^sharing/$', QuestionSharingView.as_view(), name="question_sharing"),
    url(r'^result/$', ResultView.as_view(), name="result"),
)