from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField,DateField
from wtforms.validators import DataRequired, Email, EqualTo, InputRequired

class SignUpForm(FlaskForm):
    inputFirstName = StringField('First Name',
        [DataRequired(message="Please enter your first name!")])
    inputLastName = StringField('Last Name',
        [DataRequired(message="Please enter your last name!")])
    inputEmail = StringField('Email address',
        [Email(message="Not a valid email address!"),
        DataRequired(message="Please enter your email address!")])
    inputPassword = PasswordField('Password',
        [InputRequired(message="Please enter your password!"),
        EqualTo('inputConfirmPassword', message="Password does not match!")])
    inputConfirmPassword = PasswordField('Confirm password')
    submit = SubmitField('Sign Up')

class SignInForm(FlaskForm):
    inputEmail = StringField('Email address',
        [Email(message="Not a valid email address!"),
        DataRequired(message="Please enter your email address!")])
    inputPassword = PasswordField('Password',
        [InputRequired(message="Please enter your password!")])
    submit = SubmitField('Sign In')

class TaskForm(FlaskForm):
    inputDescription = StringField('Task Description',
        [DataRequired(message="Please enter your task content!")])
    inputDeadline = DateField('Project Deadline',
        [DataRequired(message="Please enter your task deadline!")])
    inputPriority = SelectField('Priority', coerce = int)    
  
    inputStatus = SelectField('Status', coerce = int)    
    submit = SubmitField('Create Task')
class ProjectForm(FlaskForm):
    inputName = StringField('Project Name',
        [DataRequired(message="Please enter your project name!")])
    inputDescription = StringField('Project Description',
        [DataRequired(message="Please enter your project description!")])
    inputDeadline = DateField('Project Deadline',
        [DataRequired(message="Please enter your project deadline!")])
    inputStatus = SelectField('Status', coerce = int)    
    submit = SubmitField('Create Project')


