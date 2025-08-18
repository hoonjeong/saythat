from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import os
import secrets
from models import db, User, Topic
from auth_routes import auth_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///saythat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Blueprint 등록
app.register_blueprint(auth_bp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/api/topics')
def get_topics():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    
    topics = Topic.query.order_by(Topic.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    topics_data = []
    for topic in topics.items:
        topics_data.append({
            'id': topic.id,
            'title': topic.title,
            'author': topic.author,
            'created_at': topic.created_at.strftime('%Y-%m-%d %H:%M'),
            'agree_percent': topic.agree_percent,
            'disagree_percent': topic.disagree_percent,
            'total_votes': topic.total_votes,
            'views': topic.views,
            'comments_count': topic.comments_count
        })
    
    return jsonify({
        'topics': topics_data,
        'has_next': topics.has_next,
        'page': page
    })

@app.route('/api/trending/<period>')
def get_trending(period):
    from datetime import datetime, timedelta
    
    if period == 'realtime':
        time_filter = datetime.utcnow() - timedelta(hours=1)
    elif period == 'today':
        time_filter = datetime.utcnow() - timedelta(days=1)
    elif period == 'weekly':
        time_filter = datetime.utcnow() - timedelta(weeks=1)
    elif period == 'monthly':
        time_filter = datetime.utcnow() - timedelta(days=30)
    else:
        return jsonify({'error': 'Invalid period'}), 400
    
    topics = Topic.query.filter(
        Topic.created_at >= time_filter
    ).order_by(
        (Topic.agree_votes + Topic.disagree_votes).desc()
    ).limit(5).all()
    
    trending_data = []
    for idx, topic in enumerate(topics, 1):
        trending_data.append({
            'rank': idx,
            'id': topic.id,
            'title': topic.title,
            'agree_votes': topic.agree_votes,
            'disagree_votes': topic.disagree_votes,
            'views': topic.views,
            'total_votes': topic.total_votes
        })
    
    return jsonify(trending_data)

@app.route('/api/vote/<int:topic_id>', methods=['POST'])
def vote(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    vote_type = request.json.get('vote_type')
    
    if vote_type == 'agree':
        topic.agree_votes += 1
    elif vote_type == 'disagree':
        topic.disagree_votes += 1
    else:
        return jsonify({'error': 'Invalid vote type'}), 400
    
    db.session.commit()
    
    return jsonify({
        'agree_percent': topic.agree_percent,
        'disagree_percent': topic.disagree_percent,
        'total_votes': topic.total_votes
    })

def init_db():
    with app.app_context():
        db.drop_all()  # 기존 테이블 삭제
        db.create_all()  # 새로운 스키마로 테이블 재생성
        
        if Topic.query.count() == 0:
            sample_topics = [
                {'title': '의대 정원 확대, 과연 필요한가?', 'author': '의료개혁추진', 'agree_votes': 2124, 'disagree_votes': 1297, 'views': 15200, 'comments_count': 847},
                {'title': 'AI가 인간의 일자리를 대체하는 것을 막아야 하는가?', 'author': '테크워커', 'agree_votes': 970, 'disagree_votes': 1186, 'views': 8700, 'comments_count': 523},
                {'title': '학교 체벌, 완전히 금지해야 하나?', 'author': '교육혁신21', 'agree_votes': 1476, 'disagree_votes': 416, 'views': 6300, 'comments_count': 412},
                {'title': '반려동물 등록제를 의무화해야 하는가?', 'author': '펫러버2024', 'agree_votes': 1098, 'disagree_votes': 136, 'views': 4100, 'comments_count': 287},
                {'title': '원자력 발전소를 더 늘려야 하는가?', 'author': '에너지전환', 'agree_votes': 503, 'disagree_votes': 484, 'views': 3200, 'comments_count': 198},
                {'title': '부동산 양도소득세를 완화해야 하는가?', 'author': '경제정책연구', 'agree_votes': 1222, 'disagree_votes': 1621, 'views': 12100, 'comments_count': 692},
                {'title': '대학 입시에서 정시 비중을 늘려야 하는가?', 'author': '교육평등실현', 'agree_votes': 1066, 'disagree_votes': 501, 'views': 7800, 'comments_count': 423},
                {'title': '전기차 보조금을 계속 지급해야 하는가?', 'author': '그린모빌리티', 'agree_votes': 633, 'disagree_votes': 259, 'views': 4500, 'comments_count': 234},
                {'title': '온라인 투표로 대통령 선거를 진행해도 되는가?', 'author': '디지털민주주의', 'agree_votes': 1163, 'disagree_votes': 2258, 'views': 18300, 'comments_count': 867},
                {'title': '최저임금을 대폭 인상해야 하는가?', 'author': '노동자권익', 'agree_votes': 2357, 'disagree_votes': 2175, 'views': 21700, 'comments_count': 1243},
            ]
            
            for topic_data in sample_topics:
                topic = Topic(**topic_data)
                db.session.add(topic)
            
            db.session.commit()
            print("Database initialized with sample data")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)