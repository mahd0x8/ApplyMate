from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from applications.models import JobApplication
from profiles.models import UserProfile


def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/landing.html')


@login_required
def dashboard(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    apps = JobApplication.objects.filter(user=user)
    columns = {
        'wishlist': list(apps.filter(status='wishlist')),
        'applied': list(apps.filter(status='applied')),
        'interview': list(apps.filter(status='interview')),
        'offer': list(apps.filter(status='offer')),
        'rejected': list(apps.filter(status='rejected')),
    }

    total_applied = apps.exclude(status='wishlist').count()
    interviews = apps.filter(status__in=['interview', 'offer']).count()
    offers = apps.filter(status='offer').count()
    response_rate = round((interviews / total_applied * 100)) if total_applied else 0

    col_meta = [
        ('wishlist', 'Wishlist', '#94A3B8'),
        ('applied', 'Applied', '#10B981'),
        ('interview', 'Interview', '#F59E0B'),
        ('offer', 'Offer', '#22C55E'),
        ('rejected', 'Rejected', '#EF4444'),
    ]

    return render(request, 'core/dashboard.html', {
        'profile': profile,
        'columns': columns,
        'col_meta': col_meta,
        'total_applied': total_applied,
        'interviews': interviews,
        'offers': offers,
        'response_rate': response_rate,
        'total_apps': apps.count(),
    })
