from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import  UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import  UserChangeForm as DjangoUserChangeForm
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserCreationForm(DjangoUserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and password.
    """
    class Meta:
        model = User
        fields = ["email", "id_no", "first_name", "middle_name", "last_name", "security_question", "security_answer", "is_active", "is_staff", "is_superuser"]

    def clean_email(self):
        """
        Validate the email field.
        """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Email already exists."))
        return email

    def clean_id_no(self):
        """
        Validate the id_no field.
        """
        id_no = self.cleaned_data.get("id_no")
        if User.objects.filter(id_no=id_no).exists():
            raise forms.ValidationError(_("ID number already exists."))
        return id_no

    def clean(self):
        """
        Validate the form data.
        """
        cleaned_data = super().clean()
        security_answer = cleaned_data.get("security_answer")
        security_question = cleaned_data.get("security_question")
        is_superuser = cleaned_data.get("is_superuser")
        if not is_superuser:
            if not security_question:
                self.add_error("security_question", _("Security question is required."))
            if not security_answer:
                self.add_error("security_answer", _("Security answer is required."))
        return cleaned_data

    def save(self, commit=True):
        """
        Save the user instance.
        """
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

class UserChangeForm(DjangoUserChangeForm):
    """
    A form that updates a user from the given email and password.
    """
    class Meta:
        model = User
        fields = ["email", "id_no", "first_name", "middle_name", "last_name", "security_question", "security_answer", "is_active", "is_staff", "is_superuser"]

    def clean_email(self):
        """
        Validate the email field.
        """
        email = self.cleaned_data.get("email")
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError(_("Email already exists."))
        return email

    def clean_id_no(self):
        """
        Validate the id_no field.
        """
        id_no = self.cleaned_data.get("id_no")
        if User.objects.exclude(pk=self.instance.pk).filter(id_no=id_no).exists():
            raise forms.ValidationError(_("ID number already exists."))
        return id_no

    def clean(self):
        """
        Validate the form data.
        """
        cleaned_data = super().clean()
        security_answer = cleaned_data.get("security_answer")
        security_question = cleaned_data.get("security_question")
        is_superuser = cleaned_data.get("is_superuser")
        if not is_superuser:
            if not security_question:
                self.add_error("security_question", _("Security question is required."))
            if not security_answer:
                self.add_error("security_answer", _("Security answer is required."))
        return cleaned_data
