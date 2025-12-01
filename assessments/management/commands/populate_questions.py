"""
Management command to populate initial assessment questions
"""
from django.core.management.base import BaseCommand
from assessments.models import Question, QuestionOption


class Command(BaseCommand):
    help = 'Populates the database with initial mental health assessment questions'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating assessment questions...')
        
        questions_data = [
            {
                'text': 'How often have you felt nervous, anxious, or on edge over the past 2 weeks?',
                'category': 'anxiety',
                'options': [
                    ('Not at all', 0),
                    ('Several days', 1),
                    ('More than half the days', 2),
                    ('Nearly every day', 3),
                ]
            },
            {
                'text': 'How often have you been unable to stop or control worrying?',
                'category': 'anxiety',
                'options': [
                    ('Not at all', 0),
                    ('Several days', 1),
                    ('More than half the days', 2),
                    ('Nearly every day', 3),
                ]
            },
            {
                'text': 'How often have you felt down, depressed, or hopeless?',
                'category': 'depression',
                'options': [
                    ('Not at all', 0),
                    ('Several days', 1),
                    ('More than half the days', 2),
                    ('Nearly every day', 3),
                ]
            },
            {
                'text': 'How often have you had little interest or pleasure in doing things?',
                'category': 'depression',
                'options': [
                    ('Not at all', 0),
                    ('Several days', 1),
                    ('More than half the days', 2),
                    ('Nearly every day', 3),
                ]
            },
            {
                'text': 'How often have you felt that you were unable to cope with all the things you had to do?',
                'category': 'stress',
                'options': [
                    ('Never', 0),
                    ('Rarely', 1),
                    ('Sometimes', 2),
                    ('Often', 3),
                    ('Always', 4),
                ]
            },
            {
                'text': 'How often have you felt difficulties were piling up so high that you could not overcome them?',
                'category': 'stress',
                'options': [
                    ('Never', 0),
                    ('Rarely', 1),
                    ('Sometimes', 2),
                    ('Often', 3),
                    ('Always', 4),
                ]
            },
            {
                'text': 'How would you rate your overall sleep quality?',
                'category': 'general',
                'options': [
                    ('Excellent', 0),
                    ('Good', 1),
                    ('Fair', 2),
                    ('Poor', 3),
                ]
            },
            {
                'text': 'How often do you feel overwhelmed by daily responsibilities?',
                'category': 'stress',
                'options': [
                    ('Never', 0),
                    ('Rarely', 1),
                    ('Sometimes', 2),
                    ('Often', 3),
                ]
            },
            {
                'text': 'How often have you had trouble falling or staying asleep, or sleeping too much?',
                'category': 'general',
                'options': [
                    ('Not at all', 0),
                    ('Several days', 1),
                    ('More than half the days', 2),
                    ('Nearly every day', 3),
                ]
            },
            {
                'text': 'How often have you felt tired or had little energy?',
                'category': 'general',
                'options': [
                    ('Not at all', 0),
                    ('Several days', 1),
                    ('More than half the days', 2),
                    ('Nearly every day', 3),
                ]
            },
            {
                'text': 'How often have you had poor appetite or overeating?',
                'category': 'general',
                'options': [
                    ('Not at all', 0),
                    ('Several days', 1),
                    ('More than half the days', 2),
                    ('Nearly every day', 3),
                ]
            },
            {
                'text': 'How often have you felt bad about yourself or that you are a failure?',
                'category': 'depression',
                'options': [
                    ('Not at all', 0),
                    ('Several days', 1),
                    ('More than half the days', 2),
                    ('Nearly every day', 3),
                ]
            },
            {
                'text': 'How often have you had trouble concentrating on things?',
                'category': 'general',
                'options': [
                    ('Not at all', 0),
                    ('Several days', 1),
                    ('More than half the days', 2),
                    ('Nearly every day', 3),
                ]
            },
            {
                'text': 'How often do you experience physical symptoms like headaches, muscle tension, or stomach problems?',
                'category': 'stress',
                'options': [
                    ('Never', 0),
                    ('Rarely', 1),
                    ('Sometimes', 2),
                    ('Often', 3),
                ]
            },
            {
                'text': 'How satisfied are you with your social relationships?',
                'category': 'general',
                'options': [
                    ('Very satisfied', 0),
                    ('Satisfied', 1),
                    ('Somewhat satisfied', 2),
                    ('Not satisfied', 3),
                ]
            },
        ]
        
        created_count = 0
        for q_data in questions_data:
            question, created = Question.objects.get_or_create(
                text=q_data['text'],
                defaults={'category': q_data['category']}
            )
            
            if created:
                created_count += 1
                # Create options for this question
                for option_text, weight in q_data['options']:
                    QuestionOption.objects.create(
                        question=question,
                        text=option_text,
                        weight=weight
                    )
                self.stdout.write(self.style.SUCCESS(f'Created question: {question.text[:50]}...'))
        
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {created_count} new questions!'))
        self.stdout.write(f'Total questions in database: {Question.objects.count()}')



