# SayThat - 토론으로 답을 찾다

SayThat은 다양한 주제에 대해 자유롭게 토론하고 의견을 나눌 수 있는 온라인 토론 플랫폼입니다.

## 주요 기능

### 핵심 기능
- 📊 **찬반 투표 시스템** - 각 토론 주제에 대한 찬성/반대 의견 표시
- 💬 **댓글 토론** - 활발한 의견 교환을 위한 댓글 시스템
- 🔥 **인기 순위** - 실시간/일간/주간/월간 인기 토론 확인
- 📱 **반응형 디자인** - 모바일과 데스크톱 모두 지원

### 레벨 시스템
- **포인트 기반 5단계 레벨**
  - 💀 해골 (0~9,999 포인트)
  - 🥉 동메달 (10,000~99,999 포인트)
  - 🥈 은메달 (100,000~999,999 포인트)
  - 🥇 금메달 (1,000,000~9,999,999 포인트)
  - 💎 다이아 (10,000,000+ 포인트)

- **레벨별 투표 가중치**
  - 높은 레벨일수록 투표 영향력 증가 (1배~16배)
  - 포인트 어뷰징 방지 시스템

### 포인트 획득 방법
- 글 작성: +10 포인트
- 댓글 작성: +5 포인트
- 내 글/댓글이 추천받을 때: +1 포인트

### 보안 기능
- 세션 기반 인증 시스템
- 자동 로그인 (30일 유지)
- 이메일 저장 기능
- 중복 투표 방지
- 자기 글/댓글 투표 방지

## 기술 스택

- **Backend**: Flask (Python)
- **Database**: MySQL/SQLite (SQLAlchemy ORM)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Authentication**: Session-based with auto-login tokens
- **Styling**: Custom CSS with modern design

## 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/yourusername/saythat.git
cd saythat
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 열어 필요한 설정 수정
```

환경변수 예시:
```
FLASK_ENV=development
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here

# MySQL 설정 (선택사항, 없으면 SQLite 사용)
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_HOST=localhost
MYSQL_DATABASE=saythat_db
```

### 5. 애플리케이션 실행
```bash
python app.py
```

### 6. 브라우저에서 접속
```
http://localhost:5000
```

## 프로젝트 구조

```
saythat/
├── app.py              # 메인 애플리케이션
├── models.py           # 데이터베이스 모델
├── config.py           # 설정 및 상수
├── utils.py            # 유틸리티 함수
├── templates/          # HTML 템플릿
│   ├── index.html      # 메인 페이지
│   ├── login.html      # 로그인 페이지
│   ├── register.html   # 회원가입 페이지
│   ├── new_discussion.html    # 토론 작성
│   └── view_discussion.html   # 토론 보기
├── static/             # 정적 파일
│   ├── css/           # 스타일시트
│   └── js/            # JavaScript
├── instance/          # 인스턴스 폴더 (SQLite DB)
├── .env.example       # 환경 변수 예제
├── requirements.txt   # Python 패키지 목록
└── README.md         # 프로젝트 문서
```

## 주요 개선사항

### 최근 업데이트
- ✅ 레벨 시스템 구현 (포인트 기반 5단계)
- ✅ 투표 가중치 시스템 (레벨별 차등 적용)
- ✅ 자동 로그인 기능
- ✅ 이메일 저장 기능
- ✅ 세션 기반 투표 기록 (쿠키 대체)
- ✅ 툴팁 UI 개선 (레벨 정보 표시)
- ✅ 코드 리팩토링 및 최적화

### 보안 개선
- 환경변수를 통한 민감 정보 관리
- 세션 기반 인증으로 보안 강화
- 투표 기록 DB 저장으로 신뢰성 향상

## 라이선스

MIT License

## 기여

기여는 언제나 환영합니다! Pull Request를 보내주세요.

## 문의

프로젝트 관련 문의사항은 Issues를 통해 남겨주세요.