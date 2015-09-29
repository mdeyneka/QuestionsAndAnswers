from datetime import datetime
import hashlib
from flask import Flask, render_template, Response, redirect, url_for, request, session, flash
from flask.ext.login import LoginManager, UserMixin, login_required
from sqlalchemy import and_
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, current_user, logout_user
from forms import LoginForm, RegistrationForm, QuestionForm, AnswerForm

app = Flask(__name__)

app.config.from_object("config")
login_manager = LoginManager()
database = SQLAlchemy(app)
login_manager.init_app(app)
app.config["SECRET_KEY"] = "ITSASECRET"


login_manager.login_view = "template_login"

from models import User, Question, Answer, Vote
database.create_all()

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route("/")
def template_test():
    return render_template('home.html')

@app.route('/login', methods=['GET','POST'])
def template_login():
    if session.get('logged_in'):
        flash("You are logged in already", "notice")
        return redirect("/")
    
    form = LoginForm()
    
    if form.validate_on_submit():
        print "after form validating"
        hash_of_password = hashlib.sha512(form.password.data).hexdigest()
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.password == hash_of_password:
                login_user(user)
                session['logged_in'] = True
                session['fullname'] = current_user.get_fullname()
                return redirect("/")
            else:
                flash("Login or password is incorrect","notice")
        else:
            flash("This user is not found", "notice")
            return redirect(request.referrer)
            
    return render_template('login.html', form=form)

@app.route('/registration', methods=['GET','POST'])
def template_registration():
    if session.get('logged_in'):
        return redirect("/")
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        firstname = form.firstname.data
        secondname = form.secondname.data
        email = form.email.data
        password = form.password.data
        hash_of_password = hashlib.sha512(password).hexdigest()
        
        if database.session.query(User).filter(User.email == email).first():
            flash("This email is occupied already", "notice")
            return redirect (url_for("template_registration"))

        user = User(first_name = firstname,
                    second_name = secondname,
                    email=email,
                    password=hash_of_password,
                    created_date = datetime.now()
                    )
        print "before creating new session for database"
        database.session.add(user)
        database.session.commit()
        return redirect("/")
    return render_template('registration.html', form=form)

@app.route("/home")
def template_home():
    return render_template('home.html')

@app.route("/about")
def template_about():
    return render_template('about.html')

@app.route("/contacts")
def template_contacts():
    return render_template('contacts.html')

@app.route("/questions", defaults={'question_id': None}, methods=['GET', 'POST'])
@app.route("/questions/<int:question_id>", methods=['GET', 'POST'])
def template_questions(question_id):
    if question_id is None:
        if session.get('logged_in'):
            question_form = QuestionForm()
            if question_form.validate_on_submit():
                question_theme = question_form.question_theme.data
                question_text = question_form.question_text.data
                question = Question(user_id = current_user.user_id,
                            question_theme = question_theme,
                            question_text = question_text,
                            created_date = datetime.now()
                            )
                database.session.add(question)
                database.session.commit()
                return redirect("/questions")
            result_questions = database.session.query(Question, database.func.count(Answer.answer_id). \
                                    label('countOf')). \
                                    outerjoin(Answer). \
                                    group_by(Question.question_id). \
                                    join(User, User.user_id==Question.user_id). \
                                    add_columns(Question.question_id, Question.question_theme, Question.created_date, \
                                                User.first_name, User.second_name). \
                                    order_by(Question.created_date.desc()).all()
            print "logged fullname = " + str(current_user.get_fullname())
            return render_template('questions.html', \
                                   my_list=result_questions, \
                                   logged_name = current_user.get_fullname(), \
                                    question_form=question_form)
        result_questions = database.session.query(Question, database.func.count(Answer.answer_id).label('countOf')). \
                                    outerjoin(Answer). \
                                    group_by(Question.question_id). \
                                    join(User, User.user_id==Question.user_id). \
                                    add_columns(Question.question_id, Question.question_theme, Question.created_date, \
                                                User.first_name, User.second_name). \
                                    order_by(Question.created_date.desc()).all()
        return render_template('questions.html', my_list=result_questions)
 
    subquery = database.session.query(Answer, database.func.sum(database.case([(Vote.state=="like", 1)], else_=0)). \
                                    label('sum_like'), \
                                    database.func.sum(database.case([(Vote.state=="dislike", 1)], else_=0)). \
                                    label('sum_dislike')). \
                                    add_columns(Vote.state).outerjoin(Vote).group_by(Answer.answer_id).subquery()
    result_answers = database.session.query(Answer).outerjoin(User).\
                            join(subquery, Answer.answer_id == subquery.c.answer_id).\
                            add_columns(Answer.answer_id, Answer.answer_text, Answer.created_date, \
                                        User.first_name, User.second_name, \
                                        subquery.c.sum_like, subquery.c.sum_dislike). \
                            filter(Answer.question_id == question_id).order_by(Answer.created_date).all()
    result_question = Question.query.join(User, User.user_id==Question.user_id). \
                            add_columns(Question.question_id, Question.question_theme, \
                                        Question.question_text, Question.created_date, \
                                        User.first_name, User.second_name). \
                            filter(Question.question_id == question_id).first()

    if session.get('logged_in'):
        answer_form = AnswerForm()
        if answer_form.validate_on_submit():
            answer_text = answer_form.answer_text.data
            answer = Answer(user_id = current_user.user_id,
                            question_id = question_id,
                            answer_text = answer_text,
                            created_date = datetime.now()
                            )
            database.session.add(answer)
            database.session.commit()
            return redirect("/questions/"+ str(question_id))
        return render_template('question.html', question_id = question_id, \
                                question_theme=result_question.question_theme, \
                                question_text = result_question.question_text, \
                                full_user_name = result_question.first_name + \
                                " " + result_question.second_name, \
                                created_date = result_question.created_date, \
                                my_answers_list = result_answers, \
                                answer_form=answer_form)
    
    return render_template('question.html', question_id = question_id, \
                           question_theme=result_question.question_theme, \
                           question_text = result_question.question_text, \
                           full_user_name = result_question.first_name + \
                            " " + result_question.second_name, \
                           created_date = result_question.created_date, \
                           my_answers_list = result_answers)
    
@app.route("/vote/<int:answer_id>/<string:state>", methods=["POST", "GET"])
def vote(answer_id, state):
    exists = database.session.query(Vote). \
            filter(and_(Vote.answer_id == answer_id, Vote.user_id == current_user.user_id)).first()
    if not exists:
        vote = Vote(
            user_id = current_user.user_id,
            answer_id = answer_id,
            state = state
        )
        database.session.add(vote)
        database.session.commit()
    else:
        print "you voted already"
    return redirect(request.referrer)

@app.route("/logout")
def template_logout():
    logout_user()
    session.pop('logged_in', None)
    return redirect("/")