from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, RadioField, DateField
from flask_pagedown.fields import PageDownField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from dating.models import User

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators = [DataRequired(), Length(min=2, max=20), Regexp(r'^[\w.-_.]+$', message='No Spaces. Use "-" or "_" or "." instead')]) 
	department = StringField('Department', validators=[DataRequired()])
	age = DateField('birthday', format='%Y-%m-%d', validators=[DataRequired()])
	gender = RadioField('Gender', choices=[('male','male'),('female','female')])
	password = PasswordField('Password', validators = [DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('That username is taken. Please choose a different one')


class LoginForm(FlaskForm):
	username = StringField('Username', validators = [DataRequired()]) 
	password = PasswordField('Password', validators = [DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
	username = StringField('Username', validators = [DataRequired(), Length(min=2, max=20), Regexp(r'^[\w.-_.]+$')])
	email = StringField('Email', validators = [Email(), DataRequired()])
	picture = FileField('Pic 1', validators=[FileAllowed(['jpg', 'jpeg' , 'png'])])
	picture2 = FileField('Pic 2', validators=[FileAllowed(['jpg', 'jpeg' , 'png'])])
	picture3 = FileField('Pic 3', validators=[FileAllowed(['jpg', 'jpeg' , 'png'])])
	department = StringField('Department', validators=[DataRequired()])
	student_number = StringField('Student Number', validators=[])
	country = StringField('Country', validators=[DataRequired()])
	age = DateField('Birthday', format='%d-%m-%Y', validators=[DataRequired()])
	snapchat = StringField('Snapchat')
	instagram = StringField('Instagram')
	bio = PageDownField('Bio')
	private = BooleanField('Go Private?')
	submit = SubmitField('Update')

	def validate_username(self, username):
		if username.data != current_user.username:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('That username is taken. Please choose a different one')

	def validate_email(self, email):
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('That email is taken. Please choose a different one')

class MessageForm(FlaskForm):
    message = TextAreaField((''), validators=[DataRequired()]) #Length(min=0, max=140)
    submit = SubmitField('🛫')


class RequestResetForm(FlaskForm):
	email = StringField('Email', validators = [DataRequired(), Email()])
	submit = SubmitField('Request Password Reset')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is None:
			raise ValidationError('There is no account with that email. You must register first')


class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password', validators = [DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])
	submit = SubmitField('Reset Password')
