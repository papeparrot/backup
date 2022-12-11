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

    tot_count = db.project00.find({}).collection.estimated_document_count()
    
    last_page_num = math.ceil(tot_count / limit)  # 반드시 올림을 해줘야함

    
    block_size = 5
    
    block_num = int((page - 1) / block_size)
    block_start = (block_size * block_num) + 1
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