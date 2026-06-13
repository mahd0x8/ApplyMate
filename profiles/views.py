from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from .models import UserProfile, WorkExperience, Education, Skill, Project, Certification, CustomEntry
from collections import defaultdict


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    grouped = defaultdict(list)
    for entry in profile.custom_entries.all():
        grouped[entry.heading].append(entry)
    return render(request, 'profiles/profile.html', {'profile': profile, 'custom_sections': dict(grouped)})


@login_required
@require_POST
def profile_update(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    fields = ['full_name', 'email', 'phone', 'location', 'linkedin_url',
              'github_url', 'website_url', 'professional_summary',
              'preferred_titles', 'preferred_industries', 'preferred_locations', 'work_mode']
    for field in fields:
        if field in request.POST:
            setattr(profile, field, request.POST[field])
    for field in ['salary_min', 'salary_max']:
        val = request.POST.get(field, '').strip()
        setattr(profile, field, int(val) if val.isdigit() else None)
    profile.save()
    if request.headers.get('HX-Request'):
        return HttpResponse('<div class="save-success">Saved!</div>')
    return redirect('profile')


@login_required
@require_POST
def add_work_experience(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    exp = WorkExperience.objects.create(
        profile=profile,
        company=request.POST.get('company', ''),
        title=request.POST.get('title', ''),
        location=request.POST.get('location', ''),
        start_date=request.POST.get('start_date') or '2020-01-01',
        end_date=request.POST.get('end_date') or None,
        is_current=request.POST.get('is_current') == 'on',
        description=request.POST.get('description', ''),
    )
    if request.headers.get('HX-Request'):
        return render(request, 'components/work_exp_item.html', {'exp': exp})
    return redirect('profile')


@login_required
@require_POST
def delete_work_experience(request, pk):
    exp = get_object_or_404(WorkExperience, pk=pk, profile__user=request.user)
    exp.delete()
    if request.headers.get('HX-Request'):
        return HttpResponse(status=200)
    return redirect('profile')


@login_required
@require_POST
def add_education(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    edu = Education.objects.create(
        profile=profile,
        institution=request.POST.get('institution', ''),
        degree=request.POST.get('degree', ''),
        field_of_study=request.POST.get('field_of_study', ''),
        start_date=request.POST.get('start_date') or '2020-01-01',
        end_date=request.POST.get('end_date') or None,
        is_current=request.POST.get('is_current') == 'on',
        gpa=request.POST.get('gpa', ''),
        description=request.POST.get('description', ''),
    )
    if request.headers.get('HX-Request'):
        return render(request, 'components/education_item.html', {'edu': edu})
    return redirect('profile')


@login_required
@require_POST
def delete_education(request, pk):
    edu = get_object_or_404(Education, pk=pk, profile__user=request.user)
    edu.delete()
    if request.headers.get('HX-Request'):
        return HttpResponse(status=200)
    return redirect('profile')


@login_required
@require_POST
def add_skill(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    skill = Skill.objects.create(
        profile=profile,
        name=request.POST.get('name', ''),
        category=request.POST.get('category', 'technical'),
        proficiency=request.POST.get('proficiency', 'intermediate'),
    )
    if request.headers.get('HX-Request'):
        return render(request, 'components/skill_tag.html', {'skill': skill})
    return redirect('profile')


@login_required
@require_POST
def delete_skill(request, pk):
    skill = get_object_or_404(Skill, pk=pk, profile__user=request.user)
    skill.delete()
    if request.headers.get('HX-Request'):
        return HttpResponse(status=200)
    return redirect('profile')


@login_required
@require_POST
def add_project(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    proj = Project.objects.create(
        profile=profile,
        name=request.POST.get('name', ''),
        url=request.POST.get('url', ''),
        description=request.POST.get('description', ''),
        technologies=request.POST.get('technologies', ''),
    )
    if request.headers.get('HX-Request'):
        return render(request, 'components/project_item.html', {'proj': proj})
    return redirect('profile')


@login_required
@require_POST
def delete_project(request, pk):
    proj = get_object_or_404(Project, pk=pk, profile__user=request.user)
    proj.delete()
    if request.headers.get('HX-Request'):
        return HttpResponse(status=200)
    return redirect('profile')


@login_required
@require_POST
def add_certification(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    cert = Certification.objects.create(
        profile=profile,
        name=request.POST.get('name', ''),
        issuer=request.POST.get('issuer', ''),
        issued_date=request.POST.get('issued_date') or None,
        credential_url=request.POST.get('credential_url', ''),
    )
    if request.headers.get('HX-Request'):
        return render(request, 'components/cert_item.html', {'cert': cert})
    return redirect('profile')


@login_required
@require_POST
def delete_certification(request, pk):
    cert = get_object_or_404(Certification, pk=pk, profile__user=request.user)
    cert.delete()
    if request.headers.get('HX-Request'):
        return HttpResponse(status=200)
    return redirect('profile')


@login_required
@require_POST
def add_custom_entry(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    CustomEntry.objects.create(
        profile=profile,
        heading=request.POST.get('heading', '').strip(),
        title=request.POST.get('title', '').strip(),
        date=request.POST.get('date') or None,
        description=request.POST.get('description', '').strip(),
    )
    if request.headers.get('HX-Request'):
        from django.http import HttpResponse
        response = HttpResponse(status=204)
        response['HX-Refresh'] = 'true'
        return response
    return redirect('profile')


@login_required
@require_POST
def delete_custom_entry(request, pk):
    entry = get_object_or_404(CustomEntry, pk=pk, profile__user=request.user)
    entry.delete()
    if request.headers.get('HX-Request'):
        response = HttpResponse(status=204)
        response['HX-Refresh'] = 'true'
        return response
    return redirect('profile')
