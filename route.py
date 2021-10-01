from flask import Flask, render_template, request, redirect, url_for, flash
from flask_cors import CORS
from werkzeug.utils import secure_filename
from utils.OCR import ocr
from utils.text_analysis import text_mining
import os
import json

app = Flask(__name__)
"""로컬 환경에서 자바스크립트로 flask 도메인에 요청하는 경우, CORS 에러 발생.
    즉, 동일 출처가 아닐 때 에러가 발생하는데, 이를 해결해주는 flask_cors 를 사용한다.
    https://webisfree.com/2020-01-01/python-flask%EC%97%90%EC%84%9C-cors-cross-origin-%EC%82%AC%EC%9A%A9%ED%95%98%EA%B8%B0 """
CORS(app)
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


@app.route("/analyze", methods=['GET'])
def analyze():
    """ login required, 분석된 데이터로 그래프를 만들도록 구현.
    analyze.html을 렌더 -> html 통해서 javascript 작동 -> /json_data로 데이터 요청 -> 그래프 그림

    => 이 route 에서 '누구' 의 '어느' 일기 데이터에 접근할 것인지 미리 지정해 전달해야 한다."""
    return render_template('analyze.html')


@app.route("/login", methods=['GET'])
def login():
    """ login 로직을 수행함. 지금은 임시로 바로 my_diary로 보냄."""
    return redirect(url_for("my_diary"))


@app.route("/upload_file", methods=['GET', 'POST'])
def upload_file():
    if request.method == "POST":
        # 요청한 파일을 업로드 한다.
        f = request.files['file']  # input 태그의 name 을 받음.
        user_id = request.form.get('id')

        filename = str(user_id) + '_' + str(secure_filename(f.filename))
        file_dir = os.path.join("results", str(user_id))
        file_path = os.path.join(file_dir, filename)

        # 디렉토리 만들기
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir, exist_ok=True)

        # 이미지 저장
        f.save(file_path)
        flash("업로드에 성공하였습니다", "success")

        # # 페이지 넘기기
        # redirect(url_for("my_diary"))

        ### 업로드한 파일을 미리 분석해서 저장해둔다.  ###
        # request OCR
        user_ocr_result = ocr(file_path, file_dir, user_id)
        print(user_ocr_result)

        # text mining
        text_mining(user_id, user_ocr_result)

        # sentiment analysis

        return redirect(url_for("my_diary"))

    else:
        return '실패'


@app.route("/json_data", methods=['GET', 'POST'])
def json_data():
    """ returns sample json data for bar graph """
    with open("/Users/motive/Data_Study/Projects/MindTree/results/response02.json", "r",
              encoding="utf-8") as local_json:
        data = json.load(local_json)
    print(data)
    return data


if __name__ == "__main__":
    app.run(debug=True)
