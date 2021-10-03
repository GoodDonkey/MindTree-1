from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from utils.OCR import ocr
from utils.text_analysis import text_mining
from utils.request_sentiment import sentiment_analysis
import os
import json

app = Flask(__name__)
app.secret_key = "donkey_secret"  # flash 쓰려면 설정해야함.


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
    """ login required, 분석된 데이터로 그래프를 만들도록 구현.
    => 이 route 에서 '누구' 의 '어느' 일기 데이터에 접근할 것인지 미리 지정해 전달해야 한다.
    - 방법
    analyze.html을 렌더 -> 렌더할 때 그래프에 들어갈 json data 전달 -> js 상에서 {{ userData }}로 받아 그래프를 그림
    """

    # 추후 로그인 시스템이 구축되면 세션 id를 받을 수 있도록 수정.
    user_id = request.form.get('id')
    sentiment_path = os.path.join('results', str(user_id), str(user_id) + "_sentiment.json")
    with open(sentiment_path, "r",
              encoding="utf-8") as local_json:
        data = json.load(local_json)

    return render_template('analyze.html', user_data=data)


@app.route("/login", methods=['GET'])
def login():
    """ login 로직을 수행함. 지금은 임시로 바로 my_diary로 보냄."""
    return redirect(url_for("my_diary"))


@app.route("/upload_file", methods=['GET', 'POST'])
def upload_file():
    """
    1. 요청한 파일을 업로드 하고 my_diary로 리다이렉트 한다.
    2. OCR, text mining, sentiment analysis를 수행하도록 처리한다.
        위 처리는 백엔드에서 따로 이루어질 수 있도록 구현한다.
        (현재는 순차적으로 모두 분석이 이루어지고 난 후에 다음 페이지로 넘어감. 수정대상.)

    :return my_diary 페이지로 리다이렉트 """
    if request.method == "POST":
        # 요청한 파일을 업로드 한다.
        f = request.files['file']  # input 태그의 name 을 받음.

        # id 는 추후 로그인 시스템이 구현되면 세션에서 받아올 예정.
        user_id = request.form.get('id')

        # 경로 변수 정의
        filename = str(user_id) + '_' + str(secure_filename(f.filename))
        file_dir = os.path.join("results", str(user_id))
        file_path = os.path.join(file_dir, filename)

        # 디렉토리 만들기
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir, exist_ok=True)

        # 이미지 저장
        f.save(file_path)
        flash("업로드에 성공하였습니다", "success")

        ### 업로드한 파일을 미리 분석해서 저장해둔다.  ###
        # request OCR
        user_ocr_result = ocr(file_path, file_dir, user_id)
        print(user_ocr_result)

        # text mining
        text_mining(user_id, user_ocr_result)

        # sentiment analysis
        sentiment_analysis(user_id)

        return redirect(url_for("my_diary"))

    else:
        return '실패'


# @app.route("/json_data", methods=['GET', 'POST'])
# def json_data():
#     """ (삭제예정) returns sample json data for bar graph """
#     with open("/Users/motive/Data_Study/Projects/MindTree/results/response02.json", "r",
#               encoding="utf-8") as local_json:
#         data = json.load(local_json)
#     return data


if __name__ == "__main__":
    app.run(debug=True)
