from sqlalchemy.types import Enum
from app import database, app

class User(database.Model):
    __tablename__ = 'users'
    user_id = database.Column(database.Integer, primary_key=True)
    first_name = database.Column(database.String(50))   
    second_name = database.Column(database.String(50))
    email = database.Column(database.String(50), unique=True)
    root = database.Column(database.Boolean, default=False)
    password = database.Column(database.String(200))
    created_date = database.Column(database.DateTime())
    questions = database.relationship("Question", backref = "author", lazy = "dynamic" )
    answers = database.relationship("Answer", backref = "author", lazy = "dynamic" )
    
    def __unicode__(self):
        return str(self.user_id)

    def is_active(self):
        return True

    def is_anonymous(self):
        return False
    
    def get_id(self):
        return unicode(self.user_id)
    
    def get_fullname(self):
        return str(self.first_name) + " " + str(self.second_name)
    
    def __str__(self):
        return "user_id = " + str(self.user_id) + "\n first_name= " + self.first_name
    
    def __repr__(self):
        return "user_id = " + str(self.user_id) + "\n first_name = " + self.first_name \
                + "\n second+name = " + self.second_name + "\n email = " + self.email \
                + "\n is_active = " + str(self.is_active)
            
class Question(database.Model):
    __tablename__ = 'questions'
    question_id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer, database.ForeignKey('users.user_id'))
    question_theme = database.Column(database.String)
    question_text = database.Column(database.String)
    created_date = database.Column(database.DateTime())
    
    def __unicode__(self):
        return str(self.question_id)
    
    def get_id(self):
        return unicode(self.question_id)
    
    def __repr__(self):
        return unicode(self.question_theme)
    
class Answer(database.Model):
    __tablename__ = 'answers'
    answer_id = database.Column(database.Integer, primary_key=True)
    user_id = database.Column(database.Integer, database.ForeignKey('users.user_id'))
    question_id = database.Column(database.Integer, database.ForeignKey('questions.question_id'))
    answer_text = database.Column(database.String)
    created_date = database.Column(database.DateTime())
    
    def __unicode__(self):
        return str(self.answer_id)
    
    def get_id(self):
        return unicode(self.answer_id)
    
    def __repr__(self):
        return unicode("answer_id = " + str(self.answer_id) + "\n answer_text = " + self.answer_text) \
                        + "\n question_id = " + str(self.question_id)
                    
class Vote(database.Model):
    __tablename__ = 'votes'
    vote_id = database.Column(database.Integer, primary_key=True)
    answer_id = database.Column(database.Integer, database.ForeignKey('answers.answer_id'))
    user_id = database.Column(database.Integer, database.ForeignKey('users.user_id'))
    state = database.Column(Enum('like','dislike'), nullable=True)
    
    def __unicode__(self):
        return str(self.vote_id)
    
    def get_id(self):
        return unicode(self.vote_id)

    def __repr__(self):
        return unicode("vote_id = " + str(self.vote_id) + "\n answer_id = " + str(self.answer_id) + "\n user_id = " + str(self.user_id))
    