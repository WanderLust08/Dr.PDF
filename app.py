import streamlit as st
from pymongo import MongoClient




def app():
    st.title('Welcome to :blue[Dr.PDF] 🩺')
    
    print(f'mongodb+srv://{st.secrets.db_username}:{st.secrets.db_pswd}@{st.secrets.cluster_name}.hmggktk.mongodb.net/?retryWrites=true&w=majority&appName=cclmpr')

    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''


    if 'signedout' not in st.session_state:
        st.session_state.signedout = False
    if 'signout' not in st.session_state:
        st.session_state.signout = False



    def t():
        st.session_state.signedout = False
        st.session_state.signout  =False
        del st.session_state["login"]


    if not st.session_state['signedout']:
        choice = st.selectbox('Login/Signup',['Login','Signup'])

        if choice == 'Login':
            email = st.text_input('Username')
            password = st.text_input('Password',type='password')


            if st.button('Login'):
                client = MongoClient(f'mongodb+srv://{st.secrets.db_username}:{st.secrets.db_pswd}@{st.secrets.cluster_name}.hmggktk.mongodb.net/?retryWrites=true&w=majority&appName=cclmpr')
                db = client.LLM
                items = db.users.find_one({ "email": email, "pass": password })
                print(items)
                if items:
                    st.write("LOGIN SUCCESS")
                    st.session_state.useremail = email
                    st.session_state.signedout = True
                    st.session_state.signout  = True
                    if "login" not in st.session_state:
                        st.session_state["login"] = email

                    st.switch_page("pages/account.py")
                else:
                    st.error("LOGIN UNSEUCCESSFULL")

        else:
            email = st.text_input('Email Address')
            password = st.text_input('Password',type = 'password')
            email = st.text_input('Enter Unique Username')
            #Note rewriting email coz we storing usernames for LOGINs
            if st.button('Create my Account'):
                client = MongoClient("mongodb+srv://samccl:yreuow1XR14ullxU@cclmpr.hmggktk.mongodb.net/?retryWrites=true&w=majority&appName=cclmpr")
                db = client.LLM
                resp = db.users.insert_one({'email':email,'pass':password})
                if resp:
                    st.success('Account created succesfully')
                    st.markdown('Please Login using email n Password')
                    st.balloons()

    if st.session_state.signout:
        st.text('NAME'+st.session_state.useremail)
        st.button('SIGNOUT',on_click=t)


app()