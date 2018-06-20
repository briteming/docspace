from django.urls import path, include, re_path
from docspace import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path(r'', views.IndexView.as_view(), name='index'),
    path('logout/', LogoutView.as_view(template_name='login.html'), name='logout'),
    re_path(r'^login/$', views.OAuthLoginView.as_view(), name='login'),
    re_path(r'^oauth/github/$', views.GitHubOAuthView.as_view(), name='github_oauth'),
    path(r'<int:pk>.html', views.OldBlog),
    path(r'author/<int:pk>/', views.author, name='author'),
    path(r'archives/', views.archives, name='archives'),
    path(r'archive/<int:pk>/', views.DetailModelView.as_view(), name='detail'),
    path(r'category/<int:pk>/', views.category, name='category'),
    path(r'tag/<int:pk>/', views.tag, name='tag'),
    path(r'feed/', views.LatestEntriesFeed(), name='feed'),
    path(r'simditor/', include('simditor.urls')),   # add this line
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
