import streamlit as st
import time
import pandas as pd
from io import BytesIO
import base64
import plotly.express as px
from PIL import Image
from trainer import home_greet,attendance_page,profile,notepad_page,batches_page,skills_page,display_attend
from auth import trainer_data,insert_skills,get_skills,get_id,delete_skill,get_image,user_data,add_deployment,\
    delete_deploy,get_deploy,check_deploy,get_trainers,get_all_id,add_task,get_tasks,delete_task,get_deploy_id
from streamlit_option_menu import option_menu
from db import get_db_connection
conn=get_db_connection()
cursor=conn.cursor()
def view_trainer_profile(trainer,id):
    col1,col2,col3=st.columns([1,3,1])
    #info
    with col2:
        with st.container(border=True,height=350):
            col1,col2,col3=st.columns([2,0.5,3])
            image=binary_to_image(id)
            col1.write(' ')
            col1.write(' ')
            col1.write(' ')
            col1.image(image,width=290)    
            data=user_data(id)  
            col3.markdown(f''' 
                <br>
                <br>
                   
                **Emp Name:** &nbsp;&nbsp;&nbsp;&nbsp;{trainer}\n
                
                **Emp Id:** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{id} \n
                **Email:** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{data[0]}\n
                **Official Mail:** &nbsp;&nbsp;&nbsp;{data[1]}\n
                **Contact:** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{data[2]}\n
                ''',unsafe_allow_html=True)
    

def trainer_profiles():
    data=trainer_data()
    head1,head2,head3,head4=st.columns([1,0.9,1,2])
    head2.write('##### Empid')
    head3.write('##### Trainer Name')
    head4.write('##### Role')
    with st.container(border=True,height=500):
        # st.write('  ')
        for i in data:
            st.subheader(' ')
            c1,c2,c3,c4,c5=st.columns(5)
            image=get_image(i[0])
            if image is not None:
                c1.image(image,width=90)
            else:
                c1.image('profile_pic.png',width=90)
            c2.write(i[0])
            c3.write(i[1])
            c4.write(i[2])
            st.markdown('---')

def add_skill():
        data=[i[1] for i in trainer_data()]
        col1,col2,col3=st.columns([1,2,1])
        with col2:
            trainer=st.selectbox('Trainer: ',options=data)
            id=get_id(trainer)
            con=st.container(border=True)
            con.subheader('Add➕New Skill')
            skill=con.selectbox('**Skills:**',options=['Python','Data Analysis','Data Science','Dsa','Gen AI','PowerBI','Django'],key='skill')
            concept=con.text_input('**Concept:**',placeholder='enter topic..',value='NA',key='concept').capitalize()
            sub_concept=con.text_input('**Sub Concept:**',placeholder='enter sub-topic..',value='NA',key='sub-concept').capitalize()
            if con.button('Add'):
                if skill and concept and sub_concept:
                    if (skill,) not in get_skills(id):
                        insert_skills(id,skill,concept,sub_concept)
                        st.toast(f'✅ New skill {skill} added to {trainer}')
                    else:
                        st.error(f'Skill {skill} already added')
                else:
                    st.error('Enter details..')
def remove_skill():
    data=[i[1] for i in trainer_data()]
    col1,col2,col3=st.columns([1,2,1])
    with col2:
        trainer=st.selectbox('Trainer: ',options=data)
        id=get_id(trainer)
        with st.container(border=True):
            st.subheader('Remove Skill 🗑️')
            skills= [i[0] for i in get_skills(id) if i!=(None,)]
            if skills:
                skill=st.selectbox('select skill',options=skills)
                if st.button('confirm'):
                    delete_skill(id,skill)
                    st.toast(f'🗑️ Skill {skill} deleted for {trainer}')
                    time.sleep(1)
                    st.rerun()
                    
            else:
                st.header('No skill found')

def pil_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()

# Function to convert binary data to Base64 Image
def binary_to_image(id):
    image_data = get_image(id)  # Fetch binary image data from the database
    if image_data:
        img = Image.open(BytesIO(image_data[0]))  # Convert to PIL Image
    else:
        img = Image.open('profile_pic.png')  # Default profile image
    return pil_to_base64(img)  # Convert to Base64
def deployment():
    choice=st.segmented_control(' ',['Deployed Trainers','Add Deployment','Delete Deployment'],default='Deployed Trainers')
    
    col1,col2,col3=st.columns([1,2,1])
    if choice=='Deployed Trainers':
        data=get_deploy()        
        df=pd.DataFrame(data,columns=['Empid','Name','Location'])
        df.index=df.index+1
        if data:
            df['Profile_pic']=[binary_to_image(id) for id in df['Empid']]
            df=df[df.columns[[3,0,1,2]]]
            st.dataframe(df,column_config={'Profile_pic':st.column_config.ImageColumn('Profile')},width=1000)
        else:
            st.subheader('No data')
    elif choice=='Add Deployment':
        #Add deployment
        with col2:
            with st.container(border=True):
                st.subheader('➕ Add Deployment')
                data=[i[1] for i in trainer_data()]
                trainer=st.selectbox('Select Trainer:',options=data)
                id=get_id(trainer)
                loc=st.text_input('**Location**',placeholder='Enter deployment location...')
                if st.button('Deploy'):
                    if trainer and id and loc:
                        if (id,) not in check_deploy():
                            add_deployment(id,loc,trainer)
                            with st.spinner('Submitting...'):
                                time.sleep(1)
                                st.toast(f'✅ Trainer {trainer} deployed')
                        else:
                            st.error(f'{trainer} Already deployed')
                    else:
                        st.error('Enter data')
    elif choice=='Delete Deployment':
        with col2:
            with st.container(border=True):
                st.subheader('🗑️ Delete Deployed Trainer')
                trainers=[i[1] for i in get_deploy()]
                if trainers:
                    trainer=st.selectbox('Select Trainer:',options=trainers)
                    id=get_deploy_id(trainer)
                    if st.button('Delete'):
                        if id:
                            delete_deploy(id)
                            st.toast('🗑️ Deleted')
                else:
                    st.subheader('No data')

def analytics():
    data=get_trainers()  
    df=pd.DataFrame(data,columns=['empid','subject']) 
    total_trainers=len(df['empid'].unique())
    subjects=df.groupby('subject')['subject'].count()
    emp_group=df.groupby('empid')['subject'].count()
    emp_group=emp_group[emp_group>0]
    subjects=pd.DataFrame(subjects).rename(columns={'subject':'count'}).reset_index()
    cursor.execute('SELECT COUNT(*) FROM DEPLOYMENT WHERE DEPLOYED="Yes"')
    deployed_count=cursor.fetchone()[0]
    c1,c2,c3,c4=st.columns(4)
    with c1.container(border=True):
        a1,a2=st.columns(2)
        a1.image('icons/total_trainers.png',width=80)
        a2.metric('**Total Trainers**',value=total_trainers)
    with c2.container(border=True):
        count=sum(1 for i in df['empid'].unique() if i not in emp_group)
        a1,a2=st.columns(2)
        a1.image('icons/under_training.png',width=80)
        a2.metric(f'**Under Training**',value=count)
    with c3.container(border=True):
        a1,a2=st.columns(2)
        a1.image('icons/taking_batches.png',width=80)
        a2.metric(f'**Taking Batches**',value=len(emp_group))
    with c4.container(border=True):
        a1,a2=st.columns(2)
        a1.image('icons/deployment.png',width=80)
        a2.metric(f'**Deployed**',value=deployed_count)
    # st.markdown('''<h5 style="text-align:center">Total Batches</h5> ''',unsafe_allow_html=True)
    
    b1,b2=st.columns(2)
    with b1:
        fig = px.bar(subjects, y='subject', x='count',text='count')
        fig.update_layout(title_text='Batches Count',xaxis_tickangle=0)  # Rotate xticks
        fig.update_traces(textposition='inside') 
        fig.update_yaxes(tickmode="linear", dtick=1)
        st.plotly_chart(fig)
@st.dialog('Targets',width='large')
def trainer_tasks(trainer):
    id=get_id(trainer)
    tasks=get_tasks(id)
    st.info('you can select rows in the 1st column to delete')
    if tasks:
        df=pd.DataFrame(tasks,columns=['id','target','start','end','programs','completed'])
        edited=st.data_editor(df,width=700,num_rows='dynamic')
        deleted_rows=df[~df['id'].isin(edited['id'])]
        if not deleted_rows.empty:
            for id in deleted_rows['id']:
                delete_task(id)
            st.success('🗑️ Target Deleted')
            time.sleep(1)
            st.rerun()
    else:
        st.subheader('No data')
def monitor_target(id,completed):
    df=pd.read_sql('SELECT * FROM TASK',conn)
    if completed!='All':
        data=df[(df['EMPID']==id)&(df['COMPLETED']==completed)]
    else:
        data=df[(df['EMPID']==id)]
    
    data.index=data.reset_index().index+1
    st.dataframe(data,width=1200,height=300)

def assign_targets():
    choice=st.segmented_control('',['Monitor Target','Assign Target','Delete Target'],default='Monitor Target')
    c1,c2,c3=st.columns([1,2,1])
    if choice=='Assign Target':
        with c2.container(border=True):
            st.subheader('🎯 Assign Target')
            data=[i[1] for i in trainer_data()]
            trainer=st.multiselect('**Select Trainer**',options=['All',*data])
            target=st.text_input('**Target concepts**',placeholder='Eg: Functions to recursion').capitalize()
            program=st.text_area('**Programs**',placeholder='Enter program..',value='NA')
            c1,c2=st.columns(2)
            start=c1.date_input('**Start date**')
            end=c2.date_input('**End date**')
            if trainer and trainer[0]=='All':
                all_id=get_all_id()
                if st.button('Add Target'):
                    if target and start and end:
                        for id in all_id:
                            add_task(id[0],target,start,end,program)
                        st.toast(f'✅ Target added to {trainer[0]}')
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error('Enter details')
            else:
                if len(trainer)==1:
                    id=get_id(trainer[0])
                    if st.button('Add Target'):
                        if id and target and start and end:
                                add_task(id,target,start,end,program)
                                st.toast(f'✅ Target added to {trainer[0]}')
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error('Enter details')
                else:
                    col_id=[get_id(i) for i in trainer]
                    if st.button('Add Target',key='specific_trainers'):
                        if col_id and target and start and end:
                                for id in col_id:
                                    add_task(id,target,start,end,program)
                                st.toast(f'✅ Target added to {trainer}')
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error('Enter details')
    elif choice=='Delete Target':
        with c2.container(border=True):
            st.subheader('🗑️ Delete Target')
            data=[i[1] for i in trainer_data()]
            trainer=st.selectbox('**Select Trainer**',options=data)
            if trainer:
                if st.button('Get Targets'):
                    trainer_tasks(trainer)
    elif choice=='Monitor Target':
        st.subheader('Targets')
        data=[i[1] for i in trainer_data()]
        c1,c2=st.columns(2)
        trainer=c1.selectbox('**Select Trainer**',options=data)
        completed=c2.selectbox('**Completed**',options=['All','True','False'])
        if trainer:
            id=get_id(trainer)
        monitor_target(id,completed)              
            
#main function
def manager_interface(id,user,role):
    with st.sidebar:
        selected=option_menu('Menu',['Home','Profile','Trainers','Assign Target','Assign Skills','Deployment','Attendance','Notepad'],icons=['house','person','people','clipboard-check','code-slash','airplane','journal-check','pencil-square'])
    if selected=='Home':
        home_greet(id,user)
        analytics()
    elif selected=='Profile':
        profile(id,user,role)
    elif selected=='Trainers':
        a1,a2,a3=st.columns([1,1,1])
        data=[i[1] for i in trainer_data()]
        trainer=a3.selectbox('Select Trainer',options=data)
        id=get_id(trainer)
        choice=a1.segmented_control('',['Profile','Classes','Skills','Attendance'],default='Profile')
        st.markdown(f'''<h3 style="text-align:center;color:#FF4B4B">{trainer}</h3>''',unsafe_allow_html=True)
        if choice=='Profile':
            view_trainer_profile(trainer,id)
        elif choice=='Classes':
            filter=a2.selectbox('**Subject**',options=['All','Python','Dsa','Data analysis','Powerbi','Django','Data science','Gen AI'])
            batches_page(id,filter)
        elif choice=='Skills':
            skills_page(id)
        elif choice=='Attendance':
            df=pd.read_sql(f'SELECT DATE,LOGIN,LOGOUT,HOURS FROM ATTENDANCE WHERE EMPID="{id}"',conn)
            data=df.groupby('DATE').tail(1).reset_index(drop=True)
            data.index=data.index+1
            c1,c2=st.columns([0.4,2])
            def highlight_cells(val):
                hours=9
                color = 'red' if int(val[:2])<hours else 'transparent'
                return f'background-color: {color}'
            styled_df = data.style.applymap(highlight_cells,subset=['HOURS'])
            c2.dataframe(styled_df,width=700,height=300)
    elif selected=='Assign Target':
        assign_targets()
    elif selected=='Assign Skills':
        choice=st.segmented_control(' ',['Add skill','Delete skill'],default='Add skill')
        if choice=='Add skill':
            add_skill()
        elif choice=='Delete skill':
            remove_skill()
    elif selected=='Deployment':
        deployment()
    elif selected=='Attendance':
        attendance_page(id)
    elif selected=='Notepad':
        notepad_page(id)
        
            