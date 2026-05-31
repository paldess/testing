import hashlib
import random
from flask import Flask, render_template, request, make_response, abort, jsonify
from connects import connect_read, connect_write
from api_methods import api_user

app = Flask(__name__)
app_secret_key = 'secret key'
app_session_key = ''
max_age_token = 60

# Добавление куки к страницам
def cookies(page, email=None, group=None):
    global app_session_key
    global  max_age_token
    # Обновление токена куки
    if request.cookies.get('token') == app_session_key:
        resp = make_response(page)
        for i in request.cookies:
            resp.set_cookie(i, request.cookies.get(i), max_age=max_age_token, httponly=True)
        return resp
    # Создание куки
    else:
        resp = make_response(page)
        app_session_key = app_secret_key + str(random.randint(10 ** 10, 10 ** 11))
        resp.set_cookie('token', app_session_key, max_age=max_age_token, httponly=True)
        resp.set_cookie('email', email, max_age=max_age_token, httponly=True)
        resp.set_cookie('group', str(group), max_age=max_age_token, httponly=True)
        return resp

# Главна страница
@app.route('/', methods=['GET', 'POST'])
def home():
    global app_session_key
    if request.cookies.get('token') == app_session_key:
        return cookies(render_template('authorized.html', email=request.cookies.get('email')))
    else:
        return render_template('index.html')

# На страницу регистрации
@app.route('/go_run_registr/', methods=['GET', 'POST'])
def go_run_registr():
    return render_template('registration.html')

# На страницу входа
@app.route('/go_run_input', methods=['GET', 'POST'])
def go_run_input():
    return render_template('index.html')

# Регистрация пользователя
@app.route('/run_registr', methods=['GET', 'POST'])
def run_registr():
    email = request.form.get('email')
    password, password_2 = request.form.get('password'), request.form.get('password_2')
    if password == password_2:
        # Проверка существования пользователя
        sql_exist_user = f'select email from users where email = "{email}";'
        if len(connect_read(sql_exist_user)) > 0:
            return render_template('registration.html', result='Такой пользователь уже зарегестрирован')
        sql = f'insert into users(email, password) values("{email}", "{hashlib.sha256(password.encode()).hexdigest()}");'
        connect_write(sql)
    else:
        return render_template('registration.html', result='Пароли не совпадают')
    return render_template('index.html')


# Вход пользователя
@app.route('/run_input', methods=['GET', 'POST'])
def run_input():
    if request.method == 'POST':
        if 'token' in request.cookies:
            return render_template('authorized.html', email=request.cookies.get('email'))
        else:
            email = request.form.get('email')
            password = hashlib.sha256(request.form.get('pass').encode()).hexdigest()
            sql = f'select password, activ_group, is_active from users where email = "{email}";'
            try:
                data = connect_read(sql)[0]
            except:
                return render_template('index.html', result='Неверный логин или пароль')
            pass_db = data[0]
            group = data[1]
            if password == pass_db and data[2] == '1':
                resp = cookies(render_template('authorized.html', email=email), email, group)
                return resp
            return render_template('index.html', result='Неверный логин или пароль')
    else:
        return render_template('index.html')

# Выход
@app.route('/exit', methods=['POST'])
def output():
    resp = make_response(render_template('index.html'))
    del_cokie = request.cookies
    for i in del_cokie:
        resp.delete_cookie(i)
    return resp

# Ошибки 401 и 403
@app.before_request
def all_request():
    global app_session_key
    if request.cookies.get('token') == app_session_key:
        sql_page_users = f'select adress from pages join permissions p on p.page = pages.id where p.group_access = "{request.cookies.get('group')}";'
        page_users = [i[0] for i in connect_read(sql_page_users)]
        all_pages = [i[0] for i in connect_read((f'select adress from pages;'))]
        page = request.url.split('/')[-1]
        if page in page_users and request.cookies.get('token') == app_session_key:
            return cookies(render_template(page))
        elif page in page_users and request.cookies.get('token') != app_session_key:
            return abort(401)
        elif page not in page_users and page in all_pages:
            return abort(403)

# Удаление аккаунта
@app.route('/drop_user', methods=['GET', 'POST'])
def del_account():
    sql_drop = f'update users set is_active = 0 where email = "{request.cookies.get('email')}";'
    try:
        connect_write(sql_drop)
    except:
        return cookies(render_template('authorized.html', result='Ошибка изменения'))
    finally:
        return output()

# Изменение данных
@app.route('/update_users', methods=['GET', 'POST'])
def update_user():
    email = request.form.get('email')
    password = request.form.get('password')
    sql_drop = f'update users set email = "{email}", password = "{hashlib.sha256(password.encode()).hexdigest()}" where email = "{request.cookies.get('email')}";'
    try:
        connect_write(sql_drop)
    except:
        return cookies(render_template('authorized.html', result='Ошибка изменения'))
    finally:
        return output()

# Api methods
@app.route('/api/hello', methods=['GET'])
def api_read():
    return api_user()

if __name__ == '__main__':
    app.run(debug=True)
