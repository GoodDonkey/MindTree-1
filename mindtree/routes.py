import json
import os
from concurrent import futures
from threading import Thread
from flask import render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename

from mindtree.thread import analysis_threading
from mindtree.utils.OCR import OCR
from mindtree.utils.request_sentiment import SentimentAnalysis
from mindtree.utils.text_analysis import TextAnalysis

from mindtree import app


@app.route("/", methods=['GET'])
def home():
    """ 시작 페이지. 로그인을 할 수 있음."""
    return render_template('login.html')


@app.route("/my_diary", methods=['GET'])
def my_diary():
    """ login required,  """
    return render_template('my_diary.html')


@app.route("/upload", methods=['GET'])
def upload():
    """ login required,  """
    return render_template('upload.html')


@app.route("/analyze", methods=['GET', 'POST'])
def analyze():
    """ login required,
    - 구현 방법
    analyze.html을 렌더 -> 렌더할 때 그래프에 들어갈 json data 전달 -> js 상에서 {{ userData }}로 받아 그래프를 그림

    :var user_id: str.
    :var sentiment_path: sentiment analysis 파일 저장 경로
    :var sentiment_json: json. sentiment analysis 결과 파일

    -- analyze 1:
        감성분석 bar graph. json 파일을 전달한다.
    -- analyze 2:
        word cloud. results 폴더 아래에 이미지 경로를 전달한다.
        - word_cloud 경로: results/<user_id>/<user_id>_word_cloud.png 이다.
        - 이때 results/ 가 media_folder로 정의되어 있다.
        - 따라서 이때 이미지가 저장된 경로에 접근하려면 <user_id>/<user_id>_word_cloud.png 를 전달하면 된다. """

    # -- analyze 1: 감성분석 bar graph
    user_id = request.form.get('id')  # 추후 로그인 시스템이 구축되면 세션 id를 받을 수 있도록 수정.
    print("user_id: ", user_id)
    sentiment_path = os.path.join('mindtree/results', str(user_id), str(user_id) + "_sentiment.json")
    with open(sentiment_path, "r",
              encoding="utf-8") as local_json:
        sentiment_json = json.load(local_json)

    # -- analyze 2: word cloud
    image_path = os.path.join(str(user_id), str(user_id) + "_word_cloud.png")

    return render_template('analyze.html', user_data=sentiment_json, image_path=image_path)


@app.route("/results/<path:filename>", methods=['GET'])
def get_file(filename):
    """ word cloud가 저장된 미디어 폴더에 접근한다. (results폴더)

    :param filename: results 폴더 아래부터의 이미지 경로
    :return: 지정된 directory의 파일에 접근한다.
    """
    media_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
    print("media_folder", media_folder)
    return send_from_directory(media_folder, filename)


@app.route("/login", methods=['GET'])
def login():
    """ login 로직을 수행함. 지금은 임시로 바로 my_diary로 보냄."""
    return redirect(url_for("my_diary"))


@app.route("/upload_file", methods=['GET', 'POST'])
def upload_file():
    """
    1. 요청한 파일을 업로드 하고 my_diary로 리다이렉트 한다.
    2. OCR, text mining, sentiment analysis를 수행하도록 처리한다.
    """

    if request.method == "POST":
        # 요청한 파일을 업로드 한다.
        f = request.files['file']  # input 태그의 name 을 받음.

        # id 는 추후 로그인 시스템이 구현되면 세션에서 받아올 예정.
        user_id = request.form.get('id')
        print("user_id: ", user_id)

        # 경로 변수 정의
        filename = str(user_id) + '_' + str(secure_filename(f.filename))
        file_dir = os.path.join("mindtree/results", str(user_id))
        file_path = os.path.join(file_dir, filename)

        # 디렉토리 만들기
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir, exist_ok=True)

        # 이미지 저장
        f.save(file_path)
        flash("업로드에 성공하였습니다", "success")

        ### 업로드한 파일을 미리 분석해서 저장해둔다.  ###
        t1 = Thread(target=analysis_threading, args=[user_id])
        t1.start()

        return redirect(url_for("my_diary"))

    else:
        return '실패'
