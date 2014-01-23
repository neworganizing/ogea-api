from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, BooleanField
from wtforms.validators import Required

from flask.ext.wtf.html5 import EmailField
#import config as c
import psycopg2
"""
import sys,os,os.path
sys.path.append('/usr/local/noi/GIT_EXACT_OGEA/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'ogea.settings'
from django.contrib.auth.models import User
"""
class LoginForm(Form):
    username = TextField('username', validators = [Required()])
    password = PasswordField('password', validators = [Required()])
    """
    def validate(self):
        if not(Form.validate(self)):
            return -1
        try:
            user = User.objects.get(username__exact=self.username.data)
            if (user.check_password(self.username.password)):
                return 1
            else:
                return -3
        except:
            return -2
"""
    def validate(self):
        # Dummy authentication
        return 1

        #if not(Form.validate(self)):
        #    return -1
        #elif self.username.data == c.username and self.password.data == c.password:
        #    return 1
        
"""
class RegForm(Form):
    first_name = TextField('first_name', validators = [Required()])
    last_name = TextField('last_name', validators = [Required()])
    email = EmailField('email', validators = [Required()])
    org = TextField('org', validators = [Required()])
    username = TextField('username', validators = [Required()])
    password = PasswordField('password', validators = [Required()])
    password2 = PasswordField('password2', validators = [Required()])
"""
