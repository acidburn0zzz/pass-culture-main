from dataclasses import asdict
import logging
import typing

from .. import models
from .base import BaseBackend


logger = logging.getLogger(__name__)


class LoggerBackend(BaseBackend):
    """A backend that logs e-mail instead of sending it.
    It should be used for local development, and on testing/staging
    when performing load tests when we don't want to overload Sendinblue.
    """

    def send_mail(
        self,
        recipients: typing.Iterable[str],
        data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData,
        bcc_recipients: typing.Iterable[str] = None,
    ) -> models.MailResult:
        recipients = ", ".join(recipients)
        if bcc_recipients:
            bcc_recipients = ", ".join(bcc_recipients)
        sent_data = asdict(data)
        logger.info("An e-mail would be sent via Sendinblue to=%s, bcc=%s: %s", recipients, bcc_recipients, sent_data)
        result = models.MailResult(sent_data=sent_data, successful=True)

        return result
