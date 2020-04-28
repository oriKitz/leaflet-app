from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length


class NewQuery(FlaskForm):
    query_name = StringField('Query Name', validators=[DataRequired(), Length(min=2, max=120)])
    query = TextAreaField('Query', validators=[DataRequired()])
    only_me = BooleanField('Private query (only I can see it)')
    only_team = BooleanField('Shared only to my team')
    submit = SubmitField('Save')
