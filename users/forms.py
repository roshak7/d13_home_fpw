from django.utils.translation import ugettext as _
from django.contrib.auth.models import Group, User
from django.forms import ModelForm

from django.urls import reverse

from allauth.account.signals import user_signed_up
from django.dispatch import receiver


from allauth.account.forms import LoginForm, SignupForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML


class UserChangeForm(ModelForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        labels = {'username': 'Псевдоним', 'first_name': 'Имя', 'last_name': 'Фамилия', 'email': 'Электронная почта'}

class CustomLoginForm(LoginForm):

    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        # Add magic stuff to redirect back.
        self.helper.layout.append(
            HTML(
                "{% if redirect_field_value %}"
                "<input type='hidden' name='{{ redirect_field_name }}'"
                " value='{{ redirect_field_value }}' />"
                "{% endif %}"
            )
        )
        # Add password reset link.
        self.helper.layout.append(
            HTML(
                "<p><a class='button secondaryAction' href={url}>{text}</a></p>".format(
                    url=reverse('account_reset_password'),
                    text=_('Забыли пароль?')
                )
            )
        )
        # Add submit button like in original form.
        self.helper.layout.append(
            HTML(
                '<button class="btn btn-primary" type="submit">'
                '%s</button>' % _('Войти')
            )
        )

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-xs-4 hide'
        self.helper.field_class = 'col-xs-8'


class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)
        return user

@receiver(user_signed_up)
def user_signed_up_(request, user, **kwargs):
    Group.objects.get(name='common').user_set.add(user)
    user.save()
