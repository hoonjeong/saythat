# SayThat - 토론으로 답을 찾다

SayThat은 다양한 주제에 대해 자유롭게 토론하고 의견을 나눌 수 있는 온라인 토론 플랫폼입니다.

## 주요 기능

- 📊 **찬반 투표 시스템** - 각 토론 주제에 대한 찬성/반대 의견 표시
- 💬 **댓글 토론** - 활발한 의견 교환을 위한 댓글 시스템
- 🔥 **인기 순위** - 실시간/일간/주간/월간 인기 토론 확인
- 🔐 **소셜 로그인** - Google, Kakao, Naver 계정으로 간편 가입
- 📱 **반응형 디자인** - 모바일과 데스크톱 모두 지원

## 기술 스택

- **Backend**: Flask (Python)
- **Database**: SQLite (SQLAlchemy ORM)
- **Authentication**: Flask-Login, OAuth 2.0
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Custom CSS with modern design

## 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/hoonjeong/saythat.git
cd saythat
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 열어 OAuth 클라이언트 ID와 Secret 설정
```

5. 애플리케이션 실행
```bash
python app.py
```

6. 브라우저에서 http://localhost:5000 접속

## OAuth 설정

실제 소셜 로그인을 사용하려면 각 플랫폼에서 OAuth 앱을 등록해야 합니다:

- **Google**: [Google Cloud Console](https://console.cloud.google.com/)
- **Kakao**: [Kakao Developers](https://developers.kakao.com/)
- **Naver**: [Naver Developers](https://developers.naver.com/)

## 프로젝트 구조

```
saythat/
├── app.py                 # 메인 애플리케이션
├── models.py             # 데이터베이스 모델
├── auth_routes.py        # 인증 관련 라우트
├── oauth_config.py       # OAuth 설정
├── templates/            # HTML 템플릿
│   ├── index.html       # 메인 페이지
│   └── login.html       # 로그인 페이지
├── static/              # 정적 파일
│   ├── css/            # 스타일시트
│   └── js/             # JavaScript
├── .env.example         # 환경 변수 예제
├── .gitignore          # Git 제외 파일
├── requirements.txt     # Python 패키지 목록
└── README.md           # 프로젝트 문서
```

## 라이선스

MIT License

## 기여

기여는 언제나 환영합니다! Pull Request를 보내주세요.