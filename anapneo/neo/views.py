from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.contrib.auth.models import User
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template import RequestContext

from anapneo.neo.models import UserProfile, Neo, Feedback
from anapneo.neo.forms import NeoForm, UserProfileForm, FeedbackForm
from anapneo.decorators import is_logged_in
from django.db.models import Q

from datetime import datetime


def index(request):
    neo_list = Neo.objects.all().order_by('-no')[:7]
    if request.user.is_authenticated():
        me = UserProfile.objects.get(user=request.user)
        return render(request, 'index.html', {'me': me, 'neo_list': neo_list})
    return render(request, 'index.html', {'neo_list': neo_list})


def dashboard(request):
    if request.user.is_authenticated():
        try:
            me = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            display_name = request.user
            return redirect('/register/')
    
    # Search form
    if request.method == 'POST':
        q = request.POST['query']
        neos = filter_neos(q)
    else:
        neos = Neo.objects.all()

    paginator = Paginator(neos, 50)
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    # If page request (9999) is out of range, deliver last page of results.
    try:
        neo_list = paginator.page(page)
    except (EmptyPage, InvalidPage):
        neo_list = paginator.page(paginator.num_pages)

    if request.user.is_authenticated():
        return render(request, 'dashboard.html', {'neo_list': neo_list, 'page': page, 'me': me})
    return render(request, 'dashboard.html', {'neo_list': neo_list, 'page': page},
                  context_instance=RequestContext(request))


# It is used for searching in dashboard thus
# neo_fields MUST be the same with fields 
# displayed in dashboard.html 
def filter_neos(query):
    str_fields = ['no',
                  #'observation_date', # No date fields included 
                  'score',
                  'user__display_name', 
                  'position_ra',
                  'position_dec',
                  'magnitude',
                  #'updated',
                  'num_obs',
                  'arc',
                  'nominal_h']
    
    or_query = None
    for f in str_fields:
        q = Q(**{"%s__contains" % f : query})
        if or_query is None:
            or_query = q
        else:
            or_query = or_query | q
            
    return Neo.objects.filter(or_query)


@is_logged_in
def register(request):
    try:
        me = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        if request.method == 'POST':
            me = User.objects.get(username=request.user)
            form = UserProfileForm(request.POST)
            if form.is_valid():
                f = form.save(commit=False)
                f.user = me
                f.email = me.email
                form.save()
                return redirect('/dashboard/')
        else:
            form = UserProfileForm()
    return render(request, 'profile_edit_or_create.html', locals())


def neo_view(request, no):
    neo = get_object_or_404(Neo, no=no)
    f = None
    if request.user.is_authenticated():
        try:
            f = Feedback.objects.get(user=request.user, neo=neo)
        except Feedback.DoesNotExist:
            pass

    if request.method == 'POST' and request.user.is_authenticated():
        form = FeedbackForm(request.POST)
        if form.is_valid():
            vote = form.cleaned_data['vote']
            if f:
                f.vote = vote
                f.save()
            else:
                f = Feedback(user=request.user, vote=vote, neo=neo)
                f.save()
    else:
        form = FeedbackForm()

    if request.user.is_authenticated():
        me = UserProfile.objects.get(user=request.user)
        return render(request, 'neo_view.html',
                  {'neo': neo, 'feedback': form, 'me': me})
    return render(request, 'neo_view.html',
                  {'neo': neo, 'feedback': form})

@is_logged_in
def neo_edit(request, no):
    me = UserProfile.objects.get(user=request.user)
    try:
        obj = Neo.objects.get_or_create(no=no, user=request.user)
        if request.method == 'POST':
            form = NeoForm(request.POST, instance=obj)
            if form.is_valid():
                f = form.save(commit=False)
                f.user = request.user
                form.save()
                return redirect('/dashboard/')
        else:
            form = NeoForm()
        return render(request, 'neo_edit_or_create.html', {'form': form, 'me': me})

    except Neo.DoesNotExist:
        return redirect('/dashboard/')


@is_logged_in
def neo_create(request):
    me = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = NeoForm(request.POST)
        if form.is_valid():
            f = form.save(commit=False)
            f.user = request.user
            curdate = datetime.now()
            latest_no = Neo.objects.filter(created__year=curdate.strftime("%Y"),
                        created__month=curdate.strftime("%m"),
                        created__day=curdate.strftime("%d")).count()
            new_no = latest_no + 1
            tmpid = "%03d" % ( new_no )
            f.no = str(curdate.strftime("%Y%m%d")) + tmpid
            form.save()
            return redirect('/dashboard/')
    else:
        form = NeoForm()
    return render(request, 'neo_edit_or_create.html', {'form': form, 'me': me})



@is_logged_in
def profile_view(request, slug):
    me = get_object_or_404(UserProfile.objects.filter(display_name=slug))
    return render(request, 'profile_view.html', locals())


@is_logged_in
def profile_edit(request, slug):
    me = UserProfile.objects.get(user=request.user)
    if me.display_name != slug:
        return redirect('/dashboard/')
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=me)
        if form.is_valid():
            form.save()
            return redirect('/dashboard/')
    else:
        form = UserProfileForm(instance=me)
    return render(request, 'profile_edit_or_create.html', locals())


def about(request):
    if request.user.is_authenticated():
        me = UserProfile.objects.get(user=request.user)
        return render(request, 'about.html', {'me': me})
    return render(request, 'about.html', )


def contact(request):
    if request.user.is_authenticated():
        me = UserProfile.objects.get(user=request.user)
        return render(request, 'contact.html', {'me': me})
    return render(request, 'contact.html', )
