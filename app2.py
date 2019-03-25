from flask import Flask, render_template, request, session, redirect, url_for, make_response,jsonify
#DB
import pymongo
#ディレクトリ操作など
import os , re, shutil
from pathlib import Path
#タイムスタンプ取得
from datetime import datetime
#画像処理
from PIL import Image
#拡張子
from werkzeug import secure_filename
#画像　日本語をローマ字に変換
from pykakasi import kakasi

from flask_bootstrap import Bootstrap

from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, PasswordField, TextField,\
StringField, SubmitField, SelectField
from wtforms.validators import Required, Length, Regexp
from flask_wtf.file import FileField, FileRequired, FileAllowed

class LoginForm(FlaskForm):
    userID = TextField(u'userID',render_kw={'autofocus': True}, validators=[
            Required(message=u'userIDを入力してください'),
            Length(min=4, max=12, message=u'userIDは4文字以上12文字以下です。'),
            Regexp(regex='[a-z0-9]', message=u'userIDは半角小文字英数字で入力してください。')
        ])
    
    password = PasswordField(u'password', validators=[
            Required(u'パスワードが入力されていません。'),
            Length(min=4, max=12, message=u'passwordは4文字以上12文字以下です。')
        ])

    submit = SubmitField(u'Login',render_kw={"class": "btn btn-primary"}        
    )

class SignUpForm(FlaskForm):
    userID = TextField(u'userID',render_kw={'autofocus': True,"autocomplete":'off'}, validators=[
            Required(message=u'userIDを入力してください'),
            Length(min=4, max=12, message=u'userIDは4文字以上12文字以下です。'),
            Regexp(regex='[a-z0-9]', message=u'userIDは半角小文字英数字で入力してください。')
        ])
    
    username = TextField(u'username',render_kw={"autocomplete":'off'}, validators=[Required(),
                Length(min=1,max=12, message=u'usernameは1文字以上12文字以下です。')
        ])

    password = PasswordField(u'password', validators=[
            Required(u'パスワードが入力されていません。'),
            Length(min=4, max=12, message=u'passwordは4文字以上12文字以下です。')
        ])
    
    submit = SubmitField(u'登録')

app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = "The secret witch ciphers the cookie"
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

client = pymongo.MongoClient('localhost', 27017)
db = client.tter
tweets_db = db.tweets
users_db = db.users

#画像の名前が適切なものか判断するための情報
kakasi = kakasi()
kakasi.setMode('H', 'a')
kakasi.setMode('K', 'a')
kakasi.setMode('J', 'a')
conv = kakasi.getConverter()

@app.before_request
def before_request():
    if session.get('username') is None:
        if request.path == '/signUp':
            return
        elif request.path == '/login':
            return
        else:    
            return redirect('/login')


@app.route('/', methods =["GET" , "POST"])
def index():
    if request.method == 'POST':
        data = request.form['tweet']
        add_tweet(data, session['userID'], session['username'])
        return redirect(url_for('index'))
    else:   #GETリクエストがあるとページを表示する
        tweets = list(tweets_db.find({},{"_id":0}).sort('timestamp',-1))
        user = users_db.find_one( {"userID":session['userID']},{'_id':0 ,'password':0,'userID':0} )
        count = {}
        count['users'] = users_db.count()
        count['tweets'] = tweets_db.count()
        #ユーザーが削除されていなければ
        if search_user(session['userID']):
            session['img_url'] = user['img_url']
            return render_template('index.html',tweets=tweets,count=count)
        #別ウィンドウでユーザーが削除されていればセションを破棄する
        else:
            sessionPop()
            return redirect('/login')

#ツイートの追加
def add_tweet(tweet,userID,username):
    tweet = tweet.replace('\r\n', '</br>')
    #フォルダ内のファイルを検索
    p = Path(f'./static/users/{userID}')
    for path in list(p.glob('*')):
        tweets_db.insert_one({"tweet" : tweet, "userID": userID ,'username':username ,"timestamp" : str(datetime.today()),"img_url": str(path) })

#ユーザの追加
def add_user(userID, username, password):
    #ファイルのコピー
    shutil.copyfile("./static/users/default.jpg",f"./static/users/{userID}/default.jpg")
    users_db.insert_one({'userID':userID,'username':username,'password':password,'img_url':f'../static/users/{userID}/default.jpg'})
        
#userIDが登録済みか確認
def search_user(userID):
    data = users_db.find_one( {"userID":userID} )
    print(data)
    if data is not None: #登録されていれば
        return True
    return False

#パスワードを確認する
def check_pass(userID, password):
    data = users_db.find_one( {"userID":userID} )
    if data['password'] == password:    #パスワードが正しければ
        return True
    return False

#ユーザーDBとtweetDBの値を更新する
def update_db(key,value):
    users_db.update_one({'userID':session['userID']},{'$set': {key:value}})
    tweets_db.update_many({'userID':session['userID']},{'$set': {key:value}})

#セションを破棄する
def sessionPop():
    session.pop('userID', None)
    session.pop('username', None)
    session.pop('img_url', None)

#キャッシュを使わないように後ろに時間を追加
def chacheAvoidance(data):
    today = str(datetime.now()).split()[1]
    #キャッシュを使わないように後ろに時間を追加
    return data + '?'  + today
    

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            ID = form.userID.data
            passwd = form.password.data
        # ID = request.form['userID']
        # passwd = request.form['password']
            if search_user(ID) and check_pass(ID,passwd):   #ユーザIDとパスワードが正しければ
                user = users_db.find_one( {"userID":ID},{'_id':0 ,'password':0,'userID':0} )
                session['username'] = user['username']
                session['userID'] = ID
                session['img_url'] = user['img_url']
                print(session['img_url'])
                return redirect(url_for('index'))
            else:
                return render_template('login.html',form=form, error='IDまたはパスワードが違います')
        else:
            return render_template('login.html',form=form)
    else:
        return render_template('login.html',form=form)
        # return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    sessionPop()
    return redirect(url_for('login'))

@app.route('/signUp', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            userID = form.userID.data
            username = form.username.data
            passwd = form.password.data
            #exist_okは最後消す
            os.makedirs(f'./static/users/{userID}', exist_ok=True)
            if not search_user(userID):
                add_user(userID,username,passwd)
                return render_template('success.html',message='ユーザー作成に成功しました。')
            else:
                return render_template('signUp.html',form=form,error='このユーザーIDはすでに使用されています。')
        else:
            return render_template('signUp.html',form=form)
    else:
        return render_template('signUp.html', form=form)

def directory_contents_delete(path):
    #フォルダ内のファイルを検索
    p = Path(path)
    #ファイルが有れば削除
    for data in list(p.glob('*')): 
        os.remove(data)

#画像をアップロード
def upload_file(img_file):
    tmp = img_file.filename.split('.')
    extension = '.' + tmp[-1]
    filename = secure_filename(conv.do(session['userID'] + '_profile_image'))
    filepath = './static/users/%s' % session['userID']
    directory_contents_delete(filepath)
    
    endfilename = filename + extension
    img_url = os.path.join(filepath, endfilename)
    img_file.save(img_url)

    #リサイズ
    resize_image(img_url, extension)
    #HTMLからの参照用にパスを変更
    img_url = '.' + img_url
    #データベースの画像パスを変更
    update_db('img_url',img_url)
    
    session['img_url'] = chacheAvoidance(img_url)

    return 

#画像を400×400にリサイズする
def resize_image(img_url, extention):
    img = Image.open(img_url)
    img_resize = img.resize((400, 400))
    img_resize.save(img_url)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        message={'success':[],'error':[]}
        #画像が選択されているか判定（エラーハンドリング)
        try:
            if request.files['img_file']:   #画像が選択されていれば
                img_file = request.files['img_file']
                if allowed_file(img_file.filename):
                    upload_file(img_file)
                    message['success'].append('画像の変更：画像の変更に成功しました。')
                else:   
                    message['error'].append('画像の変更：サポートされていない拡張子です。')

        except: #画像が選択されてなければ何もしない
            pass

        if request.form.getlist('delete_img'):  #ユーザー画像を初期化する処理
            directory_contents_delete('./static/users/'+session['userID'])
            default_url='../static/users/default.jpg'
            update_db('img_url',default_url)
            session['img_url'] = default_url
            message['success'].append('画像の削除：画像を削除しました')

        if request.form['newname']: #ユーザー名を変更する処理
            if len(request.form['newname']) > 12:   #12文字以上ならエラーを吐く
                message['error'].append('ユーザーネームの変更：ユーザーネームに使用できるの文字列は１２文字以内です。')
            else:
                update_db('username',request.form['newname'])
                session['username'] = request.form['newname']
                message['success'].append('ユーザーネームの変更：ユーザーネームの変更に成功しました。')
        
        return render_template('profile.html',message=message)
        
    else:
        return render_template('profile.html')

@app.route('/home', methods =["GET" , "POST"])
def home():
    name = request.args.get('name')
    tweets = list(tweets_db.find({'userID':name},{"_id":0,}).sort('timestamp',-1))
    count = len(tweets)
    print(count)
    return render_template('home.html',tweets=tweets,username=name,count=count)

@app.route('/setting', methods =['GET',"POST"])
def setting():
    if request.method == 'POST':
        if request.form['submit'] == 'delete_account':
            if check_pass(session['userID'],request.form['password']):
                users_db.delete_one({'userID':session['userID']})
                tweets_db.delete_many({'userID':session['userID']})
                shutil.rmtree('./static/users/'+session['userID'])
                sessionPop()
                return render_template('success.html', message='ユーザーアカウントの削除に成功しました。\n またのご利用をお待ちしております。')
            else:
                return render_template('setting.html', error='パスワードが間違っています。')
    return render_template('setting.html')

@app.route('/getTweet', methods=['POST'])
def getTweet():
    tweets = list(tweets_db.find({},{"_id":0}).sort('timestamp',-1))
    count = {}
    count['users'] = users_db.count()
    count['tweets'] = tweets_db.count()
    return jsonify({'tweet':tweets,'count':count})


@app.route('/test', methods = ["GET","POST"])
def test():
    # form = []
    # # form = profileForm_changeImage()
    # form.append(ProfileForm.ChangeImage())
    # form.append(ProfileForm.DeleteImage())
    # form.append(ProfileForm.ChangeUsername())
    # # form.append(profileForm.)
    
    # if form[0].validate_on_submit():    #画像が送信されたら
    #     img_file = form[0].change_image.data
    #     print(form[0].submit.data)
    #     # return render_template('test.html', error=['success'],form=form,form2=form2)
    # elif form[1].validate_on_submit():  #[画像を削除]ボタンが押されたら
    #     print(form[1].submit.label.text)
    #     # for x in dir(form2.submit.label.text):
    #     #     print (x)
    #     # return render_template('test.html',form=form)
    #     # return render_template('test.html',form=form,form2=form2)
    # elif form[2].validate_on_submit():
    #     pass
    #     # return render_template('test.html',form=form)
    return render_template('test.html')
    # return render_template('test.html',form=form,form2=form2)

@app.route('/test2', methods = ["GET","POST"])
def test2():
    if request.method == 'POST':
        #画像をデフォルトに戻す
        if request.form['submit'] == 'delete_img':
            directory_contents_delete('./static/users/'+session['userID'])
            default_url='../static/users/default.jpg'
            update_db('img_url',default_url)
            session['img_url'] = default_url
            return render_template('profile.html' ,success=['画像を削除しました'] )
        #名前の変更
        elif request.form['submit'] == 'send_name':
            update_db('username',request.form['newname'])
            session['username'] = request.form['newname']
            return render_template('profile.html')
        #ユーザーの削除
        elif request.form['submit'] == 'delete_account':
            if check_pass(session['userID'],request.form['password']):
                users_db.delete_one({'userID':session['userID']})
                tweets_db.delete_many({'userID':session['userID']})
                shutil.rmtree('./static/users/'+session['userID'])
                sessionPop()
                return render_template('success.html', message='ユーザーアカウントの削除に成功しました。\n またのご利用をお待ちしております。')
            else:
                return render_template('profile.html', error=['パスワードが間違っています。'])
        #画像の変更
        elif request.files.get('img_file') is not None:
            img_file = request.files['img_file']
            if img_file and allowed_file(img_file.filename):
                return upload_file(img_file)
            else:
                return render_template('profile.html', error=['サポートされていない拡張子です。'])
        else:
            return render_template('profile.html', error=['画像が選択されていません。'])

    else:
        return render_template('test2.html')


app.run(host='0.0.0.0', debug=True)
