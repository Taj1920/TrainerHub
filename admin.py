import pandas as pd
import streamlit as st
import time
import pickle
from auth import *
from otp import send_creds
from db import get_db_connection
conn=get_db_connection()
cursor=conn.cursor()

def update_role(id,new_role):
    cursor.execute('UPDATE USER SET ROLE=? WHERE EMPID=?',(new_role,id))
    conn.commit()
def update_status(id,new_status):
    cursor.execute('UPDATE USER SET STATUS=? WHERE EMPID=?',(new_status,id))
    conn.commit()
    st.toast(f'☑️ User {id}- {new_status}')


def get_users():
    return list(conn.execute('SELECT EMPID,USERNAME,ROLE,STATUS FROM USER'))

@st.dialog('Update role')
def select_role_widget(id):
    new_role=st.selectbox('**select role**',options=['Trainer','Manager'],key=f'select_{id}')
    if st.button('confirm'):
        update_role(id,new_role)
        st.success(f'User role updated to {new_role} ✅') 
        st.session_state.user_data=get_users()
        time.sleep(1.5)
        st.rerun()


def admin_interface():
    m1,m2,m3,m4=st.columns(4)
    if 'user_data' not in st.session_state:
        st.session_state.user_data=get_users()
    if st.session_state.user_data:
        df=pd.DataFrame(st.session_state.user_data,columns=['empid','user','role','status'])
        with m1:
            with st.container(border=True):
                st.metric('**Total Users**',value=df['user'].count())
        with m2:
            with st.container(border=True):
                st.metric('**Trainers**',value=df['user'][df['role']=='Trainer'].count())
        with m3:
            with st.container(border=True):
                st.metric('**Managers**',value=df['user'][df['role']=='Manager'].count()) 
        with m4:
            with st.container(border=True):
                a1,a2=st.columns(2)
                a1.metric('**Active**',value=df['status'][df['status']=='Active'].count()) 
                a2.metric('**Blocked**',value=df['status'][df['status']=='Blocked'].count()) 
    search=st.sidebar.text_input(' ',placeholder='🔍 search user...')
    selected=st.sidebar.selectbox('**Filter**',options=['All','Trainer','Manager','Active','Blocked'],key='selected')
    tab1,tab2,tab3,tab4=st.tabs(['User Management ⚙️','Create user👤➕','Update user♻️','Delete user 🗑️'])
    with tab1:
        head1,head2,head3,head4,head5=st.columns([1,1,1,1,1])
        head1.markdown('##### Empid')
        head2.markdown('##### User')
        head3.markdown('##### Role')
        head4.markdown('##### Update role')
        head5.markdown('##### Active/Blocked')
            
        with st.container(border=True,height=300):
            col1,col2,col3,col4,col5=st.columns(5)
            if st.session_state.user_data:
                for i in st.session_state.user_data:
                    if i[1].startswith(search) and (i[2]==selected or selected=='All' or i[3]==selected):
                        with col1:
                            st.write(f'{i[0]}')
                            st.write(' ')
                        with col2:
                            st.write(f'{i[1]}')
                            st.write(' ')
                        with col3:
                            st.write(i[2])
                            st.write(' ')
                        with col4:
                            if st.button('Update',key=i[0]):
                                select_role_widget(i[0])
                        with col5:
                            is_active=i[3]=='Active'
                            toggle=st.toggle(f'{i[3]} ',value=is_active,key=f'toggle_{i[0]}')
                            if toggle and i[3]=='Blocked':
                                update_status(i[0],'Active')
                                st.session_state.user_data=get_users()
                                time.sleep(1.5)
                                st.rerun()
                            elif not(toggle) and i[3]=='Active':
                                update_status(i[0],'Blocked')
                                st.session_state.user_data=get_users()
                                time.sleep(1.5)
                                st.rerun()

                            st.write(' ')
                            
            else:
                st.write('No users yet..')
    
    with tab2:
        col1,col2,col3=st.columns([1,1.5,1])
        with col2:
            with st.container(border=True):
                uname=st.text_input('👤**Username** ',placeholder='Enter username...')
                empid=st.text_input('🪪**Employee Id** ',placeholder='Enter Id...').upper()
                email=st.text_input('📧**Email** ',placeholder='Enter Email...')
                office_email=st.text_input('📧**Official Email** ',placeholder='Enter Email...',key='official_mail')
                contact=st.text_input('📧**Contact** ',placeholder='Enter mobile no...',key='mobile')
                pwd=st.text_input('🔑**Password** ',placeholder='Enter password...',type='password')
                confirm=st.text_input('🔑**Confirm Password** ',placeholder='confirm',type='password')
                if st.button('**Create**'):
                    if uname and empid and email and office_email and contact and pwd and confirm:
                        if (uname,) not in check_uname(uname):
                            if (empid,) not in check_empid(empid):
                                if valid_email(email):
                                    if pwd==confirm:
                                        enc_pwd=pickle.dumps(pwd)
                                        insert_data(empid,uname,enc_pwd,'Trainer',email,office_email,contact)
                                        insert_empid(empid)
                                        st.success(f'user creation successful👍🏻')
                                        st.balloons()
                                        st.toast('New user created',icon='✅')
                                        st.session_state.user_data=get_users()
                                        send_creds(email,uname,pwd)
                                        time.sleep(1.5)
                                        st.rerun()
                                        
                                    else:
                                        st.error("password does'nt match")
                                else:
                                    st.warning('Invalid email (only gmail will be accepted)',icon='⚠️')
                            else:
                                st.error('Empployee Id already exists')
                        else:
                            st.error('username unavailable try another one..')
                    else:
                        st.error('enter details..') 
    with tab3:
        a1,a2,a3=st.columns([1,2,1])
        b1,b2,b3=st.columns([1,5,1])
        id=a2.text_input('** **',placeholder='🔍 Search empid...').upper()
        with b2.container(border=True):
            c1,c2,c3=st.columns(3)
            c4,c5,c6=st.columns(3)
            if id and (id,) in check_empid(id):
                data=list(get_user(id))
                data.pop(2)
                data.pop(4)
                name=c1.text_input('**Username:** ',placeholder='enter name',value=data[1])
                role=c2.selectbox('**Role:** ',placeholder='enter role',options=['Trainer','Manager'])
                email=c3.text_input('**Email:** ',placeholder='enter email',value=data[3])
                official=c4.text_input('**Official Email:** ',placeholder='enter official email',value=data[4])
                contact=c5.text_input('**Contact:** ',placeholder='enter contact',value=data[5])
                if st.button('**update**'):
                    if name and role and email and official and contact:
                        update_user(id,name,role,email,official,contact)
                        st.toast('✅User details updated..')
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error('⚠️ Enter details')
            else:
                st.header('No data found')
    with tab4:
        if 'confirm_delete' not in st.session_state:
            st.session_state.confirm_delete=False
        id=st.text_input('🪪 **Employee Id**',placeholder='Enter employee Id..',key='delete_empid').upper()
        if st.button('Delete'):
            if id and get_user(id):
                st.session_state.confirm_delete=True    
            else:
                st.error('Invalid or User not present')
        if st.session_state.confirm_delete:
            st.write('Do you want to delete?')
            if st.button('**confirm**'):
                delete_user(id)
                st.session_state.user_data=get_users()
                st.session_state.confirm_delete=False
                st.toast(f'🗑️ User {id} deleted')
                time.sleep(1.5)
                st.rerun()
               

                    
    