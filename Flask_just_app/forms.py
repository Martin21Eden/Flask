from wtforms import Form, StringField, PasswordField, validators, TextAreaField


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')])
    confirm = PasswordField('Confirm Password')


class SongForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    lyrics = TextAreaField('Lyrics', [validators.Length(min=30)])