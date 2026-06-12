import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.utils import timezone
from .models import JobApplication, ChatMessage, GeneratedDocument
from profiles.models import UserProfile


PALETTE = ['#10B981', '#EC4899', '#8B5CF6', '#0EA5A4', '#F59E0B', '#22C55E', '#3B82F6', '#A855F7']


@login_required
def application_list(request):
    apps = JobApplication.objects.filter(user=request.user)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'applications/list.html', {'apps': apps, 'profile': profile})


@login_required
def application_detail(request, pk):
    app = get_object_or_404(JobApplication, pk=pk, user=request.user)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    messages = app.chat_messages.all()
    documents = app.documents.all()
    return render(request, 'applications/detail.html', {
        'app': app,
        'profile': profile,
        'messages': messages,
        'documents': documents,
    })


@login_required
@require_POST
def application_create(request):
    data = request.POST
    import random
    color = random.choice(PALETTE)
    app = JobApplication.objects.create(
        user=request.user,
        company=data.get('company', '').strip(),
        role=data.get('role', '').strip(),
        location=data.get('location', '').strip() or 'Remote',
        status=data.get('status', 'wishlist'),
        job_description=data.get('job_description', '').strip(),
        job_url=data.get('job_url', '').strip(),
        hiring_manager=data.get('hiring_manager', '').strip(),
        source=data.get('source', 'other'),
        work_mode=data.get('work_mode', ''),
        color=color,
    )
    if request.headers.get('HX-Request'):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        return render(request, 'components/kanban_card.html', {'card': app, 'profile': profile})
    return redirect('dashboard')


@login_required
@require_POST
def application_move(request, pk):
    app = get_object_or_404(JobApplication, pk=pk, user=request.user)
    new_status = request.POST.get('status')
    if new_status in dict(JobApplication.STATUS_CHOICES):
        app.status = new_status
        if new_status == 'applied' and not app.applied_at:
            app.applied_at = timezone.now().date()
        app.save()
    if request.headers.get('HX-Request'):
        return HttpResponse(status=200)
    return redirect('dashboard')


@login_required
@require_POST
def application_delete(request, pk):
    app = get_object_or_404(JobApplication, pk=pk, user=request.user)
    app.delete()
    if request.headers.get('HX-Request'):
        return HttpResponse(status=200)
    return redirect('dashboard')


@login_required
@require_POST
def application_update(request, pk):
    app = get_object_or_404(JobApplication, pk=pk, user=request.user)
    fields = ['company', 'role', 'location', 'job_description', 'job_url',
              'hiring_manager', 'notes', 'status', 'source', 'work_mode']
    for field in fields:
        if field in request.POST:
            setattr(app, field, request.POST[field])
    for field in ['salary_min', 'salary_max']:
        val = request.POST.get(field, '').strip()
        setattr(app, field, int(val) if val.isdigit() else None)
    for field in ['deadline', 'follow_up_date']:
        val = request.POST.get(field, '').strip()
        setattr(app, field, val if val else None)
    app.save()
    if request.headers.get('HX-Request'):
        return render(request, 'components/app_detail_header.html', {'app': app})
    return redirect('application_detail', pk=pk)


@login_required
@require_POST
def chat_message(request, pk):
    app = get_object_or_404(JobApplication, pk=pk, user=request.user)
    user_msg = request.POST.get('message', '').strip()
    if not user_msg:
        return HttpResponse(status=400)

    ChatMessage.objects.create(application=app, role='user', content=user_msg)

    try:
        from ai_tools.claude_client import chat_with_application
        profile = getattr(request.user, 'profile', None)
        history = app.chat_messages.all()[:-1]
        ai_reply = chat_with_application(app, history, user_msg, profile)
    except Exception as e:
        ai_reply = f"AI service error: {str(e)}"

    assistant_msg = ChatMessage.objects.create(application=app, role='assistant', content=ai_reply)

    if request.headers.get('HX-Request'):
        return render(request, 'components/chat_messages.html', {
            'user_msg': user_msg,
            'assistant_msg': assistant_msg,
        })
    return redirect('application_detail', pk=pk)


@login_required
@require_POST
def generate_document(request, pk):
    app = get_object_or_404(JobApplication, pk=pk, user=request.user)
    doc_type = request.POST.get('doc_type', 'cv')
    tone = request.POST.get('tone', 'formal')

    try:
        from ai_tools.claude_client import generate_cv, generate_cover_letter
        profile = getattr(request.user, 'profile', None)
        if doc_type == 'cv':
            content = generate_cv(profile, app)
        else:
            content = generate_cover_letter(profile, app, tone)

        version = app.documents.filter(doc_type=doc_type).count() + 1
        doc = GeneratedDocument.objects.create(
            application=app,
            doc_type=doc_type,
            content=content,
            version=version,
        )
        if request.headers.get('HX-Request'):
            return render(request, 'components/document_preview.html', {'doc': doc})
    except Exception as e:
        if request.headers.get('HX-Request'):
            return HttpResponse(f'<div class="error-msg">Error: {str(e)}</div>', status=500)

    return redirect('application_detail', pk=pk)


@login_required
def export_document(request, doc_id, fmt):
    doc = get_object_or_404(GeneratedDocument, pk=doc_id, application__user=request.user)
    if fmt == 'txt':
        response = HttpResponse(doc.content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{doc.get_doc_type_display()}_v{doc.version}.txt"'
        return response
    elif fmt == 'docx':
        from docx import Document as DocxDoc
        from io import BytesIO
        docx = DocxDoc()
        for line in doc.content.split('\n'):
            docx.add_paragraph(line)
        buf = BytesIO()
        docx.save(buf)
        buf.seek(0)
        response = HttpResponse(buf.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename="{doc.get_doc_type_display()}_v{doc.version}.docx"'
        return response
    elif fmt == 'pdf':
        try:
            from weasyprint import HTML
            from io import BytesIO
            html_content = f"<html><body><pre style='font-family:Arial;'>{doc.content}</pre></body></html>"
            pdf_bytes = HTML(string=html_content).write_pdf()
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{doc.get_doc_type_display()}_v{doc.version}.pdf"'
            return response
        except Exception as e:
            return HttpResponse(f"PDF error: {e}", status=500)
    return HttpResponse(status=400)
