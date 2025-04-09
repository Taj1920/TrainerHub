import smtplib
import random
import streamlit as st
#create a session 

def send_otp(email):
    try:
        s=smtplib.SMTP('smtp.gmail.com',587)
        s.starttls()
        app_email=st.secrets['email_credentials']['app_email']
        app_pwd=st.secrets['email_credentials']['app_pwd']
        s.login(app_email,app_pwd)
        otp=random.randint(1000,9999)
        message=f'''Hello user,
                    verify your account"s otp.
                    TrainerHub Password Reset OTP is: {otp}
                    This OTP is valid for 5 minutes. Do not share it with anyone. If you didn"t request this, please ignore this message.
                    '''

        s.sendmail(app_email,email,message)
        s.quit()
        return otp
    except smtplib.SMTPRecipientsRefused:
        st.error("Invalid recipient email address. Please check and try again")
def send_creds(email,uname,pwd):
    try:
        s=smtplib.SMTP('smtp.gmail.com',587)
        s.starttls()
        app_email=st.secrets['email_credentials']['app_email']
        app_pwd=st.secrets['email_credentials']['app_pwd']
        s.login(app_email,app_pwd)
        otp=random.randint(1000,9999)
        message=f'''Hello {uname},
        TrainerHub credentials: 

                    username: {uname}
                    password: {pwd}
                    
                    Do not share it with anyone. If you didn"t request this, please ignore this message.
                    '''
        s.sendmail(app_email,email,message)
        st.toast('Mail sent ✅..')
        s.quit()
    except smtplib.SMTPRecipientsRefused:
        st.error("Invalid recipient email address. Please check and try again")
