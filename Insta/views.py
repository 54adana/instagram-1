Learn more or give us feedback
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from .forms import UpdateUserForm, UpdateUserProfileForm, PostForm, CommentForm, UserRegistrationForm
from django.contrib.auth import login, authenticate
from .models import Profile,Post

def signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = UserRegistrationForm()
        params = {
            'form': form
        }
    return render(request,'registration/register.html', locals())

@login_required(login_url='login')
def index(request):
    images = Post.objects.all()
    users = User.objects.all()
    posts = Post.get_all_posts()
    # print(posts)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            user_x=Profile.objects.get(name=request.user.username)
            post.user = user_x
            post.save()
            return HttpResponseRedirect(request.path_info)
    else:
        form = PostForm()
    params = {
        'images': images,
        'form': form,
        'users': users,
        'posts': posts,
    }
    return render(request, 'insta/index.html', locals())

@login_required(login_url='login')
def profile(request):
    # images = request.profile.posts.all()
    user_x=User.objects.get(username=request.user.username)
    profile_x=Profile.objects.get(name=user_x.username)
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        # prof_form = UpdateUserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid():
            user_form.save()
            # prof_form.save()
            return HttpResponseRedirect(request.path_info)
    else:
        user_form = UpdateUserForm(instance=request.user)
        # prof_form = UpdateUserProfileForm(instance=request.user.profile)
        # print(images)
    params = {
        'user_form': user_form,
    }
    return render(request, 'insta/profile.html',{'profile':profile_x})

@login_required(login_url='login')
def user_profile(request, username):
    user_prof = get_object_or_404(User, username=username)
    if request.user == user_prof:
        return redirect('profile', username=request.user.username)
    user_posts = user_prof.profile.posts.all()

    params = {
        'user_prof': user_prof,
        'user_posts': user_posts
    }
    return render(request, 'insta/profile_data.html', locals())


@login_required(login_url='login')
def post_comment(request, id):
    image = get_object_or_404(Post, pk=id)
    is_liked = False
    if image.likes.filter(id=request.user.id).exists():
        is_liked = True
    if request.method == 'Post':
        form = CommentForm(request.POST)
        if form.is_valid():
            savecomment = form.save(commit=False)
            savecomment.post = image
            savecomment.user = request.user.profile
            savecomment.save()
            return HttpResponseRedirect(request.path_info)
    else:
        form = CommentForm()
    params = {
        'image': image,
        'form': form,
        'is_liked': is_liked,
        'total_likes': image.total_likes()
    }
    return render(request, 'insta/post_view.html', locals())


def like_post(request):
    image = get_object_or_404(Post, id=request.POST.get('image_id'))
    is_liked = False
    if image.likes.filter(id=request.user.id).exists():
        image.likes.remove(request.user)
        is_liked = False
    else:
        image.likes.add(request.user)
        is_liked = False
    return redirect('comment', id=image.id)


@login_required(login_url='login')
def search_profile(request):
    if 'search_user' in request.GET and request.GET['search_user']:
        name = request.GET.get("search_user")
        results = Profile.search_profile(name)
        message = f'name'
        params = {
            'results': results,
            'message': message
        }
        return render(request, 'insta/search_results.html', locals())
    else:
        message = "You haven't searched for any image category"
    return render(request, 'insta/search_results.html', locals())

def uprofile(request):
    return render(request,'uprofile.html')