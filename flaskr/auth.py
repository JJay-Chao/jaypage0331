import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Flask
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


app = Flask(__name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.split('.')[-1].lower() in ALLOWED_EXTENSIONS


@bp.route('/register', methods=('GET', 'POST'))
def register():
    user_id = session.get('user_id')
    if user_id is not None:
        return redirect(url_for('blog.index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        myphoto = request.files['myphoto']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)
        
        if myphoto and allowed_file(myphoto.filename):
            filename = secure_filename(myphoto.filename)
        else:
            error = 'The selected file not supported!'
        
        mimetype = myphoto.mimetype


        if error is None:
            db.execute(
                'INSERT INTO user (myphoto, mimetype, username, password, visits) VALUES (?, ?, ?, ?, ?)',
                (myphoto.read(), mimetype, username, generate_password_hash(password), 0)
            )
            db.commit()
            return redirect(url_for('home'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    user_id = session.get('user_id')

    if user_id is not None:
        return redirect(url_for('blog.index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('home'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
