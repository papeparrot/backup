import time
from flask import Flask, render_template, jsonify, request, redirect, url_for
import jwt
import datetime
import hashlib
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from pymongo import MongoClient
import math

client = MongoClient('localhost', 27017)
db = client.WEEK00

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'JUNGLE'

side_tag = "전체"
word_all = "None"

@app.route("/")
def home():
   results = db.project00.find()
   side_tag = "전체"

   # 페이지 값 (디폴트값 = 1)
   page = request.args.get("page", 1, type=int)
   # 한 페이지 당 몇 개의 게시물을 출력할 것인가
   limit = 29

   # board컬럭션에 있는 모든 데이터를 가져옴
   datas = db.project00.find({}).skip((page - 1) * limit).limit(limit)

   # 게시물의 총 개수 세기
   tot_count = db.project00.find({}).collection.estimated_document_count()
   # 마지막 페이지의 수 구하기
   last_page_num = math.ceil(tot_count / limit)  # 반드시 올림을 해줘야함

   # 페이지 블럭을 5개씩 표기
   block_size = 5
   # 현재 블럭의 위치 (첫 번째 블럭이라면, block_num = 0)
   block_num = int((page - 1) / block_size)
   # 현재 블럭의 맨 처음 페이지 넘버 (첫 번째 블럭이라면, block_start = 1, 두 번째 블럭이라면, block_start = 6)
   block_start = (block_size * block_num) + 1
   # 현재 블럭의 맨 끝 페이지 넘버 (첫 번째 블럭이라면, block_end = 5)
   block_end = block_start + (block_size - 1)

   token_receive = request.cookies.get('mytoken')
   try:
      payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
      user_info = db.user.find_one({"username": payload["id"]})
      return render_template('index.html', user_info=user_info, table_data=results, check_tag=side_tag, word_all=word_all,
                             datas=datas, limit=limit, page=page, block_start=block_start, block_end=block_end, last_page_num=last_page_num)

   except jwt.ExpiredSignatureError:
      return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
   except jwt.exceptions.DecodeError:
      return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route("/list")
def board_list():
    results = db.project00.find()
    side_tag = request.args.get("check_tag", "전체")

    token_receive = request.cookies.get('mytoken')

    check_results = db.project00.find({"tag": side_tag})
    if (len(list(check_results)) > 29):
        # 페이지 값 (디폴트값 = 1)
        page = request.args.get("page", 1, type=int)
        # 한 페이지 당 몇 개의 게시물을 출력할 것인가
        limit = 29

        # board컬럭션에 있는 모든 데이터를 가져옴
        datas = db.project00.find({}).skip((page - 1) * limit).limit(limit)
        # 게시물의 총 개수 세기
        tot_count = db.project00.find({}).collection.estimated_document_count()
        # 마지막 페이지의 수 구하기
        last_page_num = math.ceil(tot_count / limit)  # 반드시 올림을 해줘야함

        # 페이지 블럭을 5개씩 표기
        block_size = 5
        # 현재 블럭의 위치 (첫 번째 블럭이라면, block_num = 0)
        block_num = int((page - 1) / block_size)
        # 현재 블럭의 맨 처음 페이지 넘버 (첫 번째 블럭이라면, block_start = 1, 두 번째 블럭이라면, block_start = 6)
        block_start = (block_size * block_num) + 1
        # 현재 블럭의 맨 끝 페이지 넘버 (첫 번째 블럭이라면, block_end = 5)
        block_end = block_start + (block_size - 1)
    else:
        datas = db.project00.find()
        page = 1
        limit = 29
        block_start = 1
        block_end = 1
        last_page_num = 1

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"username": payload["id"]})
        return render_template('index.html', user_info=user_info, table_data=results, check_tag=side_tag, word_all=word_all,
                                datas=datas, limit=limit, page=page, block_start=block_start, block_end=block_end, last_page_num=last_page_num)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login_register.html', msg=msg)


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.user.find_one(
        {'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    nickname_receive = request.form['nickname_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(
        password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,
        "nickname": nickname_receive,                                  # 비밀번호
        "profile_name": username_receive,                           # 프로필 이름 기본값은 아이디
        "profile_pic": "",                                          # 프로필 사진 파일 이름
        "profile_pic_real": "images/profile.jpg",             # 프로필 사진 기본 이미지
    }
    db.user.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.user.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/board_add')
def add():
   return render_template('board_add.html')


@app.route('/', methods=['POST'])
def board_add():
    title = request.form.get('title_post')
    tag = request.form.get('main_tag')
    side_tag = request.args.get("check_tag", "전체")

    results = db.project00.find()

    # 페이지 값 (디폴트값 = 1)
    page = request.args.get("page", 1, type=int)
    # 한 페이지 당 몇 개의 게시물을 출력할 것인가
    limit = 29

    # board컬럭션에 있는 모든 데이터를 가져옴
    datas = db.project00.find({}).skip((page - 1) * limit).limit(limit)

    # 게시물의 총 개수 세기
    # tot_count = db.project00.find({}).count()
    # tot_count = db.project00.count_documents({})
    tot_count = db.project00.find({}).collection.estimated_document_count()
    # 마지막 페이지의 수 구하기
    last_page_num = math.ceil(tot_count / limit)  # 반드시 올림을 해줘야함

    # 페이지 블럭을 5개씩 표기
    block_size = 5
    # 현재 블럭의 위치 (첫 번째 블럭이라면, block_num = 0)
    block_num = int((page - 1) / block_size)
    # 현재 블럭의 맨 처음 페이지 넘버 (첫 번째 블럭이라면, block_start = 1, 두 번째 블럭이라면, block_start = 6)
    block_start = (block_size * block_num) + 1
    # 현재 블럭의 맨 끝 페이지 넘버 (첫 번째 블럭이라면, block_end = 5)
    block_end = block_start + (block_size - 1)

    token_receive = request.cookies.get('mytoken')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"username": payload['id']})
        doc = {
            "tag": tag,
            "title": title,
            "name": user_info['nickname'],
            "date": time.strftime('%y-%m-%d %H:%M:%S')
        }

        db.project00.insert_one(doc)

        return render_template('index.html', table_data=results, check_tag=side_tag, word_all=word_all,
                                datas=datas, limit=limit, page=page, block_start=block_start, block_end=block_end, last_page_num=last_page_num,
                                user_info=user_info,)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

@app.route('/side_tag', methods=['POST'])
def side_tag():
    results = db.project00.find()

    side_tag = request.form.get('board_side_tag')

    check_results = db.project00.find({"tag": side_tag})
    if (len(list(check_results)) > 29):
        # 페이지 값 (디폴트값 = 1)
        page = request.args.get("page", 1, type=int)
        # 한 페이지 당 몇 개의 게시물을 출력할 것인가
        limit = 29

        # board컬럭션에 있는 모든 데이터를 가져옴
        datas = db.project00.find({}).skip((page - 1) * limit).limit(limit)
        # 게시물의 총 개수 세기
        tot_count = db.project00.find({}).collection.estimated_document_count()
        # 마지막 페이지의 수 구하기
        last_page_num = math.ceil(tot_count / limit)  # 반드시 올림을 해줘야함

        # 페이지 블럭을 5개씩 표기
        block_size = 5
        # 현재 블럭의 위치 (첫 번째 블럭이라면, block_num = 0)
        block_num = int((page - 1) / block_size)
        # 현재 블럭의 맨 처음 페이지 넘버 (첫 번째 블럭이라면, block_start = 1, 두 번째 블럭이라면, block_start = 6)
        block_start = (block_size * block_num) + 1
        # 현재 블럭의 맨 끝 페이지 넘버 (첫 번째 블럭이라면, block_end = 5)
        block_end = block_start + (block_size - 1)
    else:
        datas = db.project00.find()
        page = 1
        limit = 29
        block_start = 1
        block_end = 1
        last_page_num = 1
        
    return render_template('index.html', table_data=results, check_tag=side_tag, word_all=word_all,
                        datas=datas, limit=limit, page=page, block_start=block_start, block_end=block_end, last_page_num=last_page_num)


@app.route('/search', methods=['POST'])
def search():
   results = db.project00.find()
   side_tag = "전체"

   word = request.form.get('search_word')

   # 페이지 값 (디폴트값 = 1)
   page = request.args.get("page", 1, type=int)
   # 한 페이지 당 몇 개의 게시물을 출력할 것인가
   limit = 29

   # board컬럭션에 있는 모든 데이터를 가져옴
   datas = db.project00.find({}).skip((page - 1) * limit).limit(limit)

   # 게시물의 총 개수 세기
   # tot_count = db.project00.find({}).count()
   # tot_count = db.project00.count_documents({})
   tot_count = db.project00.find({}).collection.estimated_document_count()
   # 마지막 페이지의 수 구하기
   last_page_num = math.ceil(tot_count / limit)  # 반드시 올림을 해줘야함

   # 페이지 블럭을 5개씩 표기
   block_size = 5
   # 현재 블럭의 위치 (첫 번째 블럭이라면, block_num = 0)
   block_num = int((page - 1) / block_size)
   # 현재 블럭의 맨 처음 페이지 넘버 (첫 번째 블럭이라면, block_start = 1, 두 번째 블럭이라면, block_start = 6)
   block_start = (block_size * block_num) + 1
   # 현재 블럭의 맨 끝 페이지 넘버 (첫 번째 블럭이라면, block_end = 5)
   block_end = block_start + (block_size - 1)

   if word:
      word_all = list(db.project00.find({'title': {'$regex': word}}))
      print(word_all)
      return render_template('index.html', table_data=results, check_tag=side_tag, search_all=word_all,
                             datas=datas, limit=limit, page=page, block_start=block_start, block_end=block_end, last_page_num=last_page_num)
   else:
      word = "None"
      return render_template('index.html', table_data=results, check_tag=side_tag, word_all=word,
                             datas=datas, limit=limit, page=page, block_start=block_start, block_end=block_end, last_page_num=last_page_num)

@app.route('/reserve')
def reserve_home():
    token_receive = request.cookies.get('mytoken')

    try:
      payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
      user_info = db.user.find_one({"username": payload["id"]})
      

      return render_template("calender.html", user_info=user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return  redirect(url_for("home"))
    

@app.route('/reserve', methods=['POST'])
def date():
    date_receive = request.form['date'] 
    time_receive = request.form['time']
    id_receive = request.form['id']
    date = {'date': date_receive, 'time': time_receive, 'id': id_receive}

    
    if time_receive == "**:**시 ~ **:**시":
        return jsonify({'result': 'fail'})

    elif date_receive == "****년**월**일":
        return jsonify({'result': 'fail2'})

    elif db.reserve.find_one({'time' : time_receive}) and db.reserve.find_one({'date' : date_receive}):
        return jsonify({'result': 'fail3'})

    elif db.reserve.find_one({'id' : time_receive}):
        return jsonify({'result': 'fail3'})

    elif db.reserve.find_one({'id' : id_receive}, {'_id': 0}):
        return jsonify({'result': 'fail4'})

    else :
        db.reserve.insert_one(date)
        return jsonify({'result': 'success'})

@app.route('/date', methods=['POST'])
def read_times():
    ymd_receive = request.form['ymd']
    result = list(db.reserve.find({'date': ymd_receive}, {'_id': 0}))
    return jsonify({'articles': result})

@app.route('/cancle', methods=['POST'])
def reserver_cancle():
    print(db.reserve.find({}).collection.estimated_document_count())
    id_receive = request.form['id']
    
    if db.reserve.find_one({'id' : id_receive},{'_id': 0}):
        db.reserve.delete_one({'id': id_receive})
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'fail'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
