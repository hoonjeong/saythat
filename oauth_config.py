import os
from dotenv import load_dotenv

load_dotenv()

class OAuthConfig:
    # Google OAuth 2.0 설정
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', 'temp-google-client-id')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', 'temp-google-secret')
    GOOGLE_AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/auth'
    GOOGLE_ACCESS_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
    GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'
    
    # Kakao OAuth 2.0 설정
    KAKAO_CLIENT_ID = os.environ.get('KAKAO_CLIENT_ID', 'temp-kakao-client-id')
    KAKAO_CLIENT_SECRET = os.environ.get('KAKAO_CLIENT_SECRET', 'temp-kakao-secret')
    KAKAO_AUTHORIZE_URL = 'https://kauth.kakao.com/oauth/authorize'
    KAKAO_ACCESS_TOKEN_URL = 'https://kauth.kakao.com/oauth/token'
    KAKAO_USERINFO_URL = 'https://kapi.kakao.com/v2/user/me'
    
    # Naver OAuth 2.0 설정
    NAVER_CLIENT_ID = os.environ.get('NAVER_CLIENT_ID', 'temp-naver-client-id')
    NAVER_CLIENT_SECRET = os.environ.get('NAVER_CLIENT_SECRET', 'temp-naver-secret')
    NAVER_AUTHORIZE_URL = 'https://nid.naver.com/oauth2.0/authorize'
    NAVER_ACCESS_TOKEN_URL = 'https://nid.naver.com/oauth2.0/token'
    NAVER_USERINFO_URL = 'https://openapi.naver.com/v1/nid/me'