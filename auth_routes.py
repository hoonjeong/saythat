from flask import Blueprint, redirect, url_for, session, request, jsonify
from flask_login import login_user, logout_user, login_required
from authlib.integrations.flask_client import OAuth
from models import User, db
import json
import requests
from oauth_config import OAuthConfig

auth_bp = Blueprint('auth', __name__)

def init_oauth(app):
    oauth = OAuth(app)
    
    # Google OAuth 설정
    oauth.register(
        name='google',
        client_id=OAuthConfig.GOOGLE_CLIENT_ID,
        client_secret=OAuthConfig.GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    
    # Kakao OAuth 설정
    oauth.register(
        name='kakao',
        client_id=OAuthConfig.KAKAO_CLIENT_ID,
        client_secret=OAuthConfig.KAKAO_CLIENT_SECRET,
        authorize_url=OAuthConfig.KAKAO_AUTHORIZE_URL,
        access_token_url=OAuthConfig.KAKAO_ACCESS_TOKEN_URL,
        client_kwargs={
            'scope': 'profile_nickname profile_image account_email'
        }
    )
    
    # Naver OAuth 설정
    oauth.register(
        name='naver',
        client_id=OAuthConfig.NAVER_CLIENT_ID,
        client_secret=OAuthConfig.NAVER_CLIENT_SECRET,
        authorize_url=OAuthConfig.NAVER_AUTHORIZE_URL,
        access_token_url=OAuthConfig.NAVER_ACCESS_TOKEN_URL,
        client_kwargs={
            'scope': 'name email'
        }
    )
    
    return oauth

# Google 로그인
@auth_bp.route('/auth/google')
def google_login():
    # 실제 구현시 OAuth 클라이언트 ID와 Secret이 필요합니다
    # 여기서는 데모를 위한 모의 구현입니다
    return redirect(url_for('auth.oauth_callback', provider='google'))

@auth_bp.route('/auth/google/callback')
def google_callback():
    # Google OAuth 콜백 처리
    # 실제 구현시 Google에서 받은 사용자 정보로 처리
    demo_user_info = {
        'email': 'demo@google.com',
        'name': 'Google 사용자',
        'picture': None,
        'id': 'google_123456'
    }
    return handle_oauth_callback('google', demo_user_info)

# Kakao 로그인
@auth_bp.route('/auth/kakao')
def kakao_login():
    # 실제 구현시 Kakao OAuth 설정이 필요합니다
    return redirect(url_for('auth.oauth_callback', provider='kakao'))

@auth_bp.route('/auth/kakao/callback')
def kakao_callback():
    # Kakao OAuth 콜백 처리
    demo_user_info = {
        'email': 'demo@kakao.com',
        'name': '카카오 사용자',
        'picture': None,
        'id': 'kakao_123456'
    }
    return handle_oauth_callback('kakao', demo_user_info)

# Naver 로그인
@auth_bp.route('/auth/naver')
def naver_login():
    # 실제 구현시 Naver OAuth 설정이 필요합니다
    return redirect(url_for('auth.oauth_callback', provider='naver'))

@auth_bp.route('/auth/naver/callback')
def naver_callback():
    # Naver OAuth 콜백 처리
    demo_user_info = {
        'email': 'demo@naver.com',
        'name': '네이버 사용자',
        'picture': None,
        'id': 'naver_123456'
    }
    return handle_oauth_callback('naver', demo_user_info)

# OAuth 콜백 공통 처리 (데모용)
@auth_bp.route('/auth/<provider>/demo')
def oauth_callback(provider):
    # 데모를 위한 임시 사용자 정보
    demo_users = {
        'google': {
            'email': f'demo_{provider}@gmail.com',
            'name': 'Google 데모 사용자',
            'picture': None,
            'id': f'{provider}_demo_123'
        },
        'kakao': {
            'email': f'demo_{provider}@kakao.com',
            'name': '카카오 데모 사용자',
            'picture': None,
            'id': f'{provider}_demo_456'
        },
        'naver': {
            'email': f'demo_{provider}@naver.com',
            'name': '네이버 데모 사용자',
            'picture': None,
            'id': f'{provider}_demo_789'
        }
    }
    
    user_info = demo_users.get(provider, demo_users['google'])
    return handle_oauth_callback(provider, user_info)

def handle_oauth_callback(provider, user_info):
    """OAuth 콜백 처리 공통 함수"""
    # 사용자 정보로 User 객체 생성 또는 조회
    user = User.query.filter_by(
        provider=provider,
        provider_id=user_info['id']
    ).first()
    
    if not user:
        # 새 사용자 생성
        user = User(
            email=user_info['email'],
            name=user_info['name'],
            provider=provider,
            provider_id=user_info['id'],
            profile_pic=user_info.get('picture')
        )
        db.session.add(user)
        db.session.commit()
    
    # 로그인 처리
    login_user(user, remember=True)
    
    # 이전 페이지로 리다이렉트 또는 메인 페이지로
    next_page = request.args.get('next')
    return redirect(next_page) if next_page else redirect(url_for('index'))