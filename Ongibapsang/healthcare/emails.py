from typing import List, Dict, Any
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger("emails")

def send_report_email(link_url: str, to_emails: List[str], subject: str, ctx: Dict[str, Any] | None = None) -> int:
    if not to_emails:
        raise ValueError("수신자 목록이 비었습니다.")

    context = {
        "site_name": getattr(settings, "SITE_NAME", "서비스"),
        "site_domain": getattr(settings, "SITE_DOMAIN", ""),
        "link_url": link_url,
        "brand_color": getattr(settings, "BRAND_PRIMARY_COLOR", "#444444"),
        "button_text": "보고서 열기",
    }
    if ctx:
        context.update(ctx)

    html = render_to_string("emails/report_link.html", context)
    text = (render_to_string("emails/report_link.txt", context) or strip_tags(html)).strip()

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=to_emails,
    )
    msg.attach_alternative(html, "text/html")
    sent = msg.send(fail_silently=False)
    logger.info("Report email sent: to=%s count=%s", to_emails, sent)
    return sent
