"""
Application configuration settings
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32).hex())
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database settings
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'saythat_db')
    
    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Voting settings
    VOTE_COOKIE_MAX_AGE = 30 * 24 * 60 * 60  # 30 days in seconds
    VIEW_COOKIE_MAX_AGE = 30 * 24 * 60 * 60  # 30 days in seconds
    
    # Auto-login settings
    AUTO_LOGIN_TOKEN_EXPIRY_DAYS = 30
    
    # Points system
    POINTS_FOR_POST = 10
    POINTS_FOR_COMMENT = 5
    POINTS_FOR_VOTE_RECEIVED = 1
    POINTS_FOR_COMMENT_UPVOTE = 1
    
    # Level thresholds (in points)
    LEVEL_THRESHOLDS = {
        'skull': 0,        # 해골 (💀)
        'bronze': 10000,   # 동메달 (🥉)
        'silver': 100000,  # 은메달 (🥈)
        'gold': 1000000,   # 금메달 (🥇)
        'diamond': 10000000 # 다이아 (💎)
    }
    
    # Voting power by level
    VOTING_POWER = {
        'skull': 1,
        'bronze': 2,
        'silver': 4,
        'gold': 8,
        'diamond': 16
    }
    
    # UI settings
    BEST_COMMENTS_COUNT = 3
    RECENT_DISCUSSIONS_LIMIT = 5
    
    # Server settings
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    
    @staticmethod
    def get_database_uri():
        """Get database URI with MySQL fallback to SQLite"""
        try:
            import pymysql
            # Test MySQL connection
            test_conn = pymysql.connect(
                host=Config.MYSQL_HOST,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD
            )
            cursor = test_conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DATABASE}")
            test_conn.close()
            
            return f'mysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_HOST}/{Config.MYSQL_DATABASE}'
        except Exception as e:
            print(f"MySQL connection failed: {e}. Falling back to SQLite.")
            return 'sqlite:///saythat.db'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}