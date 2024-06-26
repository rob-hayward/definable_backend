# Generated by Django 4.2.8 on 2023-12-19 14:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Definition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('definition_text', models.TextField()),
                ('definition_status', models.CharField(choices=[('live', 'LIVE'), ('alternative', 'ALTERNATIVE')], default='alternative', max_length=20)),
                ('total_votes', models.PositiveIntegerField(default=0, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=200, unique=True)),
                ('positive_votes', models.PositiveIntegerField(default=0)),
                ('negative_votes', models.PositiveIntegerField(default=0)),
                ('total_votes', models.PositiveIntegerField(default=0)),
                ('positive_percentage', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('negative_percentage', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('status', models.CharField(choices=[('pending', 'PENDING'), ('approved', 'APPROVED'), ('rejected', 'REJECTED')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('live_definition', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='definable_backend_app.definition')),
            ],
        ),
        migrations.AddField(
            model_name='definition',
            name='word',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='definable_backend_app.word'),
        ),
        migrations.CreateModel(
            name='WordVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote_type', models.IntegerField(choices=[(1, 'POSITIVE'), (-1, 'NEGATIVE'), (0, 'NO_VOTE')], default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='definable_backend_app.word')),
            ],
            options={
                'unique_together': {('user', 'word')},
            },
        ),
        migrations.CreateModel(
            name='DefinitionVote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('definition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='definable_backend_app.definition')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'definition')},
            },
        ),
    ]
