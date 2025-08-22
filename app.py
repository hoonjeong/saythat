from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash, make_response
from datetime import datetime, timedelta, date
import os
import secrets
import pymysql
from dotenv import load_dotenv

# Import models and configurations
from models import db, STContent, STComment, STUser, STLevel, STAutoLogin, STVoteRecord, STViewRecord
from config import Config, config
from utils import (get_session_id, add_points, get_user_level_info, 
                   check_vote_record, save_vote_record, require_login, handle_db_errors)

# Initialize
pymysql.install_as_MySQLdb()
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])
app.config['SQLALCHEMY_DATABASE_URI'] = Config.get_database_uri()
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Initialize extensions
db.init_app(app)


@app.route('/')
def index():
    # 최신 토론들 가져오기
    discussions = STContent.query.order_by(STContent.insert_time.desc()).limit(Config.RECENT_DISCUSSIONS_LIMIT).all()
    
    # 현재 사용자의 레벨 정보 가져오기
    user_level = None
    if session.get('user_id'):
        user_level = get_user_level_info(session['user_id'])
    
    return render_template('index.html', discussions=discussions, user_level=user_level)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/logout')
def logout():
    # 자동 로그인 토큰 삭제
    if session.get('user_id'):
        STAutoLogin.query.filter_by(user_id=session['user_id']).delete()
        db.session.commit()
    
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/check-email', methods=['POST'])
def check_email():
    try:
        email = request.json.get('email')
        existing = STUser.query.filter_by(email=email).first()
        return jsonify({'available': existing is None})
    except Exception as e:
        return jsonify({'available': False, 'error': str(e)}), 500

@app.route('/api/check-nick', methods=['POST'])
def check_nick():
    try:
        nick = request.json.get('nick')
        existing = STUser.query.filter_by(nick=nick).first()
        return jsonify({'available': existing is None})
    except Exception as e:
        return jsonify({'available': False, 'error': str(e)}), 500

@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        email = data.get('email')
        nick = data.get('nick')
        password = data.get('password')
        
        # 중복 확인
        if STUser.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': '이미 사용중인 이메일입니다.'}), 400
        
        if STUser.query.filter_by(nick=nick).first():
            return jsonify({'success': False, 'message': '이미 사용중인 활동명입니다.'}), 400
        
        # 새 사용자 생성
        new_user = STUser(
            email=email,
            nick=nick,
            pw=STUser.hash_password(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # 레벨 테이블 초기화
        new_level = STLevel(user_id=new_user.id, point=0)
        db.session.add(new_level)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '회원가입이 완료되었습니다.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        auto_login = data.get('auto_login', False)
        
        user = STUser.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_nick'] = user.nick
            session['user_email'] = user.email
            
            response_data = {'success': True}
            
            # 자동 로그인 요청 시 토큰 생성
            if auto_login:
                # 기존 토큰 삭제
                STAutoLogin.query.filter_by(user_id=user.id).delete()
                
                # 새 토큰 생성
                token = secrets.token_urlsafe(32)
                expiry = datetime.utcnow() + timedelta(days=30)
                
                auto_login_entry = STAutoLogin(
                    user_id=user.id,
                    token=token,
                    expiry=expiry
                )
                db.session.add(auto_login_entry)
                db.session.commit()
                
                response_data['auto_login_token'] = token
            
            return jsonify(response_data)
        else:
            return jsonify({'success': False, 'message': '이메일 또는 비밀번호가 올바르지 않습니다.'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/auto-login', methods=['POST'])
def api_auto_login():
    try:
        data = request.get_json()
        email = data.get('email')
        token = data.get('token')
        
        # 토큰 확인
        auto_login = STAutoLogin.query.filter_by(token=token).first()
        
        if auto_login and auto_login.user.email == email:
            # 만료 시간 확인
            if auto_login.expiry > datetime.utcnow():
                user = auto_login.user
                session['user_id'] = user.id
                session['user_nick'] = user.nick
                session['user_email'] = user.email
                
                # 토큰 갱신 (만료 시간 연장)
                auto_login.expiry = datetime.utcnow() + timedelta(days=30)
                db.session.commit()
                
                return jsonify({'success': True})
            else:
                # 만료된 토큰 삭제
                db.session.delete(auto_login)
                db.session.commit()
                return jsonify({'success': False, 'message': '자동 로그인 토큰이 만료되었습니다.'}), 401
        else:
            return jsonify({'success': False, 'message': '유효하지 않은 자동 로그인 정보입니다.'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/reset-password', methods=['POST'])
@handle_db_errors
def reset_password():
    import string
    import logging
    
    email = request.json.get('email')
    user = STUser.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({'success': False, 'message': '등록되지 않은 이메일입니다.'}), 404
    
    # 임시 비밀번호 생성 (cryptographically secure)
    temp_password = secrets.token_urlsafe(8)
    user.pw = STUser.hash_password(temp_password)
    db.session.commit()
    
    # TODO: 실제 환경에서는 이메일 전송 서비스 구현 필요
    logging.info(f"Password reset requested for {email}")
    # 개발 환경에서만 콘솔 출력
    if Config.DEBUG:
        logging.info(f"Temporary password: {temp_password}")
    
    return jsonify({'success': True, 'message': '임시 비밀번호가 발급되었습니다.'})

@app.route('/new-discussion')
def new_discussion():
    if not session.get('user_id'):
        flash('로그인이 필요합니다.')
        return redirect(url_for('login'))
    
    # 현재 사용자의 레벨 정보 가져오기
    user_level = get_user_level_info(session['user_id'])
    
    return render_template('new_discussion.html', user_level=user_level)

@app.route('/api/save-discussion', methods=['POST'])
def save_discussion():
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    try:
        data = request.get_json()
        
        if not data.get('subject') or not data.get('content'):
            return jsonify({'success': False, 'message': '제목과 내용을 모두 입력해주세요.'}), 400
        
        new_content = STContent(
            subject=data['subject'],
            content=data['content'],
            user_id=session['user_id']
        )
        
        db.session.add(new_content)
        db.session.commit()
        
        # 글 작성 포인트
        add_points(session['user_id'], Config.POINTS_FOR_POST, "글 작성")
        
        return jsonify({
            'success': True,
            'message': '토론이 성공적으로 저장되었습니다.',
            'id': new_content.id
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/discussion/<int:id>')
def view_discussion(id):
    discussion = STContent.query.get_or_404(id)
    
    # 조회수 증가 (하루에 한 번만)
    today = date.today()
    user_id = session.get('user_id')
    session_id = get_session_id(session) if not user_id else None
    
    # 오늘 이미 조회했는지 확인
    existing_view = None
    if user_id:
        existing_view = STViewRecord.query.filter_by(
            user_id=user_id,
            content_id=id,
            view_date=today
        ).first()
    elif session_id:
        existing_view = STViewRecord.query.filter_by(
            session_id=session_id,
            content_id=id,
            view_date=today
        ).first()
    
    # 오늘 첫 조회인 경우에만 조회수 증가
    if not existing_view:
        try:
            # 조회 기록 저장
            view_record = STViewRecord(
                user_id=user_id,
                session_id=session_id,
                content_id=id,
                view_date=today
            )
            db.session.add(view_record)
            
            # 조회수 증가
            discussion.view_count += 1
            db.session.commit()
        except Exception as e:
            # 중복 조회 시도 (동시성 문제로 인한 예외 처리)
            db.session.rollback()
    
    # 투표 기록 확인
    voted = None
    session_id = get_session_id(session) if not session.get('user_id') else None
    vote_record = check_vote_record(session.get('user_id'), session_id, content_id=id)
    if vote_record:
        voted = "찬성" if vote_record.vote_type == 'chan' else "반대"
    
    # 댓글 정렬 (기본: 추천순)
    sort_order = request.args.get('sort', 'best')
    
    if sort_order == 'newest':
        # 최신순 - 데이터베이스에서 정렬
        comments = STComment.query.filter_by(content_id=id)\
                          .order_by(STComment.insert_time.desc()).all()
    else:
        # 추천순 - 데이터베이스에서 점수 계산 후 정렬
        from sqlalchemy import desc, case
        
        # 점수별로 정렬 (vote_plus - vote_minus)
        comments = STComment.query.filter_by(content_id=id)\
                          .order_by(desc(STComment.vote_plus - STComment.vote_minus),
                                  desc(STComment.insert_time)).all()
        
        # 베스트 댓글 마킹
        for i, comment in enumerate(comments):
            comment.is_best = i < Config.BEST_COMMENTS_COUNT
    
    # 작성자 확인
    is_author = (session.get('user_id') == discussion.user_id) if session.get('user_id') else False
    
    # 현재 사용자의 레벨 정보 가져오기
    user_level = None
    if session.get('user_id'):
        user_level = get_user_level_info(session['user_id'])
    
    return render_template('view_discussion.html', 
                         discussion=discussion, 
                         voted=voted,
                         comments=comments,
                         is_author=is_author,
                         sort_order=sort_order,
                         best_count=3 if sort_order == 'best' else 0,
                         user_level=user_level)

@app.route('/api/vote/<int:id>', methods=['POST'])
def vote_discussion(id):
    try:
        discussion = STContent.query.get_or_404(id)
        vote_type = request.json.get('vote_type')
        
        # 자기 글인지 확인
        if session.get('user_id') and session['user_id'] == discussion.user_id:
            return jsonify({'success': False, 'message': '자신이 작성한 글에는 투표할 수 없습니다.'}), 400
        
        # 중복 투표 확인
        session_id = get_session_id(session) if not session.get('user_id') else None
        existing_vote = check_vote_record(session.get('user_id'), session_id, content_id=id)
        
        if existing_vote:
            voted_text = "찬성" if existing_vote.vote_type == 'chan' else "반대"
            return jsonify({'success': False, 'message': f'이미 {voted_text}를 누르셨습니다.'}), 400
        
        # 투표자의 레벨에 따른 가중치 계산
        voting_power = 1
        if session.get('user_id'):
            voter_level = get_user_level_info(session['user_id'])
            if voter_level:
                voting_power = voter_level.voting_power
        
        if vote_type == 'chan':
            discussion.chan += voting_power
        elif vote_type == 'ban':
            discussion.ban += voting_power
        else:
            return jsonify({'success': False, 'message': '잘못된 투표 타입'}), 400
        
        # 투표 기록 저장
        save_vote_record(session.get('user_id'), session_id, vote_type, content_id=id)
        
        # 글 작성자에게 투표 포인트
        if discussion.user_id:
            add_points(discussion.user_id, Config.POINTS_FOR_VOTE_RECEIVED, "내 글에 투표")
        
        return jsonify({'success': True, 'message': '투표가 완료되었습니다.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/save-comment', methods=['POST'])
def save_comment():
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    try:
        data = request.get_json()
        
        if not data.get('content'):
            return jsonify({'success': False, 'message': '댓글 내용을 입력해주세요.'}), 400
        
        new_comment = STComment(
            content=data['content'],
            content_id=data['content_id'],
            chanban=data.get('chanban', 0),
            user_id=session['user_id']
        )
        
        db.session.add(new_comment)
        db.session.commit()
        
        # 댓글 작성 포인트
        add_points(session['user_id'], Config.POINTS_FOR_COMMENT, "댓글 작성")
        
        # 글 작성자에게 댓글 포인트 +1
        discussion = STContent.query.get(data['content_id'])
        if discussion and discussion.user_id != session['user_id']:
            add_points(discussion.user_id, 1, "내 글에 댓글")
        
        return jsonify({'success': True, 'message': '댓글이 저장되었습니다.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/edit-discussion/<int:id>')
def edit_discussion(id):
    if not session.get('user_id'):
        flash('로그인이 필요합니다.')
        return redirect(url_for('login'))
    
    discussion = STContent.query.get_or_404(id)
    # 작성자 확인
    if discussion.user_id != session['user_id']:
        flash('수정 권한이 없습니다.')
        return redirect(url_for('view_discussion', id=id))
    return render_template('edit_discussion.html', discussion=discussion)

@app.route('/api/update-discussion/<int:id>', methods=['POST'])
def update_discussion(id):
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    try:
        discussion = STContent.query.get_or_404(id)
        # 작성자 확인
        if discussion.user_id != session['user_id']:
            return jsonify({'success': False, 'message': '수정 권한이 없습니다.'}), 403
        
        data = request.get_json()
        discussion.subject = data.get('subject', discussion.subject)
        discussion.content = data.get('content', discussion.content)
        
        db.session.commit()
        return jsonify({'success': True, 'message': '수정되었습니다.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/delete-discussion/<int:id>', methods=['POST'])
@require_login
@handle_db_errors
def delete_discussion(id):
    try:
        discussion = STContent.query.get_or_404(id)
        # 작성자 확인
        if discussion.user_id != session['user_id']:
            return jsonify({'success': False, 'message': '삭제 권한이 없습니다.'}), 403
        
        # 댓글들도 함께 삭제
        STComment.query.filter_by(content_id=id).delete()
        db.session.delete(discussion)
        db.session.commit()
        
        # 세션에서 작성자 정보 제거
        session.pop(f'author_{id}', None)
        
        return jsonify({'success': True, 'message': '삭제되었습니다.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/vote-comment/<int:comment_id>', methods=['POST'])
def vote_comment(comment_id):
    try:
        comment = STComment.query.get_or_404(comment_id)
        vote_type = request.json.get('vote_type')
        
        # 자기 댓글인지 확인
        if session.get('user_id') and session['user_id'] == comment.user_id:
            return jsonify({'success': False, 'message': '자신이 작성한 댓글에는 투표할 수 없습니다.'}), 400
        
        # 중복 투표 확인
        session_id = get_session_id(session) if not session.get('user_id') else None
        existing_vote = check_vote_record(session.get('user_id'), session_id, comment_id=comment_id)
        
        if existing_vote:
            return jsonify({'success': False, 'message': '이미 투표하셨습니다.'}), 400
        
        # 투표자의 레벨에 따른 가중치 계산
        voting_power = 1
        if session.get('user_id'):
            voter_level = get_user_level_info(session['user_id'])
            if voter_level:
                voting_power = voter_level.voting_power
        
        if vote_type == 'plus':
            comment.vote_plus += voting_power
            # 댓글 작성자에게 추천 포인트
            if comment.user_id:
                add_points(comment.user_id, Config.POINTS_FOR_COMMENT_UPVOTE, "내 댓글에 추천")
        elif vote_type == 'minus':
            comment.vote_minus += voting_power
        else:
            return jsonify({'success': False, 'message': '잘못된 투표 타입'}), 400
        
        # 투표 기록 저장
        save_vote_record(session.get('user_id'), session_id, vote_type, comment_id=comment_id)
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500



def init_db():
    with app.app_context():
        db.create_all()  # 테이블이 없을 때만 생성

if __name__ == '__main__':
    init_db()
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)