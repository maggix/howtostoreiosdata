from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from .recommendation import RecommendationEngine


class StartView(TemplateView):
    template_name = "wizard/start.html"


class QuestionView(TemplateView):
    template_name = "wizard/question.html"

    def get(self, request, *args, **kwargs):
        if 'answer' in request.GET:
            answer = request.GET['answer']
            request.session[self.question_short_name] = answer
            return HttpResponseRedirect(reverse(self.next_view))
        else:
            context = {
                'question': self.question,
                'options': self.options,
            }
            return self.render_to_response(context)


class QuestionStorageView(QuestionView):
    question = "How are you storing or planning to store your data?"
    question_short_name = 'question_storage'
    next_view = 'wizard:question_background'
    options = (
        (RecommendationEngine.STORAGE_CORE_DATA, 'Core Data'),
        (RecommendationEngine.STORAGE_DEFAULTS, 'NSUserDefaults'),
        (RecommendationEngine.STORAGE_SQL, 'Raw SQLite database'),
        (RecommendationEngine.STORAGE_RAW_DATA, 'Raw NSData files'),
        (RecommendationEngine.STORAGE_KEYCHAIN, 'Keychain'),
    )


class QuestionBackgroundView(QuestionView):
    question = "Does your app need to run in the background?"
    question_short_name = 'question_background'
    next_view = 'wizard:question_sharing'
    options = (
        (RecommendationEngine.BACKGROUND_NONE, 'No, not at all'),
        (RecommendationEngine.BACKGROUND_ALWAYS, 'Yes, all the time'),
        (RecommendationEngine.BACKGROUND_OPEN_ONLY, 'Yes, but only for finishing work on open files'),
    )


class QuestionSharingView(QuestionView):
    question = "Do you need to share your sensitive data with your other apps?"
    question_short_name = 'question_sharing'
    next_view = 'wizard:result'
    options = (
        ('NO', 'No, the data will only be used by my app'),
        ('YES', 'Yes, my other apps will use this data too'),
    )


class ResultView(TemplateView):
    template_name = "wizard/result.html"

    def get_context_data(self, **kwargs):
        context = super(ResultView, self).get_context_data(**kwargs)
        background = self.request.session['question_background']
        storage = self.request.session['question_storage']
        sharing = self.request.session['question_sharing'] == 'YES'

        recommendation = RecommendationEngine(storage, background, sharing)
        context.update({
            'chosen_background': background,
            'chosen_storage': storage,
            'chosen_sharing': sharing,
            'recommendation': recommendation,
        })
        return context
