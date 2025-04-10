import re
import streamlit as st
from db import get_db_connection
conn=get_db_connection()
cursor=conn.cursor()

def check_role(uname):
    cursor.execute('SELECT ROLE FROM USER WHERE USERNAME=?',(uname,))
    return cursor.fetchone()[0]

def insert_data(empid,uname,pwd,role,email,official_mail,contact):
    cursor.execute('INSERT INTO USER(EMPID,USERNAME,PASSWORD,ROLE,EMAIL,OFFICIAL_MAIL,CONTACT) VALUES(?,?,?,?,?,?,?)',(empid,uname,pwd,role,email,official_mail,contact))
    conn.commit()
    st.cache_data.clear()

def insert_empid(empid):
    cursor.execute('INSERT INTO TRAINERS (EMPID) VALUES (?)',(empid,))
    cursor.execute('INSERT INTO SKILLS (EMPID) VALUES (?)',(empid,))
    conn.commit()
    st.cache_data.clear()
def check_uname(uname):
    return list(cursor.execute('SELECT USERNAME FROM USER'))
def check_empid(empid):
    return list(cursor.execute('SELECT EMPID FROM USER'))
def check_pwd(user):
    cursor.execute('SELECT PASSWORD FROM USER WHERE USERNAME=?',(user,))
    return cursor.fetchone()[0]
def check_status(id):
    cursor.execute('SELECT STATUS FROM USER WHERE EMPID=?',(id,))
    return cursor.fetchone()[0]
@st.cache_data
def get_user(user):
    cursor.execute('SELECT * FROM USER WHERE EMPID=?',(user,))
    return cursor.fetchone()

def update_pwd(id,pwd):
    cursor.execute('UPDATE  USER SET PASSWORD=? WHERE EMPID=?',(pwd,id))
    conn.commit()
    st.cache_data.clear()
def update_profile(email,official,contact,id):
    cursor.execute('UPDATE USER SET EMAIL=?,OFFICIAL_MAIL=?,CONTACT=? WHERE EMPID=?',(email,official,contact,id))
    conn.commit()
    st.cache_data.clear()
def delete_user(id):
    cursor.execute('DELETE FROM TRAINERS WHERE EMPID=?',(id,))
    cursor.execute('DELETE FROM USER WHERE EMPID=?',(id,))
    cursor.execute('DELETE FROM ATTENDANCE WHERE EMPID=?',(id,))
    cursor.execute('DELETE FROM SKILLS WHERE EMPID=?',(id,))
    conn.commit()
    st.cache_data.clear()

def update_user(id,name,role,email,official,contact):
    cursor.execute(f'UPDATE USER SET USERNAME=?,ROLE=?,EMAIL=?,OFFICIAL_MAIL=?,CONTACT=? \
                   WHERE EMPID=?',(name,role,email,official,contact,id))
    conn.commit()
    st.cache_data.clear()
    
def valid_email(email):
    return bool(re.findall(r'^[a-zA-Z0-9._%+-]+@gmail\.com$',email))
def get_email(id):
    cursor.execute('SELECT EMAIL FROM USER WHERE EMPID=?',(id,))
    return cursor.fetchone()[0]

def upload_image(id,image):
    cursor.execute('UPDATE TRAINERS SET IMAGE=? WHERE ID=(SELECT ID FROM TRAINERS WHERE EMPID=? LIMIT 1)',(image,id))
    conn.commit()
    st.cache_data.clear()
@st.cache_data
def get_image(id):
    cursor.execute('SELECT IMAGE FROM TRAINERS WHERE EMPID=? AND  IMAGE IS NOT NULL',(id,))
    return cursor.fetchone()

def delete_image(id):
    cursor.execute('UPDATE TRAINERS SET IMAGE=NULL WHERE EMPID=?',(id,))
    conn.commit()
    st.cache_data.clear()

@st.cache_data
def user_data(id):
    cursor.execute('SELECT EMAIL,OFFICIAL_MAIL,CONTACT FROM USER WHERE EMPID=?',(id,))
    return cursor.fetchone()
def insert_login(id,date,time):
    cursor.execute('INSERT INTO TRAINERS (EMPID,DATE,LOGIN) VALUES(?,?,?)',(id,date,time))
    conn.commit()
    st.cache_data.clear()

def insert_logout(id,date,time):
    cursor.execute('''
    UPDATE TRAINERS 
    SET LOGOUT = ? 
    WHERE EMPID = ? AND DATE = ? 
    AND LOGIN = (SELECT MIN(LOGIN) FROM TRAINERS WHERE EMPID = ? AND DATE = ? AND LOGOUT IS NULL)
''', (time, id, date, id, date))
    conn.commit()
    st.cache_data.clear()

@st.cache_data
def get_attendance(id,date):
    l=cursor.execute('SELECT DATE,LOGIN,LOGOUT FROM TRAINERS WHERE EMPID=? and DATE=?',(id,date))
    return list(l)
def insert_attend(id,date,login,logout,hours):
    cursor.execute('INSERT INTO ATTENDANCE (EMPID,DATE,LOGIN,LOGOUT,HOURS) VALUES(?,?,?,?,?)',(id,date,login,logout,hours))
    conn.commit()
    st.cache_data.clear()

@st.cache_data
def fetch_attend(id):
    l=cursor.execute('SELECT DATE,LOGIN,LOGOUT,HOURS FROM ATTENDANCE WHERE EMPID=?',(id,))
    return list(l)

#batches
def insert_batch(id,sub,batchcode,timing):
    cursor.execute('INSERT INTO TRAINERS (EMPID,SUBJECT,BATCHCODE,TIMING) VALUES(?,?,?,?)',(id,sub,batchcode,timing))
    conn.commit()
    st.cache_data.clear()
@st.cache_data
def get_batches(id):
    l=list(cursor.execute('SELECT SUBJECT,BATCHCODE,TIMING,TOPIC FROM TRAINERS WHERE EMPID=?',(id,)))
    return l
def delete_batch(id,code):
    cursor.execute('DELETE FROM TRAINERS WHERE EMPID=? AND BATCHCODE=?',(id,code))
    conn.commit()
    st.cache_data.clear()
def check_batch():
    return list(cursor.execute('SELECT BATCHCODE FROM TRAINERS'))
def update_topic(id,code,topic):
    cursor.execute('UPDATE TRAINERS SET TOPIC=? WHERE EMPID=? AND BATCHCODE=?',(topic,id,code))
    conn.commit()
    st.cache_data.clear()

#skills
def insert_skills(empid,skill,concept,subconcept):
    cursor.execute('INSERT INTO SKILLS (EMPID,SKILL,CONCEPT,SUB_CONCEPT) VALUES(?,?,?,?)',(empid,skill,concept,subconcept))
    conn.commit()
    st.cache_data.clear()
@st.cache_data
def get_skills(id):
    l=list(cursor.execute('SELECT SKILL FROM SKILLS WHERE EMPID=?',(id,)))
    return l
@st.cache_data
def get_skills_data(id):
    l=list(cursor.execute('SELECT * FROM SKILLS WHERE EMPID=?',(id,)))
    return l
def update_skill(empid,skill,concept,subconcept,status):
    cursor.execute('UPDATE SKILLS SET CONCEPT=?,SUB_CONCEPT=?,STATUS=? WHERE EMPID=? AND SKILL=?',(concept,subconcept,status,empid,skill))
    conn.commit()
    st.cache_data.clear()
def delete_skill(id,skill):
    cursor.execute('DELETE FROM SKILLS WHERE EMPID=? AND SKILL=?',(id,skill))
    conn.commit()
    st.cache_data.clear()

#notepad
def check_emp(id):
    l=list(cursor.execute('SELECT EMPID FROM NOTEPAD'))
    return l
def upd_content(id,content):
    cursor.execute('UPDATE NOTEPAD SET CONTENT=? WHERE EMPID=?',(content,id))
    conn.commit()
    st.cache_data.clear()

def add_content(id,content):
    cursor.execute('INSERT INTO NOTEPAD (EMPID,CONTENT) VALUES(?,?)',(id,content))
    conn.commit()
    st.cache_data.clear()

@st.cache_data
def get_content(id):
    cursor.execute('SELECT CONTENT FROM NOTEPAD WHERE EMPID=?',(id,))
    return cursor.fetchone()

#manager
@st.cache_data
def trainer_data():
    cursor.execute('SELECT EMPID,USERNAME,ROLE FROM USER WHERE ROLE=="Trainer"')
    return cursor.fetchall()
def get_id(name):
    cursor.execute('SELECT EMPID FROM USER WHERE USERNAME=?',(name,))
    return cursor.fetchone()[0]
@st.cache_data
def trainer_image(id):
    cursor.execute('SELECT IMAGE FROM TRAINERS WHERE EMPID=?',(id,))
    return cursor.fetchall()


#analytics
@st.cache_data
def get_trainers():
    cursor.execute('SELECT EMPID,SUBJECT FROM TRAINERS WHERE EMPID IS NOT "TYP1185"')
    return cursor.fetchall()

#deployment
def add_deployment(id,loc,trainer):
    cursor.execute('INSERT INTO DEPLOYMENT (EMPID,USERNAME,DEPLOYED,LOCATION) VALUES(?,?,"Yes",?)',(id,trainer,loc))
    conn.commit()
    st.cache_data.clear()
def update_deploy(id,loc):
    cursor.execute('UPDATE DEPLOYMENT SET LOCATION=? WHERE EMPID=?',(id,))
    conn.commit()
    st.cache_data.clear()
def delete_deploy(id):
    cursor.execute('DELETE FROM DEPLOYMENT WHERE EMPID=?',(id,))
    conn.commit()
    st.cache_data.clear()

@st.cache_data
def get_deploy():
    cursor.execute('SELECT EMPID,USERNAME,LOCATION FROM DEPLOYMENT')
    return cursor.fetchall()
def check_deploy():
    cursor.execute('SELECT EMPID FROM DEPLOYMENT WHERE DEPLOYED="Yes"')
    return cursor.fetchall()
def get_deploy_id(trainer):
    cursor.execute('SELECT EMPID FROM DEPLOYMENT WHERE USERNAME=?',(trainer,))
    return cursor.fetchone()[0]
#Assign Tasks

@st.cache_data
def get_all_id():
    cursor.execute('SELECT EMPID FROM USER WHERE ROLE="Trainer"')
    return cursor.fetchall()
def add_task(id,target,start,end,program):
    cursor.execute('INSERT INTO  TASK (EMPID,TARGET,START,END,PROGRAMS) VALUES(?,?,?,?,?)',(id,target,start,end,program))
    conn.commit()
    st.cache_data.clear()
@st.cache_data
def get_tasks(id):
    cursor.execute('SELECT ID,TARGET,START,END,PROGRAMS,COMPLETED FROM TASK WHERE EMPID=?',(id,))
    return cursor.fetchall()
def delete_task(id):
    cursor.execute('DELETE FROM TASK WHERE ID=?',(id,))
    conn.commit()
    st.cache_data.clear()
def upd_completed(id,val):
    cursor.execute('UPDATE TASK SET COMPLETED=? WHERE ID=?',(val,id))
    conn.commit()
    st.cache_data.clear()


