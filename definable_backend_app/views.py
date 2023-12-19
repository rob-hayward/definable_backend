# views.py
from rest_framework import generics, status as http_status
from rest_framework.response import Response
from .models import Word, Definition, DefinitionVote, DefinitionStatus, WordVote, WordVoteType
from .serializers import WordSerializer, DefinitionSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView
from django.db.models import F
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer


class CurrentUserView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user



class WordVoteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, word_id):
        user = request.user
        word = get_object_or_404(Word, id=word_id)
        vote_type = request.data.get('vote_type', WordVoteType.NO_VOTE.value)

        # Check if the user has already voted on this word
        word_vote, created = WordVote.objects.get_or_create(user=user, word=word, defaults={'vote_type': vote_type})

        if not created:
            if word_vote.vote_type != vote_type:
                # Update the existing vote
                word_vote.vote_type = vote_type
                word_vote.save()
            else:
                return Response({"message": "You have already voted."}, status=http_status.HTTP_400_BAD_REQUEST)

        # Update the word vote statistics
        word.update_votes()

        return Response({"message": "Vote registered successfully"}, status=http_status.HTTP_200_OK)


class DefinableDetailView(RetrieveAPIView):
    queryset = Word.objects.all()
    serializer_class = WordSerializer

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        word = self.get_object()

        # Retrieve the sort parameter, defaulting to 'most_popular'
        sort_by = request.query_params.get('sort_by', 'most_popular')

        # Get the user's votes, if authenticated
        user_word_vote, user_definition_vote = self.get_user_votes(request.user, word)

        # Sort the definitions as per the user's choice
        sorted_definitions = self.get_sorted_definitions(word, sort_by)

        # Add additional data to the response
        response.data['user_word_vote'] = user_word_vote
        response.data['user_vote'] = {'definition_id': user_definition_vote} if user_definition_vote else None
        response.data['definitions'] = sorted_definitions

        return response

    def get_user_votes(self, user, word):
        if user.is_authenticated:
            user_word_vote_query = WordVote.objects.filter(user=user, word=word).first()
            user_word_vote = user_word_vote_query.vote_type if user_word_vote_query else WordVoteType.NO_VOTE.value

            user_definition_vote_query = DefinitionVote.objects.filter(user=user, definition__word=word).first()
            user_definition_vote = user_definition_vote_query.definition_id if user_definition_vote_query else None
        else:
            user_word_vote = WordVoteType.NO_VOTE.value
            user_definition_vote = None

        return user_word_vote, user_definition_vote

    def get_sorted_definitions(self, word, sort_by):
        definitions = Definition.objects.filter(word=word).exclude(id=word.live_definition_id)
        if sort_by == 'oldest_first':
            definitions = definitions.order_by('created_at')
        elif sort_by == 'newest_first':
            definitions = definitions.order_by('-created_at')
        else:
            definitions = definitions.order_by('-total_votes', 'created_at')

        return DefinitionSerializer(definitions, many=True).data


class DefinitionVoteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, definition_id):
        user = request.user
        definition = get_object_or_404(Definition, id=definition_id)

        # Check if the user has already voted on a different definition for the same word
        existing_vote = DefinitionVote.objects.filter(user=user, definition__word=definition.word).first()
        if existing_vote:
            existing_vote.delete()  # This will update the vote count automatically

        # Create the new vote
        DefinitionVote.objects.create(user=user, definition=definition)
        definition.word.update_definitions_status()

        return Response({"message": "Vote registered successfully"})


class DefinableDictionaryView(generics.ListAPIView):
    serializer_class = WordSerializer

    def get_queryset(self):
        sort_by = self.request.query_params.get('sort_by', 'alphabetical')
        status_filter = self.request.query_params.get('status', 'approved')

        queryset = Word.objects.filter(status=status_filter)

        if sort_by == 'popularity':
            queryset = queryset.order_by('-total_votes')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'oldest':
            queryset = queryset.order_by('created_at')
        else:  # Default to alphabetical
            queryset = queryset.order_by('word')

        return queryset


class CreateDefinableView(generics.CreateAPIView):
    serializer_class = DefinitionSerializer

    def create(self, request, *args, **kwargs):
        word_text = request.data.get('word', '').strip()
        definition_text = request.data.get('definition_text', '').strip()

        if not word_text or not definition_text:
            return Response({'detail': 'Both word and definition text are required.'},
                            status=http_status.HTTP_400_BAD_REQUEST)

        word, created = Word.objects.get_or_create(word=word_text)

        # Check if status is provided, otherwise default to ALTERNATIVE
        definition_status = request.data.get('status', DefinitionStatus.ALTERNATIVE.value)
        definition = Definition.objects.create(word=word, definition_text=definition_text,
                                               definition_status=definition_status)

        if created:  # If this is the first definition, set it as the live definition.
            word.live_definition = definition
            word.save()

        return Response(WordSerializer(word).data, status=http_status.HTTP_201_CREATED)

