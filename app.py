import pickle
import time
import streamlit as st
st.set_page_config(page_title='TrainerHub',page_icon='images/trainerhub_page_icon.png',layout='wide',initial_sidebar_state='auto')

from auth import *
from datetime import datetime


st.markdown("""
    <style>
        .block-container {
            padding-top: 1 !important;
            margin-top: -90px;
        }
    </style>
""", unsafe_allow_html=True)

from streamlit_cookies_manager import EncryptedCookieManager
cookies=EncryptedCookieManager(prefix='trainerhub_',password='Python#@!')
if not cookies.ready():
    st.stop()
if 'id' not in st.session_state:
    st.session_state.id=cookies.get('id','')
if 'user' not in st.session_state:
    st.session_state.user=cookies.get('user','')
if 'logged_in' not in st.session_state:
    st.session_state.logged_in=cookies.get('logged_in')=='True'
if 'role' not in st.session_state:
    st.session_state.role=cookies.get('role','')

@st.dialog('Set new password')
def forgot_pwd():
    empid=st.text_input('🪪**Employee Id** ',placeholder='Enter username..',key='reset_empid')
    new_pwd=st.text_input('🔑**New Password** ',placeholder='Enter new password..',type='password',key='new_pwd')
    confirm=st.text_input('🔑**Confirm Password** ',placeholder='confirm',type='password',key='confirm_pwd')
    if st.button('**Reset password**'):
        if empid and new_pwd and confirm:
            if new_pwd==confirm:
                if (empid,) in check_empid(empid):
                    from otp import send_otp
                    email=get_email(empid)
                    st.text('An otp is sent to your registered email.')
                    sent_otp=send_otp(email)
                    st.session_state.sent_otp=sent_otp
                    st.session_state.show_otp_inp=True
                    
                else:
                    st.error('you are not signed up')
            else:
                st.error("password does'nt match")
        else:
            st.error('enter details..')
    if st.session_state.get('show_otp_inp',False):
        user_otp=st.text_input('**Enter Otp**',placeholder='Enter otp')
        if st.button('**Verify**'):
            if 'sent_otp' in st.session_state and int(user_otp)==st.session_state.sent_otp:
                update_pwd(empid,pickle.dumps(new_pwd))
                st.success('Password updated ✅')
                st.session_state.sent_otp=None
                st.session_state.show_otp_inp=False
                time.sleep(1)
                st.rerun()
            else:
                st.error('Incorrect otp..')




def login():
    a1,a2,a3=st.columns([2.2,2,1])
    col1,col2,col3=st.columns([1,1.5,1])
    a2.image('images/trainerhub_logo.png',width=170)
    col2.markdown('''<h3 style="text-align:center;color: #FFFF;">Login to your Account..</h2>''',unsafe_allow_html=True)
    with col2:
        with st.container(border=True):
            uname=st.text_input('👤**Username** ',placeholder='Enter username...',key='username')
            empid=st.text_input('🪪**Employee Id** ',placeholder='Enter Id...',key='empid').upper()
            pwd=st.text_input('🔑**Password** ',placeholder='Enter password...',type='password',key='password')
            c1,c2=st.columns([3,1])
            with c2:
                st.button('Forgot password?',on_click=forgot_pwd,type='tertiary')
            role=st.radio('**Role**',options=['Trainer','Manager','Admin'],horizontal=True,key='Role')
            a1,a2,a3=st.columns([2,2,1])
            if a2.button('**Login**',type='primary'):
                if uname and pwd and role:
                    if role in ['Trainer','Manager']:
                        if (uname,) in check_uname(uname):
                            if (empid,) in check_empid(empid):
                                dec_pwd=pickle.loads(check_pwd(uname))
                                if pwd==dec_pwd:
                                    if role==check_role(uname):
                                        if check_status(empid)=='Active':
                                            st.session_state.user=uname
                                            st.session_state.id=empid
                                            st.session_state.logged_in=True
                                            st.session_state.role=role
                                            cookies['user']=uname
                                            cookies['id']=empid
                                            cookies['logged_in']='True'
                                            cookies['role']=role
                                            cookies.save()
                                            st.toast('Login successful',icon='✅')
                                            time.sleep(1)
                                            st.rerun()
                                        else:
                                            st.warning('you are blocked contact admin',icon='⚠️')
                                    else:
                                        st.error(f'you are not {role}')
                                else:
                                    st.error("Incorrect password")
                            else:
                                st.error('Incorrect Employee Id')
                        else:
                            st.error('signup required')
                    elif role=='Admin':
                        if uname==st.secrets['credentials']['admin_username']:
                            if pwd==st.secrets['credentials']['admin_password']:
                                st.session_state.user='Admin'
                                st.session_state.logged_in=True
                                st.session_state.role=role
                                cookies['user']='Admin'
                                cookies['logged_in']='True'
                                cookies['role']=role
                                cookies.save()
                                st.toast('Logged in as Admin🅰️')
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error('Incorrect password')
                        else:
                            st.error('Incorrect username')
                else:
                    st.error('enter details..')    

if not(st.session_state.logged_in):
    login()
    


#greet msg
greet_display=st.empty()
def greet():
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        greeting = "Good Morning"
    elif 12 <= current_hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    greet_display.subheader(f"{greeting}, {st.session_state.user} 👋")
    

#After login
if st.session_state.logged_in:
    st.logo('images/trainerhub_logo.png',icon_image='images/trainerhub_logo.png',size='large')
    #Admin interface
    if st.session_state.role=='Admin':
        st.markdown("<h1 style='text-align:center;font-size:25px;color:orange'>Admin Dashboard</h1>", unsafe_allow_html=True)
        greet()
        from admin import *
        admin_interface()

    #Trainer interface
    elif st.session_state.role=='Trainer':
        from trainer import trainer_interface
        trainer_interface(st.session_state.id,st.session_state.user,st.session_state.role)
    
    #Manager interface
    elif st.session_state.role=='Manager':
        from manager import manager_interface
        manager_interface(st.session_state.id,st.session_state.user,st.session_state.role)

    #time refresh
    if 'last_refresh_hour' not in st.session_state:
            st.session_state.last_refresh_hour = datetime.now().hour
    if datetime.now().hour != st.session_state.last_refresh_hour:
        st.session_state.last_refresh_hour = datetime.now().hour
        st.rerun()
    c1,c2=st.sidebar.columns([0.23,1])
    if c2.button('**Logout**',type='primary'):
        #clear cookies
        cookies['logged_in']='False'
        cookies['user']=''
        cookies['role']=''
        cookies.save()
        #clear session state
        st.session_state.logged_in=False
        st.session_state.user=''
        st.session_state.role=''
        st.rerun()


