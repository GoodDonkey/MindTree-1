import os
from threading import Thread
from concurrent import futures
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, send_from_directory, abort
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from mindtree import app, db, bcrypt, Apps
from mindtree.utils.DTO import PathDTO
from mindtree.models import User, Post, SeriesPost
from mindtree.forms import RegistrationForm, LoginForm
from mindtree.thread import ThreadedAnalysis

path = PathDTO()  # 경로를 찾을 때 사용한다.


@app.before_first_request
def initialize():
    _analyzer = ThreadedAnalysis()
    Apps.analyzer = _analyzer.init_analyzers()


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('cover.html', title='cover')


@app.route("/post/my_diary", methods=['GET'])
@login_required
def my_diary():
    # 이름 확인용
    username = current_user.username
    print("[my_diary] username: ", username)

    # 포스트들을 페이지 정보를 담아 보낸다.
    page = request.args.get('page', 1, type=int)  # url에 /my_diary?page=1 과 같이 표기된 정보를 받음.
    posts = Post.query.filter_by(author=current_user) \
        .order_by(Post.pub_date.desc()) \
        .paginate(page=page, per_page=10)

    return render_template('my_diary.html', posts=posts)


@app.route("/post/upload", methods=['GET'])
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
                    next_page = request.args.get(
                            'next')  # arg: get method일때 주소에서 'next'키(key)에 대한 값(value)을 가져온다. 없으면 none

                    return redirect(next_page) if next_page else redirect(url_for('my_diary'))
                else:
                    flash('로그인 실패. email 또는 password를 다시 확인해 주세요.', 'danger')
            except Exception as e:
                print("[login] 쿼리 실패", e)
        else:
            flash('입력정보가 올바르지 않습니다.', 'danger')
    return render_template('login.html', title='login', form=form)


@app.route('/face_login')
def face_login():
    return render_template("face_login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/post/<int:post_id>/analyze')
@login_required
def analyze(post_id):
    """
    - 해당 포스트 아이디로 쿼리 후 결과가 없으면 보내지 않게 하기 """

    post = Post.query.get_or_404(post_id)

    return render_template('analyze.html', post=post)# post라는 키로 post라는 데이터를 보내주는건데, 위에 post를 말한다.


@app.route('/post/<int:post_id>/delete', methods=["POST"])
@login_required
def delete_post(post_id):
    """ 포스트를 삭제한다. """
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("포스트가 삭제되었습니다.", 'success')
    return redirect(url_for('my_diary'))


@app.route("/results/word_cloud/<path:post_id>", methods=['GET'])
def get_word_cloud_file(post_id):
    """ word cloud가 저장된 미디어 폴더에 접근(results폴더)
    :param post_id: 포스트 id
    :return: 지정된 directory의 파일에 접근한다.
    """
    word_cloud_file_name = path.get_user_word_cloud_file_name(post_id)
    print("[get_word_cloud_file] word_cloud_file_name: ", word_cloud_file_name)
    return send_from_directory(path.get_user_media_path(post_id), word_cloud_file_name)


@app.route("/results/series_word_cloud/<path:series_post_id>", methods=['GET'])
def get_series_word_cloud_file(series_post_id):
    """ word cloud가 저장된 미디어 폴더에 접근(results폴더)
    :param post_id: 포스트 id
    :return: 지정된 directory의 파일에 접근한다.
    """
    series_word_cloud_file_name = path.get_user_series_word_cloud_file_name(series_post_id)
    print("[get_series_word_cloud_file] series_word_cloud_file_name: ", series_word_cloud_file_name)
    return send_from_directory(path.get_user_media_path_series(series_post_id), series_word_cloud_file_name)


# 기능: analysis page에 유저의 게시글별 일기 이미지 파일 주소를 불러오기 위한 route
# 입력: post_id와 업로드한 일기 이미지 파일 이름을 input
        # input: f"{self._username}_{str(post_id)}.png"
# 출력: post_id와 일기 이미지 파일 이름을 user_media_path 경로에 추가하여 출력
        # output: send_from_directory(path.get_user_media_path(post_id), upload_img_file_name)
# 버전/일시: ver 0.x/2021.10.26 추가
# 개발자: 김수연
@app.route("/results/diary_img/<path:post_id>", methods=['GET'])
def get_upload_img(post_id):
    """ 
    일기 이미지 파일을 불러와서 analysis 웹 페이지에 업로드한 일기 이미지 전송
    """
    upload_img_file_name = path.get_user_diary_file_name(post_id)
    print("[get_upload_img] upload_img_file_name: ", upload_img_file_name)
    return send_from_directory(path.get_user_media_path(post_id), upload_img_file_name)


# 기능: my_diary(다이어리 페이지)의 게시글에 각 게시글별 stack bar chart 이미지 주소를 전송하는 route
# 입력: post_id와 stacked bar char 이미지 파일 이름을 input
    # input: f"{self._username}_{str(post_id)}_stacked_bar_chart.png"
# 출력: post_id와 stacked bar chart 이미지 파일 이름을 user_media_path 경로에 추가하여 출력
    # output: send_from_directory(path.get_user_media_path(post_id), stacked_bar_chart_img_file_name)
# 버전/일시: ver 0.x/2021.10.26 추가
# 개발자: 김수연
@app.route("/results/stacked_bar_chart/<path:post_id>", methods=['GET'])
def get_stacked_bar_chart_img(post_id):
    """ 
    stacked_bar_chart 이미지 파일 주소를 my_diary에 전송 
    """
    stacked_bar_chart_img_file_name = path.get_user_stacked_bar_chart_file_name(post_id)
    print("[stacked_bar_chart_img_file_name] stacked_bar_chart_img_file_name: ", stacked_bar_chart_img_file_name)
    return send_from_directory(path.get_user_media_path(post_id), stacked_bar_chart_img_file_name)


@app.route("/post/upload_file", methods=['GET', 'POST'])
def upload_file():
    """
    1. 요청한 파일을 업로드 하고 my_diary로 리다이렉트 한다.
    2. OCR, text mining, sentiment analysis를 수행하도록 처리한다.
    """
    if request.method == "POST":

        f = request.files['file']  # input 태그의 name 을 받음.
        print("[upload_file] f.filename", f.filename)

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
        try:
            if Apps.analyzer.is_initialized():
                t1 = Thread(target=Apps.analyzer.analysis, args=[post_id])
                t1.start()
            else:
                t2 = Thread(target=Apps.analyzer.init_and_analyze, args=[post_id])
                t2.start()
        except Exception as e:
            print('[upload_file] error: ', e)
            post = Post.query.get_or_404(post_id)
            post.error = True
            db.session.commit()

        return redirect(url_for("my_diary"))

    else:
        return '실패'


@app.route('/post/<int:post_id>/re_analyze')
@login_required
def re_analyze(post_id):
    try:
        if Apps.analyzer.is_initialized():
            t1 = Thread(target=Apps.analyzer.analysis, args=[post_id])
            t1.start()
        else:
            t2 = Thread(target=Apps.analyzer.init_and_analyze, args=[post_id])
            t2.start()
        flash("다시 분석을 요청하였습니다.", 'success')
    except Exception as e:
        print('[re_analyze] error: ', e)
        post = Post.query.get_or_404(post_id)
        post.error = True
        db.session.commit()

    return redirect(url_for("my_diary"))


@app.route("/datetime", methods=['GET', 'POST'])
@login_required
def datetime_analyze():

    return render_template("datetime.html")

@app.route('/series_analysis', methods=['GET', 'POST'])
@login_required
def series_analysis():
    if request.method == "POST":
        # 날짜 받아오기
        start_date = request.form['startdate']
        finish_date = request.form['finishdate']
        print(start_date, finish_date, type(start_date))

        # 날짜에 해당하는 모든 포스트 쿼리
        posts = Post.query.filter_by(user_id=current_user.id).filter(db.func.date(Post.pub_date).between(str(
                start_date),
                                                                                str(finish_date))).all()
        print(posts, type(posts))

        user_id = current_user.id

        # 모든 포스트의 ocr_text 뽑기 -> wordcloud 만드는 데에 사용
        text_list = []
        date_list = []
        sentiment_list = []

        neg_list = []
        pos_list = []
        neu_list = []

        for post in posts:
            # 모든 ocr_text를 문자열로 만들어서 리스트에 담는다
            text_list.append(post.ocr_text)
            date_format = post.pub_date.strftime('%Y-%m-%d')
            date_list.append(str(date_format))

            neg_list.append(post.sentiment['document']['confidence']['negative'])
            pos_list.append(post.sentiment['document']['confidence']['positive'])
            neu_list.append(post.sentiment['document']['confidence']['neutral'])

        # 리스트에 담은 문자열을 모두 하나의 문자열로 만든다
        texts = ' '.join(text_list)
        print(texts)

        # db에 위에서 조회한 일기 텍스트를 저장한다.
        series_post = SeriesPost(title="", ocr_text_bulk=texts, sentiment={}, word_cloud="", author=current_user)
        db.session.add(series_post)
        db.session.commit()

        #######
        # for문으로 post.sentiment['document']['sentiment']
        # 빈도를 세서 비율을 도출 -> series_post.sentiment에 json 형식으로 저장
        # -> 이후에 html에서 시각화에 써먹으면 된다.
        #######

        # 각 확률을 쓰지 않고 overall_sentiment만 쓸거면 아래의 함수를 쓰면 된다.
        # positive이면 1, negative이면 -1, neutral이면 0을 더한다.
        sentiment_cnt = 0
        sentiment_func = lambda x: 1 if x == 'positive' else -1 if x == 'negative' else 0
        neg_prob = 0
        pos_prob = 0
        neut_prob = 0

        for post in posts:
            overall_sentiment = post.sentiment['document']['sentiment']
            sentiment_cnt += sentiment_func(str(overall_sentiment))
            neg_prob += post.sentiment['document']['confidence']['negative']
            pos_prob += post.sentiment['document']['confidence']['positive']
            neut_prob += post.sentiment['document']['confidence']['neutral']

        print(sentiment_cnt, neg_prob, pos_prob, neut_prob)

        # DB에 합산된 sentiment 정보를 저장한다.
        sentiment_dict = {'document':
                              {'confidence':
                                   {'negative': neg_prob,
                                    'neutral': neut_prob,
                                    'positive': pos_prob}
                                }
                          }
        series_post.sentiment = sentiment_dict
        db.session.commit()

        # 저장한 SeriesPost의 id를 조회한다.
        series_post_id = series_post.id

        # 이 아이디를 사용해서 분석기(text 분석만 함)를 돌린다.
        try:
            if Apps.analyzer.is_initialized():
                Apps.analyzer.analyze_series(series_post_id)
            else:
                print("not initialized")
        except Exception as e:
            print('[datetime_analyze] error: ', e)
            series_post.error = True
            db.session.commit()
            return render_template("datetime.html")

        # 위의 과정들에서 series_post에 정보를 모두 넣은 후 다시 쿼리해서 변수에 담는다.
        series_post = SeriesPost.query.get(series_post_id)

        return render_template("analyze_series.html", series_post=series_post, posts=posts,
                               pos_list=pos_list, neg_list=neg_list, neu_list=neu_list,
                               date_list=date_list)

@app.template_filter('datetime')
def _jinja2_filter_datetime(date, fmt=None):
    if fmt:
        return date.strftime(fmt)
    else:
        return date.strftime('%Y년 %m월 %d일')  # 시, 분을 지웟지만 임시적임. 나중에 한국시간으로 바꾸는 법을 찾을 것
