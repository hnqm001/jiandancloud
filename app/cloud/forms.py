from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    name = StringField('搜索文件', validators=[DataRequired()], render_kw={
                       'placeholder': '请输入要搜索的内容'})
    submit = SubmitField('搜索')
