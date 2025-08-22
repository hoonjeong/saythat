"""
Utility functions for the application
"""
from functools import wraps
from flask import jsonify, session
from models import db, STLevel, STVoteRecord
from config import Config
import secrets
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_session_id(session):
    """세션 ID를 가져오거나 생성"""
    if 'session_id' not in session:
        session['session_id'] = secrets.token_urlsafe(32)
    return session['session_id']

def add_points(user_id, points, reason=""):
    """사용자에게 포인트를 추가하는 함수"""
    if not user_id:
        return
    
    level = STLevel.query.filter_by(user_id=user_id).first()
    if not level:
        level = STLevel(user_id=user_id, point=0)
        db.session.add(level)
    
    level.point += points
    db.session.commit()
    logger.info(f"Added {points} points to user {user_id} for {reason}")

def get_user_level_info(user_id):
    """사용자의 레벨 정보를 가져오는 함수"""
    if not user_id:
        return None
    
    level = STLevel.query.filter_by(user_id=user_id).first()
    if not level:
        level = STLevel(user_id=user_id, point=0)
        db.session.add(level)
        db.session.commit()
    
    return level

def check_vote_record(user_id, session_id, content_id=None, comment_id=None):
    """투표 기록 확인"""
    if user_id:
        query = STVoteRecord.query.filter_by(user_id=user_id)
    else:
        query = STVoteRecord.query.filter_by(session_id=session_id)
    
    if content_id:
        query = query.filter_by(content_id=content_id)
    if comment_id:
        query = query.filter_by(comment_id=comment_id)
    
    return query.first()

def save_vote_record(user_id, session_id, vote_type, content_id=None, comment_id=None):
    """투표 기록 저장"""
    vote_record = STVoteRecord(
        user_id=user_id,
        session_id=session_id if not user_id else None,
        content_id=content_id,
        comment_id=comment_id,
        vote_type=vote_type
    )
    db.session.add(vote_record)
    db.session.commit()
    return vote_record

def require_login(f):
    """로그인 필수 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
        return f(*args, **kwargs)
    return decorated_function

def handle_db_errors(f):
    """데이터베이스 에러 처리 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error in {f.__name__}: {str(e)}")
            return jsonify({'success': False, 'message': '서버 오류가 발생했습니다.'}), 500
    return decorated_function