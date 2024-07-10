import logging
import os
from email.mime.application import MIMEApplication

from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives

from django.conf import settings

LOGGER = logging.getLogger(__name__)


class MailSender:
    """Encapsulates functions to send emails."""

    def __init__(self):
        pass

    def send_password_reset_confirm_email(self, from_email, recipients_list, reply_tos=None, **kwargs):
        template = get_template("email_templates/password_reset_template.html")
        html = template.render(kwargs)
        LOGGER.info(f"Sending email to {recipients_list} . . .")

        self.send_email(
            from_email=from_email,
            recipients_list=recipients_list,
            subject="AOSBP App Password Reset",
            text_content="AOSBP App Password Reset",
            html_content=html,
            reply_tos=reply_tos,
        )

    def send_email(
        self,
        recipients_list,
        subject,
        text_content,
        html_content,
        from_email=None,
        reply_tos=None,
    ):
        """
        Sends an email.

        Note: If your account is in the Amazon SES  sandbox, the source and
        destination email accounts must both be verified.

        :param from_email: The source email account.
        :param recipients_list: The list of one or more destination email accounts.
        :param subject: The subject of the email.
        :param text_content: The plain text version of the body of the email.
        :param html_content: The HTML version of the body of the email.
        :param reply_tos: Email accounts that will receive a reply if the recipient
                          replies to the message.
        :return: The ID of the message, assigned by Amazon SES.
        """

        # Create the email message
        if not isinstance(recipients_list, list):
            recipients_list = [recipients_list]

        if not from_email:
            from_email = settings.EMAIL_SENDER

        email_message = EmailMultiAlternatives(subject, "", from_email, recipients_list)
        email_message.attach_alternative(html_content, "text/html")

        logo_attachment = "templates/email_templates/images/email-logo-header.png"

        # Define the attachment part and encode it using MIMEApplication.
        att = MIMEApplication(open(logo_attachment, "rb").read())

        # Add a header to tell the email client to treat this part as an attachment,
        # and to give the attachment a name.
        att.add_header("Content-ID", "<logo>")
        att.add_header("Content-Disposition", "attachment", filename=os.path.basename(logo_attachment))
        # att.set_disposition(f"inline; filename=\"{logo_attachment}\"")

        # Add the attachment to the parent container.
        email_message.attach(att)
        # email_message.attach_alternative(att, "image/png")
        email_message.send()
        try:
            message_id = email_message.send()
        except Exception:
            LOGGER.exception(
                f"Couldn't send mail from {from_email} to {recipients_list}.",
            )
            raise
        else:
            return message_id


if __name__ == "__main__":
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    django.setup()

    LOGGER.info("Starting email example")
    # Create SES client

    LOGGER.info("Client initialized . . .")

    my_sender = MailSender()

    my_sender.send_password_reset_confirm_email(
        from_email=settings.EMAIL_SENDER,
        recipients_list=["PUT_EMAIL_ADDRESS_HERE"],
    )
