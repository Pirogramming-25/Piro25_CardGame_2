import json
import os
import secrets
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse

from .env import load_env


load_env()

GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USERINFO_URL = 'https://openidconnect.googleapis.com/v1/userinfo'

KAKAO_AUTH_URL = 'https://kauth.kakao.com/oauth/authorize'
KAKAO_TOKEN_URL = 'https://kauth.kakao.com/oauth/token'
KAKAO_USERINFO_URL = 'https://kapi.kakao.com/v2/user/me'

NAVER_AUTH_URL = 'https://nid.naver.com/oauth2.0/authorize'
NAVER_TOKEN_URL = 'https://nid.naver.com/oauth2.0/token'
NAVER_USERINFO_URL = 'https://openapi.naver.com/v1/nid/me'


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:main')

    context = {}
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'login':
            return _handle_login(request, context)
        if action == 'signup':
            return _handle_signup(request, context)

    return render(request, 'accounts/login.html', context)


@login_required(login_url='accounts:login')
def main_view(request):
    return render(request, 'accounts/after.html')


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


def google_login(request):
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    if not client_id or not client_secret:
        return HttpResponseBadRequest('Google login is not configured.')

    state = _save_oauth_state(request, 'google')
    params = {
        'client_id': client_id,
        'redirect_uri': _provider_redirect_uri(request, 'google_callback'),
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
        'prompt': 'select_account',
    }
    return redirect(f'{GOOGLE_AUTH_URL}?{urlencode(params)}')


def google_callback(request):
    if request.GET.get('error'):
        return redirect('accounts:login')
    if not _is_valid_oauth_callback(request, 'google'):
        return HttpResponseBadRequest('Invalid Google login request.')

    token_data = _request_google_token(request, request.GET.get('code'))
    access_token = token_data.get('access_token')
    if not access_token:
        error = token_data.get('error_description') or token_data.get('error') or 'Unknown Google token error.'
        return HttpResponseBadRequest(f'Google did not return an access token: {error}')

    profile = _request_google_profile(access_token)
    email = profile.get('email')
    if not email or not profile.get('email_verified'):
        return HttpResponseBadRequest('Google account email is not verified.')

    user = _get_or_create_social_user(
        provider='google',
        provider_id=profile.get('sub', email),
        username_base=email.split('@', 1)[0],
        email=email,
        first_name=profile.get('given_name', ''),
        last_name=profile.get('family_name', ''),
    )
    login(request, user)
    return redirect('accounts:main')


def kakao_login(request):
    rest_api_key = os.environ.get('KAKAO_REST_API_KEY')
    if not rest_api_key:
        return HttpResponseBadRequest('Kakao login is not configured.')

    state = _save_oauth_state(request, 'kakao')
    params = {
        'client_id': rest_api_key,
        'redirect_uri': _provider_redirect_uri(request, 'kakao_callback'),
        'response_type': 'code',
        'state': state,
    }
    return redirect(f'{KAKAO_AUTH_URL}?{urlencode(params)}')


def kakao_callback(request):
    if request.GET.get('error'):
        return redirect('accounts:login')
    if not _is_valid_oauth_callback(request, 'kakao'):
        return HttpResponseBadRequest('Invalid Kakao login request.')

    token_data = _request_kakao_token(request, request.GET.get('code'))
    access_token = token_data.get('access_token')
    if not access_token:
        error = token_data.get('error_description') or token_data.get('error') or 'Unknown Kakao token error.'
        return HttpResponseBadRequest(f'Kakao did not return an access token: {error}')

    profile = _request_kakao_profile(access_token)
    kakao_account = profile.get('kakao_account', {})
    properties = profile.get('properties', {})
    email = kakao_account.get('email', '')
    nickname = properties.get('nickname') or kakao_account.get('profile', {}).get('nickname') or 'kakao_user'
    user = _get_or_create_social_user(
        provider='kakao',
        provider_id=str(profile.get('id')),
        username_base=nickname,
        email=email,
        first_name=nickname,
    )
    login(request, user)
    return redirect('accounts:main')


def naver_login(request):
    client_id = os.environ.get('NAVER_CLIENT_ID')
    client_secret = os.environ.get('NAVER_CLIENT_SECRET')
    if not client_id or not client_secret:
        return HttpResponseBadRequest('Naver login is not configured.')

    state = _save_oauth_state(request, 'naver')
    params = {
        'client_id': client_id,
        'redirect_uri': _provider_redirect_uri(request, 'naver_callback'),
        'response_type': 'code',
        'state': state,
    }
    return redirect(f'{NAVER_AUTH_URL}?{urlencode(params)}')


def naver_callback(request):
    if request.GET.get('error'):
        return redirect('accounts:login')
    if not _is_valid_oauth_callback(request, 'naver'):
        return HttpResponseBadRequest('Invalid Naver login request.')

    token_data = _request_naver_token(request, request.GET.get('code'), request.GET.get('state'))
    access_token = token_data.get('access_token')
    if not access_token:
        error = token_data.get('error_description') or token_data.get('error') or 'Unknown Naver token error.'
        return HttpResponseBadRequest(f'Naver did not return an access token: {error}')

    profile_data = _request_naver_profile(access_token)
    profile = profile_data.get('response', {})
    provider_id = profile.get('id')
    if not provider_id:
        return HttpResponseBadRequest('Naver did not return a user id.')

    email = profile.get('email', '')
    nickname = profile.get('nickname') or profile.get('name') or 'naver_user'
    user = _get_or_create_social_user(
        provider='naver',
        provider_id=provider_id,
        username_base=nickname,
        email=email,
        first_name=nickname,
    )
    login(request, user)
    return redirect('accounts:main')


def _handle_login(request, context):
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')
    user = authenticate(request, username=username, password=password)

    if user is None:
        context.update({
            'login_error': '아이디 또는 비밀번호를 확인해주세요.',
            'open_modal': 'login',
            'login_username': username,
        })
        return render(request, 'accounts/login.html', context)

    login(request, user)
    return redirect('accounts:main')


def _handle_signup(request, context):
    User = get_user_model()
    username = request.POST.get('username', '').strip()
    password1 = request.POST.get('password1', '')
    password2 = request.POST.get('password2', '')

    error = _validate_signup(User, username, password1, password2)
    if error:
        context.update({
            'signup_error': error,
            'open_modal': 'signup',
            'signup_username': username,
        })
        return render(request, 'accounts/login.html', context)

    user = User.objects.create_user(username=username, password=password1)
    login(request, user)
    return redirect('accounts:main')


def _validate_signup(User, username, password1, password2):
    if not username:
        return '아이디를 입력해주세요.'
    if User.objects.filter(username=username).exists():
        return '이미 사용 중인 아이디입니다.'
    if not password1:
        return '비밀번호를 입력해주세요.'
    if password1 != password2:
        return '비밀번호가 일치하지 않습니다.'
    if len(password1) < 8:
        return '비밀번호는 8자 이상이어야 합니다.'
    return None


def _save_oauth_state(request, provider):
    state = secrets.token_urlsafe(32)
    request.session[f'{provider}_oauth_state'] = state
    return state


def _is_valid_oauth_callback(request, provider):
    expected_state = request.session.pop(f'{provider}_oauth_state', None)
    return (
        request.GET.get('code')
        and expected_state
        and request.GET.get('state') == expected_state
    )


def _provider_redirect_uri(request, callback_name):
    return request.build_absolute_uri(reverse(f'accounts:{callback_name}'))


def _request_google_token(request, code):
    payload = urlencode({
        'code': code,
        'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
        'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
        'redirect_uri': _provider_redirect_uri(request, 'google_callback'),
        'grant_type': 'authorization_code',
    }).encode()
    return _post_form_json(GOOGLE_TOKEN_URL, payload)


def _request_google_profile(access_token):
    return _get_bearer_json(GOOGLE_USERINFO_URL, access_token)


def _request_kakao_token(request, code):
    params = {
        'code': code,
        'client_id': os.environ.get('KAKAO_REST_API_KEY'),
        'redirect_uri': _provider_redirect_uri(request, 'kakao_callback'),
        'grant_type': 'authorization_code',
    }
    kakao_client_secret = os.environ.get('KAKAO_CLIENT_SECRET')
    if kakao_client_secret:
        params['client_secret'] = kakao_client_secret

    return _post_form_json(KAKAO_TOKEN_URL, urlencode(params).encode())


def _request_kakao_profile(access_token):
    return _get_bearer_json(KAKAO_USERINFO_URL, access_token)


def _request_naver_token(request, code, state):
    params = urlencode({
        'grant_type': 'authorization_code',
        'client_id': os.environ.get('NAVER_CLIENT_ID'),
        'client_secret': os.environ.get('NAVER_CLIENT_SECRET'),
        'code': code,
        'state': state,
        'redirect_uri': _provider_redirect_uri(request, 'naver_callback'),
    })
    return _get_json(f'{NAVER_TOKEN_URL}?{params}')


def _request_naver_profile(access_token):
    return _get_bearer_json(NAVER_USERINFO_URL, access_token)


def _post_form_json(url, payload):
    req = Request(url, data=payload, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    return _open_json(req)


def _get_json(url):
    return _open_json(url)


def _get_bearer_json(url, access_token):
    req = Request(url)
    req.add_header('Authorization', f'Bearer {access_token}')
    return _open_json(req)


def _open_json(request):
    try:
        with urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode())
    except HTTPError as exc:
        body = exc.read().decode()
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {'error': f'HTTP {exc.code}', 'error_description': body}


def _get_or_create_social_user(provider, provider_id, username_base, email='', first_name='', last_name=''):
    User = get_user_model()
    provider_username = f'{provider}_{provider_id}'
    user = User.objects.filter(username=provider_username).first()
    if user:
        _update_social_user_display_name(user, username_base, first_name, last_name)
        return user

    if email:
        user = User.objects.filter(email=email).first()
        if user:
            _update_social_user_display_name(user, username_base, first_name, last_name)
            return user

    user = User(username=_unique_username(User, provider_username), email=email)
    user.first_name = first_name or username_base
    user.last_name = last_name
    user.set_unusable_password()
    user.save()
    return user


def _update_social_user_display_name(user, username_base, first_name='', last_name=''):
    display_name = first_name or username_base
    changed = False
    if display_name and user.first_name != display_name:
        user.first_name = display_name
        changed = True
    if last_name and user.last_name != last_name:
        user.last_name = last_name
        changed = True
    if changed:
        user.save(update_fields=['first_name', 'last_name'])


def _unique_username(User, base_username):
    clean_base = ''.join(ch for ch in base_username if ch.isalnum() or ch in ('_', '-')) or 'social_user'
    username = clean_base[:120]
    candidate = username
    suffix = 1
    while User.objects.filter(username=candidate).exists():
        suffix += 1
        candidate = f'{username[:115]}{suffix}'
    return candidate
