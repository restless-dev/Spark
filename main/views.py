from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Profile, Post, LikePost, FollowersCount, Notification

@login_required(login_url='signin')
def index(request):
    user_profile = Profile.objects.get(user=request.user)
    user_following_list = [follower.user for follower in FollowersCount.objects.filter(follower=request.user)]
    user_following_list.append(request.user)

    feed_list = Post.objects.filter(user__in=user_following_list)

    all_users = User.objects.exclude(username=request.user.username)
    user_following_all = [user_list.username for user_list in User.objects.filter(username__in=user_following_list)]

    suggested_users_count = max(4, len(all_users) - len(user_following_all))
    final_suggestions_list = all_users.exclude(username__in=user_following_all).order_by('?')[:suggested_users_count]

    suggestions_username_profile_list = Profile.objects.filter(user__in=final_suggestions_list).order_by('?')

    user_notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')


    return render(request, 'index.html', {'user_profile': user_profile, 'posts': feed_list, 'suggestions_username_profile_list': suggestions_username_profile_list, 'user_notifications': user_notifications})

def upload(request):

    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user = user, image = image, caption = caption)
        new_post.save()

        return redirect('/')

    else:
        return redirect('/')

@login_required(login_url='signin')
def search(request):
    user_profile = Profile.objects.get(user=request.user)
    user_notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')

    if request.method == 'POST':
        username = request.POST['username']

        username_profile_list = Profile.objects.filter(user__username__icontains=username)
    else:
        username_profile_list = []
        
    return render(request, 'search.html', {'username_profile_list': username_profile_list, 'user_profile': user_profile, 'user_notifications': user_notifications})

def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter, created = LikePost.objects.get_or_create(post_id=post_id, username=username)

    if created:
        post.num_of_likes += 1
        Notification.objects.create(
            recipient = get_user_model().objects.get(username=post.user),
            sender=request.user,
            action_type='like',
            post=post,
        )
    else:
        like_filter.delete()
        post.num_of_likes -= 1

    post.save()
    return redirect('/')

@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username = pk)
    user_profile = Profile.objects.get(user = user_object)
    user_posts = Post.objects.filter(user = pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower = follower, user = user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
        'viewer_user': follower,
    }
    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST.get('follower')
        user = request.POST.get('user')
        followers_count, created = FollowersCount.objects.get_or_create(follower=follower, user=user)

        if not created:
            followers_count.delete()
        else:
            Notification.objects.create(
                recipient=User.objects.get(username=user),
                sender=User.objects.get(username=follower),
                action_type='follow',
            )
        return redirect(reverse('profile', args=[user]))
    else:
        return redirect('/')

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        image = request.FILES.get('image', user_profile.profileimg)
        cover = request.FILES.get('cover', user_profile.profilecover)
        bio = request.POST['bio']
        location = request.POST['location']

        user_profile.profileimg = image
        user_profile.profilecover = cover
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()

        return redirect('settings')
    
    new_account = request.session.get('new_account', False)

    if new_account:
        request.session['new_account'] = False
        return render(request, 'starter-setting.html', {'user_profile': user_profile})

    return render(request, 'setting.html', {'user_profile': user_profile})

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password != password2:
            messages.info(request, "The passwords don't match... Please, try again.")
            return redirect('signup')

        if User.objects.filter(email=email).exists() or User.objects.filter(username=username).exists():
            messages.info(request, 'This email or username is already in use. Please, try again.')
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        user_login = authenticate(username=username, password=password)
        login(request, user_login)

        new_profile = Profile.objects.create(user=user, id_user=user.id)
        new_profile.save()
        request.session['new_account'] = True

        return redirect('settings')
    else:
        return render(request, 'signup.html')
    
def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')
    else:
        return render(request, 'signin.html')
    
@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(login_url='signin')
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    current_url = request.META.get('HTTP_REFERER')


    if post.user == request.user.username:
        post.delete()

    return redirect(current_url)