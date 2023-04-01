from django.urls import path
from . import views


urlpatterns = [
    path('', views.PostListView.as_view(), name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create/', views.CreatePostView.as_view(), name='post-create'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('upvote/<int:post_id>', views.upvote, name='upvote'),
    path('downvote/<int:post_id>', views.downvote, name='downvote'),
    path('posts/<int:pk>/edit/', views.UpdatePost.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', views.DeletePostView.as_view(), name='post-delete'),
    path('user/<str:username>/', views.UserPostListView.as_view(), name='user-posts'),
    path('update-profile/<int:pk>/',
         views.UpdateProfileView.as_view(), name='update-profile'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('search-users/', views.SearchUsersView.as_view(), name='search-users'),
    path('post/<int:post_id>/comment/',
         views.add_comment_to_post, name='add_comment_to_post'),
    path('comment/upvote/<int:comment_id>/',
         views.upvote_comment, name='upvote_comment'),
    path('comment/downvote/<int:comment_id>/',
         views.downvote_comment, name='downvote_comment'),
    path('post/<int:post_id>/comment/<int:pk>/update/', views.UpdateCommentView.as_view(), name='update-comment'),
    path('post/<int:post_id>/comment/<int:pk>/delete/', views.DeleteCommentView.as_view(), name='delete-comment'),

]
