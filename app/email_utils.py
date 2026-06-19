import logging
import os

import resend
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("imaq")

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY


def enviar_email_recuperacion(email: str, nombre: str, token: str) -> None:
    """Sends the password-reset email via Resend. Silently logs and skips if
    RESEND_API_KEY isn't configured (e.g. local development), so the
    recuperar-password endpoint can still respond 200 without crashing."""
    if not RESEND_API_KEY:
        logger.warning("RESEND_API_KEY no configurado; omitiendo envío de email a %s", email)
        return

    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"
    html = f"""
    <h2>Recuperar contraseña — iMaq</h2>
    <p>Hola {nombre}, recibimos una solicitud para restablecer tu contraseña.</p>
    <a href="{reset_link}" style="background:#1B4FD8;color:white;padding:12px 24px;border-radius:6px;text-decoration:none">
      Restablecer contraseña
    </a>
    <p>Este link expira en 15 minutos. Si no solicitaste esto, ignora este email.</p>
    """

    try:
        resend.Emails.send(
            {
                "from": "iMaq <onboarding@resend.dev>",
                "to": [email],
                "subject": "Recuperar contraseña — iMaq",
                "html": html,
            }
        )
    except Exception:
        logger.exception("No se pudo enviar el email de recuperación a %s", email)
