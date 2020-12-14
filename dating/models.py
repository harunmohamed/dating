from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from dating import db, login_manager, app
from flask_login import UserMixin
from markdown import markdown
import bleach



@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

followers = db.Table(
	'followers',
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=True)
	dp = db.Column(db.String(20), nullable=False, default='default.jpg')
	dp2 = db.Column(db.String(20), nullable=False, default='flip.png')
	dp3 = db.Column(db.String(20), nullable=False, default='plane.png')
	password = db.Column(db.String(60), nullable=False)
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)
	date_joined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	department = db.Column(db.String(20), nullable=False)
	student_number = db.Column(db.Integer(), unique=True, nullable=True)
	age = db.Column(db.DateTime, nullable=False)
	gender = db.Column(db.String(20), nullable=False)
	country = db.Column(db.String(20), default="Cyprus", nullable=True)
	bio = db.Column(db.String(120), nullable=True)
	private = db.Column(db.Boolean, default=False, nullable=False)
	snapchat = db.Column(db.String(20), default="snapchat", nullable=True)
	instagram = db.Column(db.String(20), default="instagram", nullable=True)
	followed = db.relationship(
		'User', secondary=followers,
		primaryjoin=(followers.c.follower_id == id),
		secondaryjoin=(followers.c.followed_id == id),
		backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
	messages_sent = db.relationship('Message',
									foreign_keys='Message.sender_id',
									backref='author', lazy='dynamic')
	messages_received = db.relationship('Message',
										foreign_keys='Message.recipient_id',
										backref='recipient', lazy='dynamic')
	last_message_read_time = db.Column(db.DateTime)


	def get_reset_token(self, expires_sec=1800):
		s = Serializer(app.config['SECRET_KEY'], expires_sec)
		return s.dumps({'user_id' : self.id}).decode('utf-8')


	@staticmethod
	def verify_reset_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)


	def __repr__(self):
		return f"User('{self.username}' , '{self.email}', '{self.dp}')"

	def birthday(self):
		if self.age.month == datetime.today().month:
			if self.age.day == datetime.today().day:
				return True

	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)

	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)

	def is_following(self, user):
		return self.followed.filter(followers.c.followed_id == user.id).count() > 0

	def new_messages(self):
		last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
		return Message.query.filter_by(recipient=self).filter(
			Message.timestamp > last_read_time).count()

	@staticmethod
	def on_changed_body(target, value, oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
		'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
		'h3', 'p', 'iframe']
		target.content = bleach.linkify(bleach.clean(markdown(value, output_format='html'),
			tags=allowed_tags, strip=True))


class Message(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	body = db.Column(db.Text) #db.String(140)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

	@staticmethod
	def on_changed_body(target, value, oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
		'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
		'h1', 'h2', 'h3', 'p', 'iframe']
		target.body = bleach.linkify(bleach.clean(markdown(value, output_format='html'),
			tags=allowed_tags, strip=True))

	def __repr__(self):
		return '<Message {}>'.format(self.body)

