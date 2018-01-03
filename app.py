from flask import Flask, render_template, flash, request, redirect, url_for
import redis
from flask_wtf import FlaskForm, CsrfProtect
from wtforms import *
from flask_zurb_foundation import Foundation
from flask_classy import FlaskView, route

app = Flask(__name__)
Foundation(app)
app.config['SECRET_KEY'] = 'redis_app'
csrf = CsrfProtect()
csrf.init_app(app)

r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0, charset="utf-8", decode_responses=True)


class QuestionForm(FlaskForm):
    title = StringField('Title Question')
    question = TextAreaField('Question')
    author = StringField('Author Name')
    submit = SubmitField(' ')


class ApplicationViews(FlaskView):
    route_base = '/'

    @route('/', methods=['GET', 'POST'])
    def index(self):
        question_form = QuestionForm()

        if request.method == 'POST' and question_form.validate_on_submit():
            # Verify if the Key exist in redis.
            if not r.exists('people'):
                try:
                    r.set('people', question_form.author.data)
                    flash('Record was Added!')
                    return redirect(url_for('ApplicationViews:index'))
                except Exception:
                    flash('Server Error!')
                    return redirect(url_for('ApplicationViews:index'))

            try:
                # Add user to the key store
                add_user = r.append('people', question_form.author.data)
                if add_user is not None:
                    flash('Successfully added record!')
                    return redirect(url_for('ApplicationViews:index'))

                flash('Record was not Added!')
                return redirect(url_for('ApplicationViews:index'))
            except Exception:
                flash('Server Error!')
                return redirect(url_for('ApplicationViews:index'))
            finally:
                flash('Done!')

        return render_template('redis.html', form=question_form)
	
    @route('/get_all', methods=['GET', 'POST'])
    def get_all(self):
	    query = r.get('people')
	    return query

ApplicationViews.register(app)

if __name__ == '__main__':
    app.run(debug=True)