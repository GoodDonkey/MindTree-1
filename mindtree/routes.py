import os
from threading import Thread
from concurrent import futures

from flask import render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from mindtree import app, db, bcrypt
from mindtree.utils.DTO import PathDTO
from mindtree.models import User, Post
from mindtree.forms import RegistrationForm, LoginForm
from mindtree.thread import ThreadedAnalysis

path = PathDTO()  # 경로를 찾을 때 사용한다.

with futures.ThreadPoolExecutor() as executor:
    """ analyzer를 로드합니다.
    쓰레드 처리 하였지만 실질적으로 앱이 로드되려면 각 분석기가 모두 로드되어야 합니다.
    쓰레드 처리를 하지 않으면 두번 initializing되어서 이렇게 처리했습니다. """
    _analyzer = ThreadedAnalysis()
    analyzer = executor.submit(_analyzer.init_analyzers).result()


@app.route("/my_diary", methods=['GET'])
@login_required
def my_diary():
    username = current_user.username
    posts = Post.query.filter_by(author=current_user).all()
    print("[my_diary] username: ", username)
    return render_template('my_diary.html', posts=posts)


@app.route("/upload", methods=['GET'])
@login_required
def upload():
    return render_template('upload.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('my_diary'))
    form = RegistrationForm()
    if request.method == "POST":
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash("계정이 생성되었습니다. 로그인할 수 있습니다.", 'success')  # username으로 들어온 인풋을 data로 받을 수 있다.
            return redirect(url_for('login'))
        else:
            flash("입력정보가 적절하지 않습니다. 다시 시도해주세요", 'danger')  # username으로 들어온 인풋을 data로 받을 수 있다.
    return render_template('register.html', title='Register', form=form)


@app.route("/",  methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            try:
                user = User.query.filter_by(email=form.email.data).first()
                # db의 password와 form의 password를 비교하여 True, False를 반환함
                if user and bcrypt.check_password_hash(user.password, form.password.data):
                    login_user(user, remember=form.remember.data)
                    next_page = request.args.get('next')  # arg: get method일때 주소에서 'next'키(key)에 대한 값(value)을 가져온다. 없으면 none

                    return redirect(next_page) if next_page else redirect(url_for('my_diary'))
                else:
                    flash('로그인 실패. email 또는 password를 다시 확인해 주세요.', 'danger')
            except Exception as e:
                print("[login] 쿼리 실패", e)
        else:
            flash('입력정보가 올바르지 않습니다.', 'danger')
    return render_template('login.html', title='login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/analyze/<int:post_id>')
@login_required
def analyze(post_id):
    """
    - 해당 포스트 아이디로 쿼리 후 결과가 없으면 보내지 않게 하기 """

    post = Post.query.get_or_404(post_id)

    return render_template('analyze.html', post=post)


@app.route("/results/<path:post_id>", methods=['GET'])
def get_word_cloud_file(post_id):
    """ word cloud가 저장된 미디어 폴더에 접근(results폴더)
    :param post_id: 포스트 id
    :return: 지정된 directory의 파일에 접근한다.
    """
    word_cloud_file_name = path.get_user_word_cloud_file_name(post_id)
    print("[get_word_cloud_file] word_cloud_file_name: ", word_cloud_file_name)
    return send_from_directory(path.get_user_media_path(post_id), word_cloud_file_name)


@app.route("/upload_file", methods=['GET', 'POST'])
def upload_file():
    """
    1. 요청한 파일을 업로드 하고 my_diary로 리다이렉트 한다.
    2. OCR, text mining, sentiment analysis를 수행하도록 처리한다.
    """
    if request.method == "POST":

        f = request.files['file']  # input 태그의 name 을 받음.
        print("[upload_file] f.filename, title", f.filename)

        # 현재 유저로 포스트를 db에 저장(빈 데이터를 저장하고, 각 분석이 끝나면 업데이트하는 방식)
        post = Post(title="", ocr_text='', sentiment={}, word_cloud="", author=current_user)
        db.session.add(post)
        db.session.commit()
        post_id: int = post.id

        # 경로 변수 정의
        filename = path.get_user_diary_file_name(post_id)
        file_dir = path.get_user_media_path(post_id)
        file_path = os.path.join(file_dir, filename)

        # 디렉토리 만들기
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir, exist_ok=True)

        # 이미지 저장
        f.save(file_path)

        flash("업로드에 성공하였습니다", "success")

        """ ** 업로드한 파일을 미리 분석해서 저장해둔다 **
        1. 1번이상 분석했다면, worker에 각 분석기가 초기화 되어 있으므로, 바로 분석함.
        2. 안되어있으면 초기화 후 분석 진행.
        단, app이 debug모드이기 때문에 reloading될 때마다 다시 초기화해야한다.
        """

        if analyzer.is_initialized():
            t1 = Thread(target=analyzer.analysis, args=[post_id])
            t1.start()
        else:
            t2 = Thread(target=analyzer.init_and_analyze, args=[post_id])
            t2.start()

        return redirect(url_for("my_diary"))

    else:
        return '실패'


@app.template_filter('datetime')
def _jinja2_filter_datetime(date, fmt=None):
    if fmt:
        return date.strftime(fmt)
    else:
        return date.strftime('%Y년 %m월 %d일 %H시 %M분')
