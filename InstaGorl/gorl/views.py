from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404
from .models import Post, Like, Comment, CommentReply
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UpdateProfileForm
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import PostForm, ProfileUpdateForm, PostFilter, CommentForm, CommentReplyForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
# from django.http import QueryDict
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.utils import timezone
from django.db.models import Sum, F
from PIL import Image
from django.template.loader import render_to_string
from django.conf import settings
from django.core.cache import cache


class PostListView(ListView):
    model = Post
    template_name = 'gorl/post_list.html'
    context_object_name = 'posts'
    ordering = '-date_posted'

    def get(self, request, *args, **kwargs):
        paginate_by = request.COOKIES.get("posts_per_page") or 5
        self.paginate_by = int(paginate_by)
        paginator = self.get_paginator(self.get_queryset(), self.paginate_by)
        page = request.GET.get('page') or 1
        try:
            paginator.validate_number(page)
        except:
            page = paginator.num_pages
            return redirect(f'{self.request.path}?page={page}&paginate_by={paginate_by}')
        response = super().get(request, *args, **kwargs)
        response.set_cookie("posts_per_page", paginate_by)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home'
        context['posts_per_page'] = self.paginate_by

        return context


class SearchView(ListView):
    model = Post
    template_name = 'gorl/search.html'
    context_object_name = 'posts'
    ordering = '-date_posted'
    paginate_by = 5
    filterset_class = PostFilter  # import the PostFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = self.filterset_class(
            self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get(self, request, *args, **kwargs):
        title = request.GET.get('title')
        paginate_by = request.COOKIES.get(
            "posts_per_pageee") or self.paginate_by
        self.paginate_by = int(paginate_by)
        queryset = self.get_queryset()
        paginator = self.get_paginator(queryset, self.paginate_by)
        page = request.GET.get('page') or 1
        try:
            page_obj = paginator.page(page)
        except:
            page = paginator.num_pages
            if title:
                return redirect(f'{self.request.path}?page={page}&paginate_by={paginate_by}&title={title}')
            else:
                return redirect(f'{self.request.path}?page={page}&paginate_by={paginate_by}')
        self.kwargs.update({'page_obj': page_obj})
        response = super().get(request, *args, **kwargs)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.all()
        context['title'] = 'Search'
        context['filterset'] = self.filterset
        context['post_count'] = self.get_queryset().count()

        return context


class SearchUsersView(ListView):
    model = User
    template_name = 'gorl/searchUsers.html'
    context_object_name = 'users'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('username', None)
        if query:
            queryset = queryset.filter(username__icontains=query)
        for user in queryset:
            user_posts = Post.objects.filter(author=user)
            total_likes = user_posts.annotate(score=F('upvotes') - F(
                'downvotes')).aggregate(Sum('score'))['score__sum'] or 0
            user.total_likes = total_likes
        return queryset

    def get(self, request, *args, **kwargs):
        title = request.GET.get('username')
        paginate_by = request.COOKIES.get(
            "posts_per_pageeee") or self.paginate_by
        self.paginate_by = int(paginate_by)
        queryset = self.get_queryset()
        paginator = self.get_paginator(queryset, self.paginate_by)
        page = request.GET.get('page') or 1
        try:
            page_obj = paginator.page(page)
        except:
            page = paginator.num_pages
            if title:
                return redirect(f'{self.request.path}?page={page}&paginate_by={paginate_by}&username={title}')
            else:
                return redirect(f'{self.request.path}?page={page}&paginate_by={paginate_by}')
        self.kwargs.update({'page_obj': page_obj})
        response = super().get(request, *args, **kwargs)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Search'
        context['user_count'] = self.get_queryset().count()
        return context


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(
                request, f'Account created for {username}! You are now able to login.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'gorl/register.html', {'form': form, 'title': 'Register'})


def login_view(request):

    if request.method == 'POST':
        form = CustomAuthenticationForm(
            data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)
                return redirect('home')
            else:
                messages.error(
                    request, 'Please enter a correct username and password Gorl. Note that both fields may be case-sensitive Haydur.')
    else:
        message = request.GET.get('message')

        if message:
            # Add the message to the Django messages framework
            messages.success(request, message)
        form = CustomAuthenticationForm()
    return render(request, 'gorl/login.html', {'form': form, 'title': 'Login'})


def logout_view(request):
    logout(request)
    messages.success(
        request, f'You have been logged out!')
    return redirect('login')


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'gorl/create_post.html'

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        files = cleaned_data.get("files")
        file_url = cleaned_data.get("file_url")
        delete_files = cleaned_data.get("delete_files")

        if files and file_url:
            messages.error(
                self.request, "Can only post a file or a URL, not both.")
            return self.form_invalid(form)

        if delete_files and not files:
            messages.error(self.request, "No files to delete.")
            return self.form_invalid(form)

        user = User.objects.get(pk=self.request.user.pk)
        form.instance.author = user
        if Post.objects.filter(author=user).exists():
            last_post = Post.objects.filter(author=user).latest('date_posted')
            if (timezone.now() - last_post.date_posted).total_seconds() < 30:
                messages.error(
                    self.request, "You can only create a post once every 30 seconds.")
                return redirect('home')

        if files:
            form.instance.files = files
            form.instance.file_url = None
        if file_url:
            form.instance.file_url = file_url

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, 'Can only post a file or a URL, not both.')
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create'

        return context

    def get_success_url(self):
        messages.success(self.request, "Post Created Gorl!")
        return reverse('home')


class UpdatePost(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'gorl/update_post.html'

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        files = cleaned_data.get("files")
        file_url = cleaned_data.get("file_url")
        delete_files = cleaned_data.get("delete_files")

        if self.request.user != form.instance.author:
            messages.error(
                self.request, "You don't have permission to edit this post.")
            return redirect('home')

        if files and file_url:
            messages.error(
                self.request, "Can only post a file or a URL, not both.")
            return self.form_invalid(form)

        if delete_files and not files:
            messages.error(self.request, "No files to delete.")
            return self.form_invalid(form)

        if files:
            form.instance.files = files
            form.instance.file_url = None
        if file_url:
            form.instance.file_url = file_url

        if form.cleaned_data.get('delete_files'):
            form.instance.files.delete()
            form.instance.file_url = ""
        else:
            files = form.cleaned_data.get("files")
            if files:
                form.instance.files = files

        form.save()
        messages.success(self.request, "Post edited Gorl.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit'
        return context

    def test_func(self):
        # check if the user is the author of the post
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        messages.success(
            self.request, "Don't be like that Gorl.")
        # redirect to an error page if the user is not the author of the post
        return render(self.request, 'gorl/error.html', {'error': "You don't have permission to edit this post."})

    def get_success_url(self):
        # redirect to the detail view of the post after saving the edits
        return reverse_lazy('post-detail', kwargs={'pk': self.object.pk})


class DeletePostView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'gorl/delete_post.html'

    def test_func(self):
        # Check if the current user is the author of the post
        return self.request.user == self.get_object().author

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, "Post deleted Gorl.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete'
        return context

    def handle_no_permission(self):
        messages.success(
            self.request, "Don't be like that Gorl.")
        # redirect to an error page if the user is not the author of the post
        return render(self.request, 'gorl/error.html', {'error': "You don't have permission to edit this post."})

    def get_success_url(self):
        messages.success(self.request, "Post deleted Gorl.")
        return reverse_lazy('home')


class UserPostListView(ListView):
    model = Post
    template_name = 'gorl/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(
            User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')

    def get(self, request, *args, **kwargs):
        paginate_by = request.COOKIES.get(
            "posts_per_pagee") or self.paginate_by
        self.paginate_by = int(paginate_by)
        queryset = self.get_queryset()
        paginator = self.get_paginator(queryset, self.paginate_by)
        page = request.GET.get('page') or 1
        try:
            paginator.validate_number(page)
        except:
            page = paginator.num_pages
            return redirect(f'{self.request.path}?page={page}&paginate_by={paginate_by}')
        response = super().get(request, *args, **kwargs)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(
            User, username=self.kwargs.get('username'))
        context['user'] = user
        context['show_profile_settings'] = self.request.user.username == user.username
        context['comments'] = Comment.objects.all()
        total_likes = sum(post.score for post in self.get_queryset())
        context['title'] = 'Profile'
        context['total_likes'] = total_likes
        context['post_count'] = Post.objects.filter(author=user).count()
        return context


class UpdateProfileView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UpdateProfileForm
    template_name = 'gorl/update_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_form'] = ProfileUpdateForm(
            instance=self.get_object().profile)
        context['title'] = 'Update'
        return context

    def test_func(self):
        # Check if the current user is the owner of the profile
        return self.request.user == self.get_object()

    def form_valid(self, form):
        response = super().form_valid(form)
        profile_form = ProfileUpdateForm(
            self.request.POST, self.request.FILES, instance=self.get_object().profile)
        if profile_form.is_valid():
            profile_form.save()

        messages.success(self.request, 'Your profile has been updated')
        return response

    def form_invalid(self, form):
        messages.error(
            self.request, 'There was an error updating your profile. The Gorl Name or GorlMail might already be taken.')
        return redirect('update-profile', pk=self.object.pk)

    def handle_no_permission(self):
        messages.success(
            self.request, "Don't be like that Gorl.")
        # redirect to an error page if the user is not the author of the post
        return render(self.request, 'gorl/error.html', {'error': "You don't have permission to edit this profile."})

    def get_success_url(self):
        return reverse_lazy('update-profile', kwargs={'pk': self.object.pk})


# @login_required
# def upvote(request, post_id):
#     post = get_object_or_404(Post, pk=post_id)
#     user = request.user  # get the user object
#     post.upvote(user)
#     return JsonResponse({"upvotes": post.upvotes, "downvotes": post.downvotes, "score": post.score})


# @login_required
# def downvote(request, post_id):
#     post = get_object_or_404(Post, pk=post_id)
#     user = request.user
#     post.downvote(user)
#     return JsonResponse({"upvotes": post.upvotes, "downvotes": post.downvotes, "score": post.score})

@login_required
def upvote(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        user = request.user
        if user.is_authenticated:
            post.upvote(user)
            return JsonResponse({"upvotes": post.upvotes, "downvotes": post.downvotes, "score": post.score})
        else:
            return JsonResponse({"error": "User is not authenticated."}, status=401)
    else:
        messages.success(
            request, "Don't be like that Gorl.")
        return render(request, 'gorl/error.html', {'error': "You don't have permission to do that."})


@login_required
def downvote(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        user = request.user
        if user.is_authenticated:
            post.downvote(user)
            return JsonResponse({"upvotes": post.upvotes, "downvotes": post.downvotes, "score": post.score})
        else:
            return JsonResponse({"error": "User is not authenticated."}, status=401)
    else:
        messages.success(
            request, "Don't be like that Gorl.")
        return render(request, 'gorl/error.html', {'error': "You don't have permission to do that."})


class PostDetailView(DetailView):
    model = Post
    template_name = 'gorl/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        return context


@login_required
def add_comment_to_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            user_last_comment_key = f'user_last_comment_{request.user.pk}'
            last_comment_time = cache.get(user_last_comment_key)

            if last_comment_time and (timezone.now() - last_comment_time) < timezone.timedelta(seconds=30):
                return JsonResponse({'success': False, 'error_message': 'You can only post a comment every 30 seconds.'})
            else:
                comment = form.save(commit=False)
                comment.author = request.user
                comment.post_id = post
                comment.save()
                cache.set(user_last_comment_key, timezone.now(), timeout=30)

                new_comment_score = comment.score if comment else None
                context = {
                    'new_comment': comment,
                    'user_authenticated': True,
                    'user': request.user,
                    'comment_id': comment.id,
                    'new_comment_score': new_comment_score,
                    'parent_id': None,
                }
                new_comment = render_to_string('gorl/comments.html', context)
                context['new_comment_score'] = new_comment_score
                return JsonResponse({'success': True, 'new_comment': new_comment, 'comment_id': comment.id, 'new_comment_score': new_comment_score})
        else:
            messages.error(request, 'There was an error posting your comment.')
    else:
        form = CommentForm()

    comments = post.comments.all()

    context = {
        'form': form,
        'post': post,
        'comments': comments,
        'new_comment': None,
        'user_authenticated': request.user.is_authenticated,
        'new_comment_score': None,
        'parent_id': None,
    }

    return render(request, 'gorl/post_detail.html', context)


@login_required
def upvote_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, pk=comment_id)
        user = request.user
        if user.is_authenticated:
            comment.upvote(user)
            return JsonResponse({"upvotes": comment.upvotes, "downvotes": comment.downvotes, "score": comment.score})
        else:
            return JsonResponse({"error": "User is not authenticated."}, status=401)
    else:
        messages.success(request, "Don't be like that Gorl.")
        return render(request, 'gorl/error.html', {'error': "You don't have permission to do that."})


@login_required
def downvote_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, pk=comment_id)
        user = request.user
        if user.is_authenticated:
            comment.downvote(user)
            return JsonResponse({"upvotes": comment.upvotes, "downvotes": comment.downvotes, "score": comment.score})
        else:
            return JsonResponse({"error": "User is not authenticated."}, status=401)
    else:
        messages.success(
            request, "Don't be like that Gorl.")
        return render(request, 'gorl/error.html', {'error': "You don't have permission to do that."})


class UpdateCommentView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'gorl/update_comment.html'

    def get_success_url(self):
        return reverse_lazy('post-detail', kwargs={'pk': self.object.post_id.pk})

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author=self.request.user)

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.get_object().post_id
        return context

    def handle_no_permission(self):
        messages.success(
            self.request, "Don't be like that Gorl.")
        # redirect to an error page if the user is not the author of the post
        return render(self.request, 'gorl/error.html', {'error': "You don't have permission to edit this comment."})


class DeleteCommentView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'gorl/comment_confirm_delete.html'

    def get_success_url(self):
        comment = self.get_object()
        return reverse_lazy('post-detail', kwargs={'pk': comment.post_id.pk})

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(author=self.request.user)

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # add the comment object to the context dictionary
        context['comment'] = self.get_object()
        context['post'] = self.get_object().post_id
        return context

    def handle_no_permission(self):
        messages.success(
            self.request, "Don't be like that Gorl.")
        # redirect to an error page if the user is not the author of the post
        return render(self.request, 'gorl/error.html', {'error': "You don't have permission to delete this comment."})


@login_required
def add_comment_reply_to_comment(request, post_id, parent_id):
    post = get_object_or_404(Post, id=post_id)
    parent_comment = get_object_or_404(Comment, id=parent_id)

    if request.method == 'POST':
        form = CommentReplyForm(request.POST)
        if form.is_valid():
            user_last_comment_key = f'user_last_comment_{request.user.pk}'
            last_comment_time = cache.get(user_last_comment_key)

            if last_comment_time and (timezone.now() - last_comment_time) < timezone.timedelta(seconds=30):
                return JsonResponse({'success': False, 'error_message': 'You can only post a comment every 30 seconds.'})
            else:
                comment_reply = form.save(commit=False)
                comment_reply.author = request.user
                comment_id = request.POST.get('comment_id')
                comment_reply.parent_comment = get_object_or_404(
                    Comment, id=comment_id)
                comment_reply.save()
                cache.set(user_last_comment_key, timezone.now(), timeout=30)

                new_comment_score = comment_reply.score if comment_reply else None
                context = {
                    'new_comment': comment_reply,
                    'user_authenticated': True,
                    'user': request.user,
                    'comment_id': comment_reply.id,
                    'new_comment_score': new_comment_score,
                    'parent_id': parent_id,
                    'post_id': post_id,
                    'parent_comment_id': parent_comment.id,
                }
                new_comment = render_to_string(
                    'gorl/comments_comments.html', context)
                context['new_comment_score'] = new_comment_score
                return JsonResponse({'success': True, 'new_comment': new_comment, 'comment_id': comment_reply.id, 'new_comment_score': new_comment_score})
        else:
            messages.error(request, 'There was an error posting your comment.')
    else:
        form = CommentReplyForm()

    comments = post.comments.all()

    context = {
        'form': form,
        'post': post,
        'comments': comments,
        'new_comment': None,
        'user_authenticated': request.user.is_authenticated,
        'new_comment_score': None,
        'parent_id': parent_id,
        'post_id': post_id,
        'parent_comment_id': parent_comment.id,
    }

    return render(request, 'gorl/post_detail.html', context)
