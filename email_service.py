from flask_mail import Message
from extensions import mail


def send_welcome_email(user, verify_url):
    msg = Message(
        subject="Verify your Enock Nyame Quiz account",
        recipients=[user.email]
    )
    msg.html = f"""
    <div style="font-family:Segoe UI,sans-serif; background:#0f172a; padding:40px; color:#e2e8f0;">
      <div style="max-width:520px; margin:0 auto; background:#1e293b; border-radius:12px; padding:32px;">
        <h2 style="color:#a5b4fc;">Welcome to Enock Nyame's Quiz, {user.username}! 🧠</h2>
        <p style="color:#cbd5e1;">Thanks for registering! Please verify your email to activate your account.</p>
        <a href="{verify_url}"
           style="display:inline-block; margin:20px 0; padding:12px 28px; background:#6366f1;
                  color:#ffffff; border-radius:8px; text-decoration:none; font-weight:600; font-size:16px;"
           target="_blank">
          Verify My Account
        </a>
        <p style="color:#94a3b8; font-size:0.85rem;">Or copy this link into your browser:<br/>
          <span style="color:#a5b4fc;">{verify_url}</span>
        </p>
        <p style="color:#64748b; font-size:0.85rem;">This link expires in 24 hours.</p>
      </div>
    </div>
    """
    mail.send(msg)


def send_password_reset_email(user, reset_url):
    msg = Message(
        subject="Reset your Enock Nyame Quiz password",
        recipients=[user.email]
    )
    msg.html = f"""
    <div style="font-family:Segoe UI,sans-serif; background:#0f172a; padding:40px; color:#e2e8f0;">
      <div style="max-width:520px; margin:0 auto; background:#1e293b; border-radius:12px; padding:32px;">
        <h2 style="color:#a5b4fc;">Password Reset Request 🔑</h2>
        <p style="color:#cbd5e1;">Hi {user.username}, click the button below to reset your password.</p>
        <a href="{reset_url}"
           style="display:inline-block; margin:20px 0; padding:12px 28px; background:#6366f1;
                  color:#ffffff; border-radius:8px; text-decoration:none; font-weight:600; font-size:16px;"
           target="_blank">
          Reset My Password
        </a>
        <p style="color:#94a3b8; font-size:0.85rem;">Or copy this link into your browser:<br/>
          <span style="color:#a5b4fc;">{reset_url}</span>
        </p>
        <p style="color:#64748b; font-size:0.85rem;">This link expires in 1 hour. If you did not request this, ignore this email.</p>
      </div>
    </div>
    """
    mail.send(msg)


def send_ban_email(user):
    msg = Message(
        subject="Enock Nyame Quiz — Account Suspended",
        recipients=[user.email]
    )
    msg.html = f"""
    <div style="font-family:Segoe UI,sans-serif; background:#0f172a; padding:40px; color:#e2e8f0;">
      <div style="max-width:520px; margin:0 auto; background:#1e293b; border-radius:12px; padding:32px;">
        <h2 style="color:#ef4444;">Account Suspended ⚠️</h2>
        <p style="color:#cbd5e1;">Hi {user.username}, your account has been suspended by an administrator.</p>
        <p style="color:#cbd5e1;">If you believe this is a mistake, please contact support.</p>
      </div>
    </div>
    """
    mail.send(msg)