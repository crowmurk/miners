from django import forms
from django.core.exceptions import ValidationError
from django.core.mail import BadHeaderError, mail_managers
from django.utils.translation import gettext_lazy as _


class ContactForm(forms.Form):
    FEEDBACK = 'F'
    CORRECTION = 'C'
    SUPPORT = 'S'
    # Значения отображаются пользователю в форме
    REASON_CHOICES = (
        (FEEDBACK, _('Feedback')),
        (CORRECTION, _('Correction')),
        (SUPPORT, _('Support')),
    )
    reason = forms.ChoiceField(
        choices=REASON_CHOICES,
        initial=FEEDBACK,
        label=_('Reason'),
    )
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={'placeholder': 'youremail@domain.com'},
        ),
        required=False,
        label=_('Email'),
    )
    text = forms.CharField(
        widget=forms.Textarea,
        label=_('Message'),
    )

    def send_mail(self):
        reason = self.cleaned_data.get('reason')
        reason_dict = dict(self.REASON_CHOICES)
        full_reason = reason_dict.get(reason)
        email = self.cleaned_data.get('email')
        text = self.cleaned_data.get('text')
        body = _('Message From') + ': {}\n\n{}\n'.format(
            email, text)
        try:
            mail_managers(full_reason, body)
        except BadHeaderError:
            self.add_error(
                None,
                ValidationError(
                    _('Could Not Send Email.\n'
                      'Extra Headers not allowed '
                      'in email body.'),
                    code='badheader'))
            return False
        else:
            return True
