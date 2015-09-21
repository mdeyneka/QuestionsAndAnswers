from flask.ext.wtf import Form
from wtforms import StringField, IntegerField, BooleanField, PasswordField, validators, TextAreaField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Length

class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class QuestionForm(Form):
    question_theme = StringField('Question Theme', validators=[DataRequired()])
    question_text = StringField('Question', widget=TextArea(), validators=[DataRequired()])
    
class RegistrationForm(Form):
    firstname = StringField('First name', validators=[DataRequired()])
    secondname = StringField('Second name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    

class AnswerForm(Form):
    answer_text = StringField('Answer text', widget=TextArea(), validators=[DataRequired()])