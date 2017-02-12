from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from . import models


def token_required(func):
    def _wrap(request, store_id, *args, **kwargs):
        store = models.Store.objects.get(pk=store_id)
        tokens = store.token_set.all()
        if tokens.count():
            try:
                token_id = request.GET.get('token')
                tokens.get(pk=token_id)
            except models.Token.DoesNotExist:
                return not_authorized()
        return func(request, store_id, *args, **kwargs)
    return _wrap


def not_authorized():
    return JsonResponse({'error': 'Not authorized.'}, status=403)


def not_found():
    return JsonResponse({'error': 'Not found.'}, status=404)


class StoreListView(View):

    def get(self, request):
        stores = models.Store.objects.count()
        values = models.Value.objects.count()
        return JsonResponse({'stores': stores, 'values': values})

    @method_decorator(csrf_exempt)
    def post(self, request):
        store = models.Store()
        store.save()
        return JsonResponse({'store': store.id})


class StoreDetailView(View):

    def get(self, request, store_id):
        try:
            store = models.Store.objects.get(pk=store_id)
        except models.Store.DoesNotExist:
            return not_found()
        return JsonResponse({
            'store': store.id,
            'tokens': [token.id for token in store.token_set.all()],
            'values': dict((value.key, value.value)
                           for value in store.value_set.all()),
        })

    @method_decorator(token_required)
    def delete(self, request, store_id):
        try:
            models.Store.objects.get(pk=store_id).delete()
        except models.Store.DoesNotExist:
            return not_found()
        return JsonResponse({})


class ValueDetailView(View):

    def get(self, request, store_id, key):
        try:
            value = models.Value.objects.get(store_id=store_id, key=key)
        except (models.Store.DoesNotExist, models.Value.DoesNotExist):
            return not_found()
        return JsonResponse({'value': value.value})

    @method_decorator(token_required)
    def post(self, request, store_id, key):
        try:
            store = models.Store.objects.get(pk=store_id)
        except (models.Store.DoesNotExist):
            return not_found()
        value = request.POST['value']
        value, created = models.Value.objects.get_or_create(
            store=store, key=key, defaults={'value': value})
        if not created:
            value.value = request.POST['value']
            value.save()
        return JsonResponse({'value': value.value})

    @method_decorator(token_required)
    def delete(self, request, store_id, key):
        try:
            models.Value.objects.get(store_id=store_id, key=key).delete()
        except models.Value.DoesNotExist:
            return not_found()
        return JsonResponse({})


class TokenListView(View):

    @method_decorator(token_required)
    def get(self, request, store_id):
        tokens = models.Token.objects.filter(store_id=store_id)
        tokens = [token.id for token in tokens]
        return JsonResponse({'tokens': tokens})

    @method_decorator(token_required)
    def post(self, request, store_id):
        token = models.Token(store_id=store_id)
        token.save()
        return JsonResponse({'token': token.id})


class TokenDetailView(View):

    def delete(self, request, store_id, token_id):
        try:
            token = models.Token.objects.get(store_id=store_id, pk=token_id)
        except models.Token.DoesNotExist:
            return not_found()
        token.delete()
        return JsonResponse({})
