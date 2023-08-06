from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, ContactForm, PostForm, UserCreationForm, UserProfileForm
from .models import Comment, Post, UserProfile
from .tasks import print_contact_message, send_admin_message, send_user_message


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to the login page after successful registration
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if 'submit' in request.POST:  # The user chose to submit the post
                post.status = 'published'
            else:  # The user chose to save the post as a draft
                post.status = 'draft'
            post.save()

            send_admin_message.delay(f"New post with id {post.id} is created.")

            return redirect('user_posts')
    else:
        form = PostForm()

    return render(request, 'create_post.html', {'form': form})


# Create your views here.

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        # If the user is not the author of the post, redirect to a different view or display an error message.
        # For simplicity, we'll redirect to the post detail view.
        return redirect('user_posts')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            return redirect('user_posts.html')
    else:
        form = PostForm(instance=post)

    return render(request, 'edit_post.html', {'form': form, 'post': post})


@login_required
def user_posts(request):
    user = request.user
    posts = Post.objects.filter(author=user).order_by('-pub_date')
    return render(request, 'user_posts.html', {'posts': posts})


@login_required
@cache_page(60 * 2)
def all_posts(request):
    posts = Post.objects.all().order_by('-pub_date')

    paginator = Paginator(posts, 10)

    page = request.GET.get('page')
    try:
        paginated_posts = paginator.page(page)
    except PageNotAnInteger:
        paginated_posts = paginator.page(1)
    except EmptyPage:
        paginated_posts = paginator.page(paginator.num_pages)

    context = {'paginated_posts': paginated_posts}
    return render(request, 'all_posts.html', context)


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post, is_approved=True)

    paginator = Paginator(comments, 2)

    page = request.GET.get('page')
    try:
        paginated_comments = paginator.page(page)
    except PageNotAnInteger:
        paginated_comments = paginator.page(1)
    except EmptyPage:
        paginated_comments = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user if request.user.is_authenticated else None
            comment.save()

            send_admin_message.delay(f"New comment with id {comment.id} submitted.")

            if comment.post.author != request.user:
                send_user_message.delay(request.user.username, f"Your post received a new comment {comment.content}.")
            return redirect('post_detail', post_id=post_id)
    else:
        form = CommentForm()

    context = {'post': post, 'paginated_comments': paginated_comments, 'form': form}
    return render(request, 'post_detail.html', context)


@login_required
def account_profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = None
    return render(request, 'account_profile.html', {'user_profile': user_profile})


@login_required
def edit_profile(request):
    user_profile = request.user.userprofile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('account_profile')
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'edit_profile.html', {'form': form})


@login_required
def view_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_profile = get_object_or_404(UserProfile, user=user)

    if request.user == user:
        return redirect('account_profile')

    return render(request, 'view_profile.html', {'user_profile': user_profile})


@login_required
def contact_admin(request):
    if request.method == 'POST':
        form = ContactForm(request.POST, user=request.user)

        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            print_contact_message.delay(name, email, message)

            return JsonResponse({'success': True})
        else:
            # Return a JSON response with form errors
            return JsonResponse({'errors': form.errors}, status=400)

    else:
        form = ContactForm(user=request.user)

    return render(request, 'contact_form.html', {'form': form})
