# tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Word, Definition, WordStatus, DefinitionStatus

class WordModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.word = Word.objects.create(word='test')

    def test_word_creation(self):
        self.assertEqual(self.word.word, 'test')
        self.assertEqual(self.word.status, WordStatus.PENDING.value)
        self.assertEqual(self.word.positive_votes, 0)
        self.assertEqual(self.word.negative_votes, 0)
        self.assertEqual(self.word.total_votes, 0)

    def test_word_str_representation(self):
        self.assertEqual(str(self.word), 'test')

class DefinitionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.word = Word.objects.create(word='test')
        self.definition = Definition.objects.create(
            word=self.word,
            definition_text='A test definition'
        )

    def test_definition_creation(self):
        self.assertEqual(self.definition.word, self.word)
        self.assertEqual(self.definition.definition_text, 'A test definition')
        self.assertEqual(self.definition.definition_status, DefinitionStatus.ALTERNATIVE.value)
        self.assertEqual(self.definition.total_votes, 0)

    def test_definition_str_representation(self):
        expected_str = 'test: A test definition'
        self.assertEqual(str(self.definition), expected_str)