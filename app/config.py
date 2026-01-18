"""App configuration from environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration - supports both local and AWS RDS environment variables
    # AWS EB with RDS sets: RDS_HOSTNAME, RDS_PORT, RDS_USERNAME, RDS_PASSWORD, RDS_DB_NAME
    # For manual config, use: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
    DB_HOST = os.environ.get('RDS_HOSTNAME') or os.environ.get('DB_HOST', 'awseb-e-axxpyrp6jn-stack-awsebrdsdatabase-zdcptgsoelxx.cfaao2wyugtt.il-central-1.rds.amazonaws.com')
    DB_PORT = int(os.environ.get('RDS_PORT') or os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('RDS_USERNAME') or os.environ.get('DB_USER', 'flytauadmin')
    DB_PASSWORD = os.environ.get('RDS_PASSWORD') or os.environ.get('DB_PASSWORD', 'FlytauPass1234')
    DB_NAME = os.environ.get('RDS_DB_NAME') or os.environ.get('DB_NAME', 'flytau')
    DB_POOL_SIZE = int(os.environ.get('DB_POOL_SIZE', 5))
    DB_POOL_NAME = 'flytau_pool'
    
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    
    # In production, SECRET_KEY must be set via environment variable
    @property
    def SECRET_KEY(self):
        key = os.environ.get('SECRET_KEY')
        if not key:
            raise ValueError("SECRET_KEY environment variable must be set in production")
        return key


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DB_NAME = os.environ.get('TEST_DB_NAME', 'flytau_test')


# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
