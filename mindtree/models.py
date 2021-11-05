from datetime import datetime
from mindtree import db, login_manager
from flask_login import UserMixin
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from pytz import timezone


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    # id의 db.Integer는 자동증가 설정 안해줘도 primary_key면 자동 삽입됨.
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    date_joined = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone('Asia/Seoul')))
    posts = db.relationship('Post', backref='author', lazy=True)  # 해당 유저의 모든 포스트 연결
    series_posts = db.relationship('SeriesPost', backref='author', lazy=True)  # 해당 유저의 모든 포스트 연결

    # 토큰 발행하기 (현재 User객체에 대해서)
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)  # secret키를 넣어 serializer를 초기화한다.
        return s.dumps({'user_id': self.id}).decode('utf-8')  # 위 serializer로 토큰을 생성해 반환한다.

    # 발행한 토큰
    @staticmethod  # 이 decorator로 아래 method가 self가 없는 method 임을 명시해준다.
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']  # 토큰에서 user_id를 뽑아냄
        except Exception as e:
            return e
        return User.query.get(user_id)  # try에서 뽑아낸 user_id를 db에서 select하여 반환한다.

    def __repr__(self):
        return f"User('{self.id}', '{self.username}', '{self.email}')"


class CustomNow(datetime):
    """ 기존에 시간 관련 칼럼에 한국 시간대를 적용하기 위해
    datetime.now(timezone('Asia/Seoul'))로 넣어봤으나, 시간이 바뀌어 들어가긴 하는데 제대로 안바뀜.
    또한, pagination등을 할 때 datetime객체(?)로 인식이 안됨. -> now()로 메서드를 실행해서 넣어서 그런듯(...라고 예상)
    그래서 메서드를 직접 실행하지 않고 전달하기 위해 timezone 정보를 오버라이딩해서 CustomNow.now를 정의하여 넣어주니까 정상작동 되었음."""
    @classmethod
    def now(cls, tz=timezone('Asia/Seoul')):
        return super().now()


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 자동 증가
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 참조: 'author'키로
    title = db.Column(db.String(100), nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=CustomNow.now)  # 자동 입력됨
    last_updated = db.Column(db.DateTime, nullable=True, default=CustomNow.now, onupdate=CustomNow.now)
    ocr_text = db.Column(db.String(500), nullable=False)
    sentiment = db.Column(db.JSON, nullable=False)
    word_cloud = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, nullable=True, default=False)
    error = db.Column(db.Boolean, nullable=True, default=False)

    def __repr__(self):
        return f"Post('{self.id}', '{self.user_id}', '{self.pub_date}',\n'{self.last_updated}', \n" \
               f"'{self.ocr_text}',\n" \
               f" '{self.sentiment}', \n'{self.word_cloud}', \n'{self.completed}'  )" # , \n " \
                # f" '{self.stacked_bar_chart}' )"


class SeriesPost(db.Model):  # 여러날의 포스트를 분석하여 저장하는 테이블
    id = db.Column(db.Integer, primary_key=True)  # 자동 증가
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 참조: 'author'키로
    title = db.Column(db.String(100), nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=CustomNow.now)  # 자동 입력됨
    last_updated = db.Column(db.DateTime, nullable=True, default=CustomNow.now, onupdate=CustomNow.now)
    ocr_text_bulk = db.Column(db.String(500), nullable=False)
    sentiment = db.Column(db.JSON, nullable=False)
    word_cloud = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, nullable=True, default=False)
    error = db.Column(db.Boolean, nullable=True, default=False)

    def __repr__(self):
        return f"SeriesPost('{self.id}', '{self.user_id}', '{self.pub_date}',\n'{self.last_updated}', \n" \
               f"'{self.ocr_text_bulk}',\n" \
               f" '{self.sentiment}', \n'{self.word_cloud}', \n'{self.completed}', \n'{self.error}')"
