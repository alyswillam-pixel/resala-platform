from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django import forms as django_forms
from django.contrib.auth import forms as admin_forms
from django.forms import EmailField
from django.utils.translation import gettext_lazy as _

from .models import User


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User
        field_classes = {"auc_email": EmailField}


class UserAdminCreationForm(admin_forms.AdminUserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Passwords are auto-generated in save_model, so remove these fields
        # entirely rather than just making them optional.
        self.fields.pop("password1", None)
        self.fields.pop("password2", None)

    def clean(self):
        # Skip the entire auth form password validation chain.
        # Passwords are auto-generated in save_model.
        return django_forms.ModelForm.clean(self)

    def _post_clean(self):
        # Skip the password strength validators that UserCreationForm runs.
        django_forms.ModelForm._post_clean(self)

    def save(self, commit=True):
        # Skip the auth form's set_password_and_save() — password is
        # generated in UserAdmin.save_model and emailed via Celery.
        return django_forms.ModelForm.save(self, commit=commit)

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        fields = ("auc_email", "auc_id", "committee_role")
        field_classes = {"auc_email": EmailField}
        error_messages = {
            "auc_email": {"unique": _("This email has already been taken.")},
        }


class UserSignupForm(SignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """
