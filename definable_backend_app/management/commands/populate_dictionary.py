from django.core.management.base import BaseCommand
import json
from definable_backend_app.models import Word, Definition, WordVote, DefinitionVote, WordStatus, DefinitionStatus, \
    WordVoteType
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Populates the database with a sample dictionary'

    def handle(self, *args, **kwargs):
        with open('sample_dictionary.json', 'r') as file:
            data = json.load(file)

        rob_user = User.objects.get(username='rob')

        for letter, words in data.items():
            for word_text, definition_text in words:
                # Check if the word already exists
                word, created = Word.objects.get_or_create(
                    word=word_text,
                    defaults={
                        'status': WordStatus.APPROVED.value
                    }
                )

                if created:
                    definition = Definition.objects.create(
                        word=word,
                        definition_text=definition_text,
                        definition_status=DefinitionStatus.LIVE.value
                    )
                    WordVote.objects.create(user=rob_user, word=word, vote_type=WordVoteType.POSITIVE.value)
                    DefinitionVote.objects.create(user=rob_user, definition=definition)

                    # Update word votes and status
                    word.update_votes()
                    word.update_definitions_status()

        self.stdout.write(self.style.SUCCESS('Successfully populated the dictionary'))
