#FROM continuumio/miniconda3:4.5.11
#
#RUN apt-get update -y; apt-get upgrade -y
#
## You don't technically need these, but I get kind of twitchy if I don't have vim installed
#RUN apt-get install -y vim-tiny vim-athena ssh
#RUN apt-get install git -y
## Add a user and switch, using the default root user is BAD
#RUN adduser --home /home/flask flask
#
#USER mindtree-user
#WORKDIR /home/Mindtree-user
#
## app working directory
#RUN mkdir -p MindTree
#WORKDIR /home/Mindtree-user/MindTree
#
## Always save your environments in a conda env file.
## This makes it so much easier to fix your environment when you inadvertantly clobber it
## conda 환경 파일을 복사한다.
#COPY mindtree-env.yml environment.yml
#RUN conda env create -f environment.yml
#RUN echo "alias l='ls -lah'" >> ~/.bashrc
#
## This is the conda magic. If you are running through a shell just activating the environment in your profile is peachy
#RUN echo "source activate flask-app" >> ~/.bashrc
#
## py-hanspell이 conda나 pip로 안받아짐. 그래서 깃에서 직접 다운로드 후 설치한다.
## run git clone to get py-hanspell
#RUN git clone https://github.com/ssut/py-hanspell.git
#
## run setup.py to install py-hanspell
#RUN python py-hanspell/setup.py install
#
## This is the equivalent of running `source activate`
## Its handy to have in case you want to run additional commands in the Dockerfile
#ENV CONDA_EXE /opt/conda/bin/conda
#ENV CONDA_PREFIX /home/flask/.conda/envs/flask-app
#ENV CONDA_PYTHON_EXE /opt/conda/bin/python
#ENV CONDA_PROMPT_MODIFIER (flask-app)
#ENV CONDA_DEFAULT_ENV flask-app
#ENV PATH /home/flask/.conda/envs/flask-app/bin:/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
#
## 실행한다.
#CMD ["python","app.py"]


# init a base image (Alpine is small Linux distro)
FROM python:3.8.12

# define the present working directory
WORKDIR /MindTree
# copy the contents into the working dir
ADD . /MindTree

# dlib 설치시 이슈가 있어 미리 cmake를 설치해둔다.
RUN pip3 install cmake
# run pip to install the dependencies of the flask app
RUN pip3 install -r requirements.txt

# run git clone to get py-hanspell
RUN git clone https://github.com/ssut/py-hanspell.git ./

# run setup.py to install py-hanspell
RUN python ./py-hanspell/setup.py install
