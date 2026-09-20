import asyncio

import resend
from fastapi.templating import Jinja2Templates

from config import settings

templates = Jinja2Templates(directory="templates")

resend.api_key = settings.resend_api_key.get_secret_value()


async def send_email(to_email: str, subject: str, plain_text: str, html_content: str | None = None) -> None:
    params: dict[str, str] = {
        "from": settings.resend_from,
        "to": to_email,
        "subject": subject,
        "text": plain_text,
    }

    if html_content:
        params["html"] = html_content

    await asyncio.to_thread(resend.Emails.send, params)


async def send_password_reset_email(to_email: str, username: str, token: str) -> None:
    reset_url = f"{settings.frontend_url}/reset-password?token={token}"

    template = templates.env.get_template("email/password_reset.html")
    html_content = template.render(reset_url=reset_url, username=username)

    plain_text = f"""Hi {username},

You requested to reset your password. Click the link below to set a new password:

{reset_url}

This link will expire in 1 hour.

If you didn't request this, you can safely ignore this email.

Best regards,
The FastAPI Blog Team
"""

    await send_email(
        to_email=to_email,
        subject="Reset Your Password - FastAPI Blog",
        plain_text=plain_text,
        html_content=html_content,
    )
