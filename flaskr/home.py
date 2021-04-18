from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session, Flask
)

from flaskr.db import get_db

import os
from multiprocessing import Value

counter = Value('i', 0)
app = Flask(__name__)

bp = Blueprint('home', __name__)

cookies_history = []

@bp.route('/')
def home():
    cookies_now = request.cookies.get('session')

    user_id = session.get('user_id')
    db = get_db()
    if user_id is not None:
        if cookies_now not in cookies_history:
            counter.value += 1
            out = counter.value
            cookies_history.append(cookies_now)

            user_id = session.get('user_id')
            
            user = db.execute(
                        'SELECT * FROM user WHERE id = ?', (user_id,)
                   ).fetchone()
            
            user_visit = user['visits']
            user_visit += 1
            
            db.execute('UPDATE user SET visits = ?'
                       ' WHERE id = ?',
                       (user_visit, user_id)
                      )
            
            db.commit()
        else:
            out = counter.value

            user = db.execute(
                        'SELECT * FROM user WHERE id = ?', (user_id,)
                   ).fetchone()
            
            user_visit = user['visits']
    else:
        out = counter.value
        user_visit = '-'

    image_path = os.path.join('static', 'JayImage', 'myImage.jpg')
    return render_template('home/home.html', image_path=image_path, visits=out, user_visit=user_visit)