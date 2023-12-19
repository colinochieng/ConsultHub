#!/usr/bin/env python3
"""
module for emailing
"""
import yagmail
import os
from jinja2 import Environment, FileSystemLoader
from typing import Dict


sender_email = os.getenv("MAIL_SENDER", "colinatjku@gmail.com")
sender_password = os.getenv("MAIL_PASSWORD", "gwli cdnv vmpe kfzh")


def render_email_html(contexts: Dict, file: str) -> str:
    """
    a function to render a complete html body for emailing
    Args:
        contexts (dict): template variables
        file (str): name of file to read from
            assumes file is located in the templates dir
    return (str): complete html body, reay for sending
    """
    # Create a Jinja environment
    env = Environment(loader=FileSystemLoader("./api/utils/templates"))

    # HTML template
    template = env.get_template("response.html")

    # Render the template with the context variables
    output = template.render(**contexts)

    return output


def send_emails(subject, body_type, email_info) -> None:
    """
    Send emails using yagmail.

    Parameters:
    - subject (str): Email subject.
    - body_type (str): Html Email to be sent.
    - email_info (list): List of tuples made of
        contexts(template variables to replace)
        and email (mail addresses to send the emails to.)
    """
    yag = yagmail.SMTP(sender_email, sender_password)

    try:
        # Send emails to each recipient
        for context, to_email in email_info:
            # Send the email
            content = render_email_html(context, f"{body_type}.html")
            yag.send(to=to_email, subject=subject, contents=content)

    except Exception as e:
        print(f"Error sending email: {str(e)}")

    finally:
        # Close the SMTP connection
        yag.close()
