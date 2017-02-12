import uuid

from django.db import models


class Store(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store)

    class Meta:
        unique_together = (('id', 'store'),)


class Value(models.Model):
    store = models.ForeignKey(Store)
    key = models.CharField(max_length=255)
    value = models.TextField()

    class Meta:
        unique_together = (('store', 'key'),)
