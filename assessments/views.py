from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Avg
from django.views.decorators.csrf import csrf_protect
from datetime import datetime, timedelta
from .models import Question, QuestionOption, Assessment, ContactMessage
from .forms import SignUpForm, ContactForm, QuestionForm, QuestionOptionFormSet


def home(request):
    """Landing page"""
    return render(request, 'assessments/home.html')


@csrf_protect
def signup_view(request):
    """User registration"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'assessments/signup.html', {'form': form})


@csrf_protect
def login_view(request):
    """User login"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'assessments/login.html')


@login_required
def dashboard(request):
    """User dashboard with assessment history"""
    user_assessments = Assessment.objects.filter(user=request.user)[:10]
    
    # Calculate statistics
    total_assessments = user_assessments.count()
    if total_assessments > 0:
        avg_score = user_assessments.aggregate(Avg('total_score'))['total_score__avg']
        latest_assessment = user_assessments.first()
    else:
        avg_score = 0
        latest_assessment = None
    
    # Get category distribution for chart
    category_counts = user_assessments.values('overall_category').annotate(count=Count('id'))
    
    context = {
        'assessments': user_assessments,
        'total_assessments': total_assessments,
        'avg_score': round(avg_score, 1) if avg_score else 0,
        'latest_assessment': latest_assessment,
        'category_counts': list(category_counts),
    }
    
    return render(request, 'assessments/dashboard.html', context)


@login_required
@csrf_protect
def quiz_view(request):
    """Mental health assessment quiz"""
    questions = Question.objects.prefetch_related('options').all()
    
    if request.method == 'POST':
        # Calculate scores
        total_score = 0
        anxiety_score = 0
        depression_score = 0
        stress_score = 0
        general_score = 0
        
        answered_questions = 0
        
        for question in questions:
            answer_id = request.POST.get(f'question_{question.id}')
            if answer_id:
                try:
                    option = QuestionOption.objects.get(id=answer_id)
                    weight = option.weight
                    total_score += weight
                    
                    # Add to category-specific scores
                    if question.category == 'anxiety':
                        anxiety_score += weight
                    elif question.category == 'depression':
                        depression_score += weight
                    elif question.category == 'stress':
                        stress_score += weight
                    else:
                        general_score += weight
                    
                    answered_questions += 1
                except QuestionOption.DoesNotExist:
                    pass
        
        if answered_questions > 0:
            # Determine overall category
            max_possible = answered_questions * 4
            percentage = (total_score / max_possible) * 100
            
            if percentage < 25:
                category = 'low'
            elif percentage < 50:
                category = 'mild'
            elif percentage < 75:
                category = 'moderate'
            else:
                category = 'severe'
            
            # Save assessment
            assessment = Assessment.objects.create(
                user=request.user,
                total_score=total_score,
                anxiety_score=anxiety_score,
                depression_score=depression_score,
                stress_score=stress_score,
                general_score=general_score,
                overall_category=category
            )
            
            messages.success(request, 'Assessment completed successfully!')
            return redirect('result', assessment_id=assessment.id)
        else:
            messages.error(request, 'Please answer at least one question.')
    
    context = {
        'questions': questions,
    }
    return render(request, 'assessments/quiz.html', context)


@login_required
def result_view(request, assessment_id):
    """Display assessment result"""
    try:
        assessment = Assessment.objects.get(id=assessment_id, user=request.user)
        
        # Get recommendations based on category
        recommendations = get_recommendations(assessment.overall_category)
        
        context = {
            'assessment': assessment,
            'recommendations': recommendations,
        }
        return render(request, 'assessments/result.html', context)
    except Assessment.DoesNotExist:
        messages.error(request, 'Assessment not found.')
        return redirect('dashboard')


def get_recommendations(category):
    """Get personalized recommendations based on assessment category"""
    recommendations = {
        'low': [
            "You're doing great! Continue maintaining healthy habits.",
            "Regular exercise and good sleep are helping you stay balanced.",
            "Keep engaging in activities you enjoy.",
            "Consider helping others - it can boost your own well-being."
        ],
        'mild': [
            "Take some time for self-care activities.",
            "Practice mindfulness or meditation for 10 minutes daily.",
            "Maintain a regular sleep schedule.",
            "Stay connected with friends and family.",
            "Consider talking to a counselor or therapist."
        ],
        'moderate': [
            "It's important to prioritize your mental health.",
            "Seek support from a mental health professional.",
            "Practice stress-reduction techniques like deep breathing.",
            "Engage in regular physical activity.",
            "Consider joining a support group.",
            "Remember: seeking help is a sign of strength, not weakness."
        ],
        'severe': [
            "Your well-being is our priority. Please seek professional help immediately.",
            "Contact a mental health professional or crisis helpline.",
            "Speak with your doctor about your concerns.",
            "Reach out to trusted friends or family members.",
            "Remember: you are not alone, and help is available.",
            "In crisis? Call 988 (Suicide & Crisis Lifeline) or your local emergency services."
        ]
    }
    return recommendations.get(category, recommendations['mild'])


def guidance_view(request):
    """Guidance and support resources page"""
    helplines = [
        {
            'name': '988 Suicide & Crisis Lifeline',
            'number': '988',
            'description': 'Free, confidential support 24/7 for people in distress'
        },
        {
            'name': 'Crisis Text Line',
            'number': 'Text HOME to 741741',
            'description': 'Free, 24/7 crisis support via text message'
        },
        {
            'name': 'National Alliance on Mental Illness (NAMI)',
            'number': '1-800-950-NAMI',
            'description': 'Information, referrals, and support for mental health conditions'
        },
        {
            'name': 'SAMHSA National Helpline',
            'number': '1-800-662-4357',
            'description': 'Free, confidential treatment referral and information service'
        },
    ]
    
    resources = [
        {
            'title': 'BetterHelp',
            'description': 'Online counseling platform with licensed therapists',
            'link': 'https://www.betterhelp.com/',
            'type': 'Online Counseling'
        },
        {
            'title': 'Talkspace',
            'description': 'Therapy via text, audio, and video messaging',
            'link': 'https://www.talkspace.com/',
            'type': 'Online Counseling'
        },
        {
            'title': 'Mindfulness Apps',
            'description': 'Headspace, Calm, or Insight Timer for meditation',
            'link': 'https://www.headspace.com/',
            'type': 'Self-Help'
        },
        {
            'title': 'Psychology Today',
            'description': 'Find local therapists and mental health professionals',
            'link': 'https://www.psychologytoday.com/',
            'type': 'Therapist Directory'
        },
    ]
    
    tips = [
        "Practice deep breathing exercises for 5-10 minutes daily",
        "Maintain a regular sleep schedule (7-9 hours per night)",
        "Stay physically active - even a 15-minute walk helps",
        "Connect with others - social support is crucial",
        "Limit alcohol and avoid recreational drugs",
        "Eat a balanced diet rich in fruits and vegetables",
        "Take breaks from screens and social media",
        "Practice gratitude by writing down 3 things you're thankful for each day",
        "Set realistic goals and celebrate small achievements",
        "Don't hesitate to seek professional help when needed"
    ]
    
    context = {
        'helplines': helplines,
        'resources': resources,
        'tips': tips,
    }
    return render(request, 'assessments/guidance.html', context)


@csrf_protect
def contact_view(request):
    """Contact form for counselor inquiries"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'assessments/contact.html', {'form': form})


# Admin Panel Views
def is_staff_user(user):
    """Check if user is staff"""
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_staff_user)
def admin_dashboard(request):
    """Admin dashboard"""
    total_questions = Question.objects.count()
    total_messages = ContactMessage.objects.count()
    total_assessments = Assessment.objects.count()
    recent_messages = ContactMessage.objects.all()[:5]
    
    context = {
        'total_questions': total_questions,
        'total_messages': total_messages,
        'total_assessments': total_assessments,
        'recent_messages': recent_messages,
    }
    return render(request, 'assessments/admin/dashboard.html', context)


@login_required
@user_passes_test(is_staff_user)
def admin_questions(request):
    """List all questions"""
    questions = Question.objects.prefetch_related('options').all()
    context = {
        'questions': questions,
    }
    return render(request, 'assessments/admin/questions.html', context)


@login_required
@user_passes_test(is_staff_user)
@csrf_protect
def admin_add_question(request):
    """Add a new question with options"""
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        formset = QuestionOptionFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            question = form.save()
            formset.instance = question
            formset.save()
            messages.success(request, 'Question added successfully!')
            return redirect('admin_questions')
    else:
        form = QuestionForm()
        formset = QuestionOptionFormSet()
    
    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'assessments/admin/add_question.html', context)


@login_required
@user_passes_test(is_staff_user)
@csrf_protect
def admin_edit_question(request, question_id):
    """Edit an existing question"""
    question = get_object_or_404(Question, id=question_id)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = QuestionOptionFormSet(request.POST, instance=question)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Question updated successfully!')
            return redirect('admin_questions')
    else:
        form = QuestionForm(instance=question)
        formset = QuestionOptionFormSet(instance=question)
    
    context = {
        'form': form,
        'formset': formset,
        'question': question,
    }
    return render(request, 'assessments/admin/edit_question.html', context)


@login_required
@user_passes_test(is_staff_user)
@csrf_protect
def admin_delete_question(request, question_id):
    """Delete a question"""
    question = get_object_or_404(Question, id=question_id)
    
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted successfully!')
        return redirect('admin_questions')
    
    context = {
        'question': question,
    }
    return render(request, 'assessments/admin/delete_question.html', context)


@login_required
@user_passes_test(is_staff_user)
def admin_contact_messages(request):
    """View all contact messages"""
    messages_list = ContactMessage.objects.all()
    context = {
        'messages_list': messages_list,
    }
    return render(request, 'assessments/admin/contact_messages.html', context)


@login_required
@user_passes_test(is_staff_user)
def admin_view_message(request, message_id):
    """View a single contact message"""
    message = get_object_or_404(ContactMessage, id=message_id)
    context = {
        'message': message,
    }
    return render(request, 'assessments/admin/view_message.html', context)


@login_required
@user_passes_test(is_staff_user)
@csrf_protect
def admin_delete_message(request, message_id):
    """Delete a contact message"""
    message = get_object_or_404(ContactMessage, id=message_id)
    
    if request.method == 'POST':
        message.delete()
        messages.success(request, 'Message deleted successfully!')
        return redirect('admin_contact_messages')
    
    context = {
        'message': message,
    }
    return render(request, 'assessments/admin/delete_message.html', context)

