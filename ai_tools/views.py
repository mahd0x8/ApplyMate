from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from .models import FormAnswer
from profiles.models import UserProfile


@login_required
def ai_tools_home(request):
    from applications.models import JobApplication
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    recent_answers = FormAnswer.objects.filter(user=request.user)[:5]
    user_apps = JobApplication.objects.filter(user=request.user)
    return render(request, 'ai_tools/home.html', {
        'profile': profile,
        'recent_answers': recent_answers,
        'user_apps': user_apps,
    })


@login_required
@require_POST
def form_assistant(request):
    question = request.POST.get('question', '').strip()
    length_mode = request.POST.get('length_mode', 'medium')
    tone = request.POST.get('tone', 'balanced')

    if not question:
        return HttpResponse('<div class="error-msg">Please enter a question.</div>', status=400)

    try:
        from .claude_client import answer_form_question
        profile = getattr(request.user, 'profile', None)
        answer = answer_form_question(question, profile, length_mode, tone)
        fa = FormAnswer.objects.create(
            user=request.user,
            question=question,
            answer=answer,
            length_mode=length_mode,
            tone=tone,
        )
        if request.headers.get('HX-Request'):
            return render(request, 'components/form_answer.html', {'fa': fa})
    except Exception as e:
        if request.headers.get('HX-Request'):
            return HttpResponse(f'<div class="error-msg">Error: {str(e)}</div>', status=500)

    return redirect('ai_tools')


@login_required
@require_POST
def analyze_jd(request):
    job_description = request.POST.get('job_description', '').strip()
    if not job_description:
        return HttpResponse('<div class="error-msg">Please enter a job description.</div>', status=400)

    try:
        from .claude_client import analyze_job_description
        profile = getattr(request.user, 'profile', None)
        result = analyze_job_description(job_description, profile)
        if request.headers.get('HX-Request'):
            return render(request, 'components/jd_analysis.html', {'result': result})
    except Exception as e:
        if request.headers.get('HX-Request'):
            return HttpResponse(f'<div class="error-msg">Error: {str(e)}</div>', status=500)

    return redirect('ai_tools')


@login_required
@require_POST
def interview_prep(request):
    from applications.models import JobApplication
    app_id = request.POST.get('app_id')
    app = None
    if app_id:
        try:
            app = JobApplication.objects.get(pk=app_id, user=request.user)
        except JobApplication.DoesNotExist:
            pass

    if not app:
        return HttpResponse('<div class="error-msg">Application not found.</div>', status=400)

    try:
        from .claude_client import generate_interview_questions
        questions = generate_interview_questions(app)
        if request.headers.get('HX-Request'):
            return render(request, 'components/interview_questions.html', {'questions': questions, 'app': app})
    except Exception as e:
        if request.headers.get('HX-Request'):
            return HttpResponse(f'<div class="error-msg">Error: {str(e)}</div>', status=500)

    return redirect('ai_tools')


@login_required
@require_POST
def follow_up_email(request):
    from applications.models import JobApplication
    app_id = request.POST.get('app_id')
    email_type = request.POST.get('email_type', 'follow_up')
    app = None
    if app_id:
        try:
            app = JobApplication.objects.get(pk=app_id, user=request.user)
        except JobApplication.DoesNotExist:
            pass

    if not app:
        return HttpResponse('<div class="error-msg">Application not found.</div>', status=400)

    try:
        from .claude_client import generate_follow_up_email
        email_content = generate_follow_up_email(app, email_type)
        if request.headers.get('HX-Request'):
            return render(request, 'components/email_preview.html', {'email_content': email_content, 'app': app})
    except Exception as e:
        if request.headers.get('HX-Request'):
            return HttpResponse(f'<div class="error-msg">Error: {str(e)}</div>', status=500)

    return redirect('ai_tools')
