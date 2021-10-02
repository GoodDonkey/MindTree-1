import io
import os
from datetime import datetime

from hanspell import spell_checker

# Imports the Google Cloud client library
from google.cloud import vision


def get_time_str():
    return "[" + str(datetime.now()) + "]"


def spell_check(input_text):
    """ 맞춤법을 체크한다.
    - spell_checker 처리 결과는
    original, checked, words 등을 출력할 수 있다.

    :return : 맞춤법 체크한 단어 str """

    result = spell_checker.check(input_text)

    print(get_time_str(), "checked\n")
    print(result.checked)

    return result.checked


def request_ocr(content):
    """ 이미지를 받아서 Google OCR 요청을 보내고 결과를 받는다.
    :param content: 이미지
    :return OCR 결과 텍스트 """

    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    image = vision.Image(content=content)

    # 이미지에서 text를 추출한다.
    response_text = client.text_detection(image=image)
    words = response_text.text_annotations

    # words[0]는 추출된 모든 텍스트.
    # 그 중 description 이라는 key 에 저장된 값이 인식된 텍스트의 문자열이다.
    print("------------아래는 뽑은 텍스트 입니다---------------")
    words_cat = words[0].description

    print(f'뽑힌 텍스트 확인'
          f' \n{words[0].description}')

    return words_cat


def ocr(file_path, file_dir, user_id):
    """ OCR main function
    1. 이미지 파일 OCR 처리 + 맞춤법 체크
    2. 결과 저장
    :return OCR 결과 텍스트 """

    # 이미지 파일 ocr 하기
    with io.open(file_path, 'rb') as image_file:
        content = image_file.read()
    text = request_ocr(content)
    text_checked = spell_check(text)

    # 결과 저장하기
    user_ocr_path = os.path.join(file_dir, f"{str(user_id)}_ocr.txt")
    with open(user_ocr_path, "w") as ocr_result:
        ocr_result.write(text_checked)

    return user_ocr_path
