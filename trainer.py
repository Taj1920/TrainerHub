import streamlit as st
import pandas as pd
import time
from auth import *
from datetime import datetime
from PIL import Image
from io import BytesIO
from streamlit_option_menu import option_menu
from streamlit_cropper import st_cropper
from streamlit_extras.stylable_container import stylable_container
from db import get_db_connection
conn=get_db_connection()
cursor=conn.cursor()


def binary_to_image(id):
    image_data=get_image(id)
    if image_data:
        return Image.open(BytesIO(image_data[0]))
    else:
        return Image.open('profile_pic.png')
    


def upd_profile(id):
    if (id,) in check_empid(id):
        data=list(get_user(id))
        data.pop(2)
        data.pop(4)
        name=st.text_input('**Username:** ',value=data[1],disabled=True)
        role=st.text_input('**Role:** ',value=data[2],disabled=True)
        email=st.text_input('**Email:** ',placeholder='enter email',value=data[3])
        official=st.text_input('**Official Email:** ',placeholder='enter official email',value=data[4])
        contact=st.text_input('**Contact:** ',placeholder='enter contact',value=data[5])
        if st.button('**update**',type='primary'):
            if email and official and contact:
                update_profile(email,official,contact,id)
                st.toast('✅Profile updated..')
                time.sleep(0.5)
                st.rerun()
            else:
                st.error('⚠️ Enter details')
    else:
        st.header('No data found')



def upload_img(id):
    img=st.file_uploader('upload image',type=['png','jpg','jpeg'])
    if img!=None:
        progress_bar=st.progress(0)
        for i in range(1,101):
            time.sleep(0.1)
            progress_bar.progress(i,text=f'uploaded  {i}%')
        img=st_cropper(Image.open(img),box_color='blue',aspect_ratio=(1,1))
        if st.button('ok',key='crop_image'):
            img_byte=BytesIO()
            img.save(img_byte,format='PNG')
            bin_img=img_byte.getvalue()
            upload_image(id,bin_img)
            st.toast('Image uploaded✅')
@st.dialog('🗑️')     
def del_dialog(id):
    st.write('Do you want to Delete?')
    if st.button('confirm'):
        delete_image(id)
        st.success('Image removed ✅')

def profile(id,user,role):
    st.markdown('''<h3 style="text-align:center;color:#FF4B4B;">Profile</h2>
        ''',unsafe_allow_html=True)
    col1,col2,col3=st.columns([1,5,1])
    with col2:
        with stylable_container(key='profile_container',
                                css_styles='''
                                {
                                background-color: #262730;
                                border-radius:8px;
                                padding: 25px;
                                box-shadow: 0px 3px 4px #95a5a6;
                                }
                                
                                '''):
            col1,col2=st.columns([1,1])
            image=binary_to_image(id)
            
            col1.image(image,width=250)
            action=col1.pills('-',['Edit Image','Remove Image'],key=user,label_visibility='hidden')
            if action=='Edit Image':
                with st.popover('upload Image',use_container_width=True):
                    upload_img(id)
    
            elif action=='Remove Image':
                del_dialog(id)
            data=user_data(id) 
            
            col2.markdown(f'''
                <br>
                                
                **Emp Name:** &nbsp;&nbsp;&nbsp;&nbsp;{user}\n
                
                **Emp Id:** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{id} \n
                **Email:** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{data[0]}\n
                **Official Mail:** &nbsp;&nbsp;&nbsp;{data[1]}\n
                **Contact:** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{data[2]}\n
                **Role:** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{role}
                ''',unsafe_allow_html=True)
            with col2.popover('Edit 🖋️',help='Edit profile'):
                upd_profile(id)
    

@st.dialog('Today Entry/Exit')
def mark_entry(id,status):
    date=datetime.today().strftime('%d-%m-%Y')
    day=datetime.today().strftime('%A')
    time=datetime.now().strftime('%H:%M:%S')
    if status=='Mark Entry':
        insert_login(id,date,time)
        st.markdown(f'**Date:** &nbsp;&nbsp;&nbsp;{date}')
        st.markdown(f'''**Day:** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{day}''')
        st.markdown(f'''**Logged in at:** &nbsp;&nbsp;&nbsp;{time}''')
    elif status=='Mark Exit':
        insert_logout(id,date,time)
        st.markdown(f'**Date:** &nbsp;&nbsp;&nbsp;{date}')
        st.markdown(f'''**Day:** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{day}''')
        st.markdown(f'''**Logged out at:** &nbsp;&nbsp;&nbsp;{time}''') 
 

def greet(user):
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        greeting = "Good Morning"
    elif 12 <= current_hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    st.markdown(f'<h3>{greeting}, <span style="color:#FF4B4B;">{user}👋</span>',unsafe_allow_html=True)

def display_attend(login_data): 
    df=pd.DataFrame(login_data,columns=['Date','Login','Logout','Worked_hours'])
    dates=df.groupby('Date').tail(1).reset_index(drop=True)
    dates.index=dates.index+1
    return st.dataframe(dates,width=700,height=400),dates
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='XlsxWriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data
@st.dialog('Delete batch')
def remove_batch(id,batchcode):
    st.write('Do you want to delete?')
    if st.button('confirm',key=f'confirm{batchcode}',type='primary'):
        delete_batch(id,batchcode)
        st.success('🗑️Batch deleted')
        time.sleep(1)
        st.rerun()
@st.dialog('Update Topic')
def upd_topic(id,code):
    topic=st.text_input('**Topic**',placeholder='Enter topic name..').capitalize()
    if st.button('update',type='primary'):
        if topic:
            update_topic(id,code,topic)
            st.success('✅ Topic updated..')
            time.sleep(1)
            st.rerun()
def celebrate(skill):
    st.title(' ')
    st.balloons()
    st.toast(f'Congratulations!🎉🎉 for completing {skill}')
@st.dialog('update skill  🔄')
def upd_skill(id,data):
    with st.container(border=True):
        skill=st.text_input('**Skill**',value=data[0],disabled=True)
        concept=st.text_input('**Concept**',value=data[1],placeholder='enter concept..').capitalize()
        sub_concept=st.text_input('**Sub-concept**',value=data[2],placeholder='enter sub-concept..').capitalize()
        status=st.selectbox('**Status**',options=['on going','completed'])
        if status=='completed':
            st.warning('⚠️ change to "completed" only when full course is completed')
        if st.button('update',key=f'{id}',type='primary'):
            if concept and sub_concept and status:
                with st.spinner('updating..'):
                    update_skill(id,skill,concept,sub_concept,status)
                    time.sleep(2)
                    st.success('✅ Skill updated')
                    if status=='completed':
                        celebrate(skill)
                    time.sleep(3)
                    st.rerun()
            else:
                st.warning('⚠️ Enter data..')
def home_greet(id,user):
            st.markdown("""
    <style>
        .block-container {
            padding-top: 2 !important;
            margin-top: -100px;
        }
    </style>
""", unsafe_allow_html=True)
            with stylable_container(key='colored_greet',css_styles='''
                                    {
                                    background-color:#262730;
                                    border:1px solid black;
                                    border-radius:7px;
                                    box-shadow: 0px 3px 4px #95a5a6;
                                    padding: 9px;
                                    }
                                    
                                    '''):
                col1,col2=st.columns([10,2])
                with col1:
                    greet(user) 
                with col2:
                    if 'entry' not in st.session_state:
                        st.session_state.entry=False
                    if 'exit' not in st.session_state:
                        st.session_state.exit=False
                    if st.session_state.entry:
                        if st.button('**Mark Exit**',type='primary'):
                            st.session_state.entry=False
                            st.session_state.exit=True
                            mark_entry(id,'Mark Exit')
                            time.sleep(3)
                            st.rerun()    
                    elif st.button('**Mark Entry**',type='primary'):
                        mark_entry(id,'Mark Entry')
                        st.session_state.entry=True
                        st.session_state.exit=False
                        time.sleep(3)
                        st.rerun()
def attendance_page(id):
    st.toast('Mark Entry or Exit if data is not visible')
    date=datetime.today().strftime('%d-%m-%Y')
    attendance=get_attendance(id,date)
    if attendance:
        if 'exit' not in st.session_state:
            st.session_state.exit=False
        attend=pd.DataFrame(attendance,columns=['date','login','logout'])
        attend['login']=pd.to_timedelta(attend['login'])
        attend['logout']=pd.to_timedelta(attend['logout'])
        min=attend['login'].min()
        max=attend['logout'].max()
        time_diff=max-min
        if pd.notna(min) and pd.notna(max):
            login=str(min).split()[2]
            logout=str(max).split()[2]
            insert_attend(id,date,login,logout,str(time_diff).split()[2])
        if st.session_state.exit:
            st.markdown(f'''#### Today's worked Hours -    &nbsp;&nbsp; {str(time_diff).split()[2]}
                        ''')
        login_data=fetch_attend(id)
        out_df,data=display_attend(login_data)
        col1,col2=st.columns([2,1])
        out_df
        excel_data = to_excel(data)
        st.download_button(label="Download Attendance", 
            data=excel_data, 
            file_name="data.xlsx", 
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",type='primary')        
    else:
        st.header('No data found')
def notepad_page(id):
    st.toast("Ideas fade, but written words last forever. 📝 Start noting your brilliance today! 🚀")
    st.markdown('''<h2 style="text-align:center;color:#FF4B4B;">Notepad</h2>''',unsafe_allow_html=True)
    st.write('---')
    if (id,) in check_emp(id):
        data=get_content(id)[0]
    else:
        add_content(id,'No Data')
    if data!=None:
        content=st.text_area('**Your Content:**',value=data,placeholder='Go on Type something...',height=300)
    else:    
        content=st.text_area('**Your Content:**',placeholder='Go on Type something...',height=300)
    if st.button('**Save changes ✔️**',type='primary'):
        if content:
            if (id,) in check_emp(id):
                upd_content(id,content)
                st.toast('✅ Content Saved')
            else:
                add_content(id,content)
                st.toast('✅ Content Added')
def batches_page(id,filter):
    all_data = [i for i in get_batches(id) if None not in i]
    # Filter data first
    cls_data = [i for i in all_data if filter == 'All' or i[0] == filter]
    cols_per_row=3
    with st.container(height=430,border=True):
        with st.spinner('Loading...'):
            time.sleep(1)
        for i in range(0,len(cls_data),cols_per_row):
            row_data = cls_data[i:i + cols_per_row]
            cols=st.columns(cols_per_row)
            for j in range(cols_per_row):
                with cols[j]:
                    if j<len(row_data):
                        data=row_data[j]
                        
                        with stylable_container(key=f'stylable_classes_{data[1]}',
                                                css_styles='''
                                                {
                                                background-color: #262730;
                                                border-radius:8px;
                                                
                                                box-shadow: 0px 3px 4px #95a5a6;
                                                padding:10px;
                                                }
                                                '''):
                            st.write(f'**Subject**   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; :&nbsp;&nbsp;{data[0]}')
                            st.write(f'**Batch Code** &nbsp;&nbsp;  :&nbsp;&nbsp;  {data[1]}')
                            st.write(f'**Timing** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; :&nbsp;&nbsp;{data[2]}')
                            st.write(f'**Topic** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; :&nbsp;&nbsp;{data[3]}')
                            b1,b2=st.columns(2)
                            if b1.button('Delete',key=f'del {data[1]}',type='primary'):
                                remove_batch(id,data[1])
                            if b2.button('Update topic',key=f'upd {data[1]}',type='primary'):
                                upd_topic(id,data[1])
                    else:
                        st.empty()

def skills_page(id):
    skill_data=[i for i in get_skills_data(id) if None not in i]
    cols_per_row=3
    with st.container(height=430,border=True):
        with st.spinner('Loading...'):
            time.sleep(1)
        if skill_data:
            for i in range(0,len(skill_data),cols_per_row):
                columns=st.columns(3)
                for j,col in enumerate(columns):
                    if i+j<len(skill_data):
                        data=skill_data[i+j][2:]
                        with col:
                            with stylable_container(key=f'skill_{data[0]}',
                                                    css_styles='''
                                                    {
                                                    background-color: #262730;
                                                    border-radius:8px;
                                                    
                                                    box-shadow: 0px 3px 4px #95a5a6;
                                                    padding:10px;
                                                    }
                                                    '''):
                                st.markdown(f'''
                                **Skill** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; :&nbsp;&nbsp; **{data[0]}**\n
                                **Concept** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; :&nbsp;&nbsp;{data[1]}\n
                                **Sub-Concept** &nbsp; :&nbsp;&nbsp;{data[2]}\n
                                **Status** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; :&nbsp;&nbsp;{data[3]}
                                ''')
                                st.button('Update  🔄',key=f'sub{data[0]}',on_click=upd_skill,args=[id,data],type='primary')
        else:                   
            st.header('No data found')

def trainer_interface(id,user,role):    
    st.markdown("""
    <style>
        .block-container {
            padding-top: 1 !important;
            margin-top: -100px;
        }
    </style>
    
""", unsafe_allow_html=True)
    with st.sidebar:
        selected=option_menu('Menu',['Home','Profile','Classes','Skills','Attendance','Notepad'],icons=['house','person','book','code-slash','calendar-check','pencil-square'])
    if selected=='Home':
        with st.container():
            home_greet(id,user)
            choice=st.segmented_control(' ',['Analytics','Tasks'],default='Analytics') 
            if choice=='Analytics':
                batch=[i for i in get_batches(id) if None not in i]
                skill_data=[i for i in get_skills_data(id) if None not in i]
                tasks=get_tasks(id)
                if batch and skill_data:   
                    df=pd.DataFrame(batch,columns=['subject','code','timing','topic'])
                    df1=pd.DataFrame(skill_data,columns=['id','empid','skill','concept','subconcept','status'])
                    df2=pd.DataFrame(tasks,columns=['Unique_id','Target','Start','End','Programs','Completed']) 

                    a1,a2,a3,a4,a5=st.columns(5)
                    b1,b2=st.columns(2)
                    with b1:
                        count=pd.DataFrame(df.groupby('subject')['code'].count()).reset_index().rename(columns={'code':'count'})
                        st.markdown('''<h5 style="text-align:center;">Class count</h5>''',unsafe_allow_html=True)
                        st.bar_chart(count,x='subject',y='count',height=250)
                            
                    total_batches=df['code'].count()
                    ongoing=df1['status'][df1['status']=='on going'].count()
                    completed=df1['status'][df1['status']=='completed'].count()
                    pending_tasks=df2['Completed'][df2['Completed']=='False'].count()
                    completed_tasks=df2['Completed'][df2['Completed']=='True'].count()
                    with a1.container(height=104,border=True):
                        c1,c2=st.columns([1.5,3])
                        with c1:
                            st.image('icons/presentation.png')
                        with c2:
                            st.metric('**Total Batches**',value=total_batches)
                    
                    with a2.container(height=104,border=True):
                        c1,c2=st.columns([1.5,3])
                        with c1:
                            st.image('icons/on-going.png')
                        with c2:
                            st.metric('**Skills- on going**',value=ongoing)
                    with a3.container(height=104,border=True):
                        c1,c2=st.columns([1.5,3])
                        with c1:
                            st.image('icons/completed.png')
                        with c2:
                            st.metric('**Skills- completed**',value=completed)
                    with a4.container(height=104,border=True):
                        c1,c2=st.columns([1.7,3])
                        with c1:
                            st.image('icons/pending-tasks.png')
                        with c2:
                            st.metric('**Tasks Pending**',value=pending_tasks)
                    with a5.container(height=104,border=True):
                        c1,c2=st.columns([1.5,3])
                        with c1:
                            st.image('icons/completed-task.png')
                        with c2:
                            st.metric('**Tasks completed**',value=completed_tasks)
                else:
                    c1,c2,c3=st.columns([3,4,1])
                    c2.title(' ')
                    c2.subheader('No data Found 😞')
                    c2.subheader('Add Classes and skills ...')

            elif choice=='Tasks':
                tasks=get_tasks(id)
                df=pd.DataFrame(tasks,columns=['Unique_id','Target','Start','End','Programs','Completed'])
                df.index=df.index+1
                edited=st.data_editor(df,width=1000,height=300,column_config={'Completed':st.column_config.CheckboxColumn('Completed')})
                
                if st.button('**update**',type='primary'):
                    st.toast('♻️ updating...')
                    id_true=edited['Unique_id'][edited['Completed']=='True']
                    id_false=edited['Unique_id'][edited['Completed']=='False']
                    time.sleep(2)
                    if not id_true.empty :
                        for i in id_true:
                            upd_completed(i,"True")
                    if not id_false.empty:
                        for i in id_false:
                            upd_completed(i,"False")
                        st.toast('✅ updated..')
            
    elif selected=='Profile':
        profile(id,user,role)
    elif selected=='Attendance':
        attendance_page(id)
    elif selected=='Classes':
        c1,c2,c3=st.columns([5,4,2])
        select=c1.segmented_control(' ',['Your Batches','Add New Batch'],default='Your Batches')
        #add batch
        if select=='Add New Batch':
            st.toast('Please enter the Batch timing in the specified format')
            c1,c2,c3=st.columns([1,2,1])
            with c2:
                with st.container(border=True):
                    subject=st.selectbox('**Subject**',options=['Python','Dsa','Data analysis','Powerbi','Django','Data science','Gen AI'])
                    batchcode=st.text_input('**Batch code**',placeholder='enter batch code..').upper()
                    timing=st.text_input('**Batch Timing**',placeholder='Eg: 7:00 AM/PM to 9:00 AM/PM').upper()
                    if st.button('Add ➕',type='primary'):
                        if subject and batchcode and timing:
                            if (batchcode,) not in check_batch():
                                insert_batch(id,subject,batchcode,timing)
                                st.toast('✅ New Batch Added')
                            else:
                                st.warning('Batch already exists')
                        else:
                            st.error('Enter details..')
        elif select=='Your Batches':
            filter=c3.selectbox('**Filter**',options=['All','Python','Dsa','Data analysis','Powerbi','Django','Data science','Gen AI'])
            batches_page(id,filter)
    elif selected=='Skills':
        st.write('  ')
        st.subheader('Your skills ⬆️')
        skills_page(id)
    elif selected=='Notepad':
        notepad_page(id)
    
    

