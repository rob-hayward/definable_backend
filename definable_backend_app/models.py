# models.py
from django.db import models, transaction
from django.contrib.auth.models import User
from enum import Enum
from django.db.models import Count
from django.db.models.signals import pre_save
from django.dispatch import receiver


class WordVoteType(Enum):
    POSITIVE = 1
    NEGATIVE = -1
    NO_VOTE = 0

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

    @classmethod
    def default(cls):
        return cls.NO_VOTE.value


class WordStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class DefinitionStatus(Enum):
    LIVE = "live"
    ALTERNATIVE = "alternative"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Word(models.Model):
    word = models.CharField(max_length=200, unique=True)
    live_definition = models.ForeignKey('Definition', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    positive_votes = models.PositiveIntegerField(default=0)
    negative_votes = models.PositiveIntegerField(default=0)
    total_votes = models.PositiveIntegerField(default=0)
    positive_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    negative_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=WordStatus.choices(), default=WordStatus.PENDING.value)
    created_at = models.DateTimeField(auto_now_add=True)

    def update_votes(self):
        vote_data = WordVote.objects.filter(word=self).aggregate(
            positive_votes=Count('id', filter=models.Q(vote_type=WordVoteType.POSITIVE.value)),
            negative_votes=Count('id', filter=models.Q(vote_type=WordVoteType.NEGATIVE.value)),
        )
        self.positive_votes = vote_data['positive_votes']
        self.negative_votes = vote_data['negative_votes']
        self.total_votes = self.positive_votes + self.negative_votes
        self.positive_percentage = round((self.positive_votes / self.total_votes) * 100,
                                         2) if self.total_votes > 0 else 0
        self.negative_percentage = round((self.negative_votes / self.total_votes) * 100,
                                         2) if self.total_votes > 0 else 0
        self.save()

    def update_definitions_status(self):
        with transaction.atomic():
            ordered_definitions = self.definition_set.order_by('-total_votes', 'created_at')

            for i, definition in enumerate(ordered_definitions):
                if i == 0:
                    definition.definition_status = DefinitionStatus.LIVE.value
                    self.live_definition = definition
                else:
                    definition.definition_status = DefinitionStatus.ALTERNATIVE.value
                definition.save(update_fields=['definition_status'])

            self.save(update_fields=['live_definition'])

    def __str__(self):
        return self.word


@receiver(pre_save, sender=Word)
def update_word_status(sender, instance, **kwargs):
    # Define the criteria for approving or rejecting a word
    if instance.positive_votes > instance.negative_votes:
        instance.status = WordStatus.APPROVED.value
    elif instance.negative_votes > instance.positive_votes:
        instance.status = WordStatus.REJECTED.value
    else:
        instance.status = WordStatus.PENDING.value


class WordVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    vote_type = models.IntegerField(choices=WordVoteType.choices(), default=WordVoteType.default())
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'word']


class Definition(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    definition_text = models.TextField()
    definition_status = models.CharField(max_length=20, choices=DefinitionStatus.choices(), default=DefinitionStatus.ALTERNATIVE.value)
    total_votes = models.PositiveIntegerField(default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def update_votes(self):
        self.total_votes = self.votes.count()
        self.save()
        self.word.update_definitions_status()

    def get_user_vote(self, user):
        return 'Voted' if DefinitionVote.objects.filter(definition=self, user=user).exists() else 'Not Voted'

    def __str__(self):
        return f"{self.word}: {self.definition_text[:50]}"


class DefinitionVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    definition = models.ForeignKey(Definition, on_delete=models.CASCADE, related_name='votes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'definition']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.definition.update_votes()

    def delete(self, *args, **kwargs):
        definition = self.definition
        super().delete(*args, **kwargs)
        definition.update_votes()

