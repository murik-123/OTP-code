import os
import smtplib
import threading
import time
from email.message import EmailMessage

import OTP_generator as otp


SENDER_EMAIL = "muradkhandavudlu.25@gmail.com"
APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]


def send_otp_email(recipient, code):
    message = EmailMessage()
    message["Subject"] = "Your OTP code"
    message["From"] = SENDER_EMAIL
    message["To"] = recipient
    message.set_content(f"Your OTP code is: {code}")

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(SENDER_EMAIL, APP_PASSWORD)
        smtp.send_message(message)


def expire_otp_after(seconds, otp_state, expired):
    time.sleep(seconds)
    otp_state["code"] = ""
    expired.set()


def main():
    email = input("Enter your email: ").strip()
    code = otp.generate_code()
    otp_state = {"code": code}
    expired = threading.Event()

    try:
        send_otp_email(email, code)
    except Exception as error:
        print(f"Could not send the OTP email: {error}")
        return

    print("OTP sent. You have 1 minute to enter the code before it expires.")

    timer = threading.Thread(
        target=expire_otp_after,
        args=(60, otp_state, expired),
        daemon=True,
    )
    timer.start()

    entered_code = input("Enter your OTP code: ").strip()

    if expired.is_set():
        print("That code has expired. Please request a new one.")
    elif entered_code == otp_state["code"]:
        otp_state["code"] = ""
        print("Authenticating...")
        time.sleep(3)
        print("Authentication successful.")
    else:
        otp_state["code"] = ""
        print("That code is incorrect.")


if __name__ == "__main__":
    main()