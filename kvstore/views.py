from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from . import models


class TextResponse(HttpResponse):

    def __init__(self, *args, **kwargs):
        kwargs['content_type'] = 'text/plain'
        super(TextResponse, self).__init__(*args, **kwargs)


def token_required(func):
    def _wrap(request, store_id, *args, **kwargs):
        store = models.Store.objects.get(pk=store_id)
        tokens = store.token_set.all()
        if tokens.count():
            try:
                tokens.get(pk=request.META['HTTP_X_TOKEN'])
            except (KeyError, models.Token.DoesNotExist):
                raise PermissionDenied
        return func(request, store_id, *args, **kwargs)
    return _wrap


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
        store = get_object_or_404(models.Store, pk=store_id)
        return JsonResponse({
            'store': store.id,
            'tokens': [token.id for token in store.token_set.all()],
            'values': dict((value.key, value.value)
                           for value in store.value_set.all()),
        })

    @method_decorator(token_required)
    def delete(self, request, store_id):
        get_object_or_404(models.Store, pk=store_id).delete()
        return JsonResponse({})


class ValueDetailView(View):

    def get(self, request, store_id, key):
        value = get_object_or_404(models.Value, store_id=store_id, key=key)
        return TextResponse(value.value)

    @method_decorator(token_required)
    def post(self, request, store_id, key):
        store = get_object_or_404(models.Store, pk=store_id)
        value = request.body
        value, created = models.Value.objects.get_or_create(
            store=store, key=key, defaults={'value': value})
        if not created:
            value.value = request.body
            value.save()
        return JsonResponse({'value': value.value})

    @method_decorator(token_required)
    def delete(self, request, store_id, key):
        get_object_or_404(models.Value, store_id=store_id, key=key).delete()
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
        get_object_or_404(models.Token, store_id=store_id,
                          pk=token_id).delete()
        return JsonResponse({})
