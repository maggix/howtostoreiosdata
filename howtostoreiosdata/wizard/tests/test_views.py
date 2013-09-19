from django.conf import settings
from django.core.urlresolvers import reverse_lazy, reverse
from django.test import TestCase
from django.utils.importlib import import_module
from howtostoreiosdata.wizard.views import QuestionStorageView, QuestionBackgroundView, QuestionSharingView
from howtostoreiosdata.wizard.recommendation import RecommendationEngine


class StartViewTest(TestCase):
    url = reverse_lazy('wizard:start')

    def test_render(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class QuestionViewsTest(TestCase):

    def test_storage_question(self):
        self._test_question('wizard:question_storage', QuestionStorageView)

    def test_backgorund_question(self):
        self._test_question('wizard:question_background', QuestionBackgroundView)

    def test_sharing_question(self):
        self._test_question('wizard:question_sharing', QuestionSharingView)

    def _test_question(self, url_name, view_class):
        url = reverse(url_name)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        answer = 'foo'
        response = self.client.get(url, {'answer': answer})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session[view_class.question_short_name], answer)


class ResultViewTest(TestCase):
    url = reverse_lazy('wizard:result')

    def test_render(self):
        # https://code.djangoproject.com/ticket/10899
        from django.conf import settings
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

        session = self.client.session
        session[QuestionStorageView.question_short_name] = RecommendationEngine.STORAGE_CORE_DATA
        session[QuestionBackgroundView.question_short_name] = RecommendationEngine.BACKGROUND_OPEN_ONLY
        session[QuestionSharingView.question_short_name] = 'NO'
        session.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'NSFileProtectionCompleteUnlessOpen')

