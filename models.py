from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib
from config import Config

db = SQLAlchemy()

class STContent(db.Model):
    __tablename__ = 'ST_CONTENT_TB'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('ST_USER_TB.id'), nullable=True, index=True)
    chan = db.Column(db.Integer, default=0)
    ban = db.Column(db.Integer, default=0)
    view_count = db.Column(db.Integer, default=0)
    insert_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    comments = db.relationship('STComment', backref='discussion', lazy=True)
    author = db.relationship('STUser', backref='discussions', lazy=True, foreign_keys='[STContent.user_id]')

class STComment(db.Model):
    __tablename__ = 'ST_COMMENT_TB'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('ST_USER_TB.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey('ST_CONTENT_TB.id'), nullable=False)
    chanban = db.Column(db.Integer, default=0)  # 0: 반대, 1: 찬성
    vote_plus = db.Column(db.Integer, default=0)
    vote_minus = db.Column(db.Integer, default=0)
    insert_time = db.Column(db.DateTime, default=datetime.utcnow)
    author = db.relationship('STUser', backref='comments', lazy=True, foreign_keys='[STComment.user_id]')

class STUser(db.Model):
    __tablename__ = 'ST_USER_TB'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    pw = db.Column(db.String(200), nullable=False)  # SHA1 암호화
    nick = db.Column(db.String(200), unique=True, nullable=False)
    insert_time = db.Column(db.DateTime, default=datetime.utcnow)
    level_info = db.relationship('STLevel', backref='user', uselist=False, lazy=True)
    
    @staticmethod
    def hash_password(password):
        return hashlib.sha1(password.encode()).hexdigest()
    
    def check_password(self, password):
        return self.pw == self.hash_password(password)

class STLevel(db.Model):
    __tablename__ = 'ST_LEVEL_TB'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('ST_USER_TB.id'), unique=True, nullable=False)
    point = db.Column(db.Integer, default=0)
    
    @property
    def level_name(self):
        thresholds = Config.LEVEL_THRESHOLDS
        if self.point < thresholds['bronze']:
            return "해골"
        elif self.point < thresholds['silver']:
            return "동메달"
        elif self.point < thresholds['gold']:
            return "은메달"
        elif self.point < thresholds['diamond']:
            return "금메달"
        else:
            return "다이아"
    
    @property
    def level_icon(self):
        thresholds = Config.LEVEL_THRESHOLDS
        if self.point < thresholds['bronze']:
            return "💀"
        elif self.point < thresholds['silver']:
            return "🥉"
        elif self.point < thresholds['gold']:
            return "🥈"
        elif self.point < thresholds['diamond']:
            return "🥇"
        else:
            return "💎"
    
    @property
    def voting_power(self):
        """레벨에 따른 투표 가중치"""
        thresholds = Config.LEVEL_THRESHOLDS
        power = Config.VOTING_POWER
        if self.point < thresholds['bronze']:
            return power['skull']
        elif self.point < thresholds['silver']:
            return power['bronze']
        elif self.point < thresholds['gold']:
            return power['silver']
        elif self.point < thresholds['diamond']:
            return power['gold']
        else:
            return power['diamond']

class STAutoLogin(db.Model):
    __tablename__ = 'ST_AUTO_LOGIN_TB'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('ST_USER_TB.id'), nullable=False)
    token = db.Column(db.String(200), unique=True, nullable=False)
    expiry = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('STUser', backref='auto_login_tokens', lazy=True)

class STVoteRecord(db.Model):
    __tablename__ = 'ST_VOTE_RECORD_TB'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('ST_USER_TB.id'), nullable=True, index=True)
    session_id = db.Column(db.String(200), nullable=True, index=True)
    content_id = db.Column(db.Integer, db.ForeignKey('ST_CONTENT_TB.id'), nullable=True, index=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('ST_COMMENT_TB.id'), nullable=True, index=True)
    vote_type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate votes
    __table_args__ = (
        db.UniqueConstraint('user_id', 'content_id', name='unique_user_content_vote'),
        db.UniqueConstraint('user_id', 'comment_id', name='unique_user_comment_vote'),
        db.UniqueConstraint('session_id', 'content_id', name='unique_session_content_vote'),
        db.UniqueConstraint('session_id', 'comment_id', name='unique_session_comment_vote'),
    )

class STViewRecord(db.Model):
    __tablename__ = 'ST_VIEW_RECORD_TB'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('ST_USER_TB.id'), nullable=True)
    session_id = db.Column(db.String(200), nullable=True)  # 비로그인 사용자용
    content_id = db.Column(db.Integer, db.ForeignKey('ST_CONTENT_TB.id'), nullable=False)
    view_date = db.Column(db.Date, nullable=False)  # 조회 날짜 (시간 제외)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to ensure one view per user/session per content per day
    __table_args__ = (
        db.UniqueConstraint('user_id', 'content_id', 'view_date', name='unique_user_content_view_date'),
        db.UniqueConstraint('session_id', 'content_id', 'view_date', name='unique_session_content_view_date'),
    )