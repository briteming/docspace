import requests
from django.views.generic import View, TemplateView
from django.core.exceptions import PermissionDenied
from django.contrib.auth import login
from django.apps import apps
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.views import LoginView

if settings.AUTH_USER_MODEL:
    _label, _model = settings.AUTH_USER_MODEL.split('.')
    User = apps.get_model(app_label=_label, model_name=_model, require_ready=True)
else:
    from django.contrib.auth.models import User

from docspace.models import Metadata

GITHUB_CLIENT_ID = getattr(settings, 'GITHUB_CLIENT_ID', None)
GITHUB_CLIENT_SECRET = getattr(settings, 'GITHUB_CLIENT_SECRET', None)
'''4529033a34be3e8ed521eed00d513a1e27b40554'''


class OAuthView(View):
    '''第三方账号认证视图，该视图负责处理回调请求，获取用户信息'''
    access_token_url = None
    user_api = None
    client_id = None
    client_secret = None

    def get(self, request, *args, **kwargs):
        access_token = self.get_access_token(request)
        user_info = self.get_user_info(access_token)
        return self.authenticate(user_info)

    def authenticate(self, user_info):
        #子类中实现 auth 方法
        pass

    def get_access_token(self, request):
        '''获取access token'''
        url = self.access_token_url
        headers = {'Accept': 'application/json'}
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': request.GET['code']
        }
        req = requests.post(url, data, headers=headers, timeout=5)
        # 解析返回的json文本
        result = req.json()
        if 'access_token' in result:
            return result['access_token']
        else:
            # 由于code是临时的用户标记
            # 如果code过期了，则无法得到access_token
            # 这种情况下应该抛出禁止访问的错误，django会返回403
            raise PermissionDenied

    def get_user_info(self, access_token):
        '''获取用户信息'''
        url = self.user_api + access_token
        # 拿到access_token后调用api即可获得用户信息
        r = requests.get(url, timeout=5)
        # 用户信息也是json文本
        user_info = r.json()
        print(user_info)
        return user_info

    def get_success_url(self):
        '''获取登录成功后返回的网页'''
        if 'next' in self.request.session:
            return self.request.session.pop('next')
        else:
            return reverse('index')

class GitHubOAuthView(OAuthView):
    '''github账号认证视图'''
    # 在具体类中定义相应的参数
    access_token_url = 'https://github.com/login/oauth/access_token'
    user_api = 'https://api.github.com/user?access_token='
    client_id = getattr(settings, 'GITHUB_CLIENT_ID', '494c5dbc2ad26c59498e')
    client_secret = getattr(
        settings,
        'GITHUB_CLIENT_SECRET',
        '4529033a34be3e8ed521eed00d513a1e27b40554'
        )

    def authenticate(self, user_info):
        '用户认证'
        verify = Metadata.objects.filter(key='github', value=user_info['id'])
        #user = User.objects.filter(profile__github_id=user_info['id'])
        # 在数据库中检索GitHub id
        # 如果有，则选择相应的用户登录
        # 如果没有，则创建用户，然后再登录
        if not verify:
            # 用户的模型见下文
            # user_info里'login'为用户名，'id'为GitHub的id，'avatar_url'为用户头像的url
            # 除此还有很多其他信息，如果想知道，直接print(user_info)
            user = User.objects.create_user(user_info['login'], website=user_info['html_url'])
            Metadata.objects.create(object_repr=user, key='github', value=user_info['id'])
        else:
            user = verify[0].object_repr
        # 用login函数登录，logout函数注销
        login(self.request, user)
        return redirect(self.get_success_url())


class OAuthLoginView(LoginView):

    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        context = super(OAuthLoginView, self).get_context_data(**kwargs)
        if 'next' in self.request.GET:
            self.request.session['next'] = self.request.GET['next']
        client_id = getattr(settings, 'GITHUB_CLIENT_ID', '494c5dbc2ad26c59498e')
        authorize_url = 'https://github.com/login/oauth/authorize?client_id='
        context['github_oauth_url'] = authorize_url + '{}'.format(client_id)
        return context
