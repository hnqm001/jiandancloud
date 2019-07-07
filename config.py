import os
import sys
basedir = os.path.abspath(os.path.dirname(__file__))

# SQLite URI 判断兼容系统
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
    AVATARS_SAVE_PATH = os.path.join(basedir, 'app\\static\\images\\avatars')
else:
    prefix = 'sqlite:////'
    AVATARS_SAVE_PATH = os.path.join(basedir, 'app/static/images/avatars')


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.139.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '465'))
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    JIANDANCLOUD_MAIL_SUBJECT_PREFIX = '[JIANDANCLOUD]'
    JIANDANCLOUD_MAIL_SENDER = 'JiandanCloud Admin <ztxc007@139.com>'
    # 管理员邮箱地址
    JIANDANCLOUD_ADMIN = os.environ.get('JIANDANCLOUD_ADMIN')
    # 如果设置成 True (默认情况)，Flask-SQLAlchemy 将会追踪对象的修改并且发送信号
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 可以用于显式地禁用或者启用查询记录
    SQLALCHEMY_RECORD_QUERIES = True

    JIANDANCLOUD_POSTS_PER_PAGE = 15
    JIANDANCLOUD_FOLLOWERS_PER_PAGE = 25
    JIANDANCLOUD_COMMENTS_PER_PAGE = 20
    # 设置上传路径
    UPLOAD_PATH = os.path.join(basedir, 'uploads')
    # 设置最大文件上传大小，单位字节
    MAX_CONTENT_LENGTH = 300 * 1024 * 1024

    # Flask-Dropzone 配置:
    DROPZONE_SERVE_LOCAL = True
    DROPZONE_ALLOWED_FILE_CUSTOM = True
    DROPZONE_ALLOWED_FILE_TYPE = 'image/*,.txt,.dbf,.pdf,.xls,.xlsx, \
    .doc,.docx,.ppt,.pptx,.zip,.rar,.7z,.csv,.mp4,.avi'
    DROPZONE_MAX_FILE_SIZE = 300
    DROPZONE_MAX_FILES = 10
    DROPZONE_ENABLE_CSRF = True  # enable CSRF protection
    DROPZONE_DEFAULT_MESSAGE = '点击框内选择需上传的文件，或者直接拖动文件到框内下载'
    DROPZONE_INVALID_FILE_TYPE = '不能上传该类型文件'
    DROPZONE_TIMEOUT = 5 * 60 * 1000

    # 头像配置
    AVATARS_SERVE_LOCAL = True

    AVATARS_SIZE_TUPLE = (16, 30, 200)
    AVATARS_IDENTICON_COLS = 7
    AVATARS_IDENTICON_ROWS = 7

    BAIDUMAP_AK = os.environ.get('BAIDUMAP_AK')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        prefix + os.path.join(basedir, 'data-dev.db')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        prefix


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        prefix + os.path.join(basedir, 'data.db')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
