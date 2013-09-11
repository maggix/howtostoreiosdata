from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from .models import Recommendation


class QuestionView(TemplateView):
    template_name = "wizard/question.html"

    def get(self, request, *args, **kwargs):
        if 'answer' in request.GET:
            answer = request.GET['answer']
            request.session[self.question_short_name] = answer
            return HttpResponseRedirect(reverse(self.get_next_view(answer)))
        else:
            context = {
                'question': self.question,
                'options': self.options,
            }
            return self.render_to_response(context)

    def get_next_view(self, answer):
        return self.next_view


class QuestionStorageView(QuestionView):
    question = "How are you storing or planning to store your data?"
    question_short_name = 'question_storage'
    next_view = 'wizard:question_background'
    options = (
        (Recommendation.STORAGE.core_data, 'Core Data'),
        (Recommendation.STORAGE.defaults, 'NSUserDefaults'),
        (Recommendation.STORAGE.rawsql, 'Raw SQLite/FMDB database'),
        (Recommendation.STORAGE.raw_data, 'Raw NSData files'),
        (Recommendation.STORAGE.keychain, 'Keychain'),
    )


class QuestionBackgroundView(QuestionView):
    question = "Does your app need to run in the bakground?"
    question_short_name = 'question_background'
    next_view = 'wizard:question_sharing'
    options = (
        ('NO', 'No'),
        ('YES', 'Yes'),
        ('OPENONLY', 'Yes, but only for finishing work on open files, like finishing a download.'),
    )


class QuestionSharingView(QuestionView):
    question = "Do you need to share your sensitive data with your other apps?"
    question_short_name = 'question_sharing'
    next_view = 'wizard:result'
    options = (
        ('YES', 'Yes'),
        ('NO', 'No'),
    )


class ResultView(TemplateView):
    template_name = "wizard/result.html"

    def get_context_data(self, **kwargs):
        context = super(ResultView, self).get_context_data(**kwargs)

        background = self.request.session['question_background']
        storage = self.request.session['question_storage']
        sharing = self.request.session['question_sharing'] == 'YES'
        recommended_storage = self.recommended_storage(storage, sharing)
        recommended_protection_level = self.recommended_protection_level(background, recommended_storage)
        recommendation = Recommendation(storage=recommended_storage, protection_level=recommended_protection_level)
        context.update({
            'chosen_background': background,
            'chosen_storage': storage,
            'chosen_sharing': sharing,
            'recommendation': recommendation,
        })
        return context

    def recommended_storage(self, storage, sharing):
        if storage == Recommendation.STORAGE.defaults:
            return Recommendation.STORAGE.keychain
        if sharing:
            return Recommendation.STORAGE.keychain
        return storage

    def recommended_protection_level(self, background, storage):
        if background == 'YES':
            return Recommendation.PROTECTION_LEVEL.after_first_unlock
        if background == 'NO':
            return Recommendation.PROTECTION_LEVEL.always

        if background == 'OPENONLY':
            if storage == Recommendation.STORAGE.keychain:
                return Recommendation.PROTECTION_LEVEL.after_first_unlock
            else:
                return Recommendation.PROTECTION_LEVEL.unless_open
