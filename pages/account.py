import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import json
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai

from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
# from dotenv import load_dotenv

import re
import datetime
from io import BytesIO

from pymongo import MongoClient
from fpdf import FPDF

client = MongoClient(f'mongodb+srv://{st.secrets.db_username}:{st.secrets.db_pswd}@{st.secrets.cluster_name}.hmggktk.mongodb.net/?retryWrites=true&w=majority&appName=cclmpr')





import time

# load_dotenv()

genai.configure(api_key=os.getenv(st.secrets.GOOGLE_API_KEY))

# def generate_pdf():
#     """Generate an example pdf file and save it to example.pdf"""
    

#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)
#     pdf.cell(200, 10, txt="Welcome to Streamlit!", ln=1, align="C")
#     pdf.output("example.pdf")


def generate_pdf(myresp,ques):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('ariblk','','C:\Windows\Fonts\\ariblk.ttf', uni=True)
    pdf.set_font('ariblk', size=12)
                # mytxt = json_data['reply']
                # pdf.multi_cell(200, 10, myresp, align="L")
    x = datetime.datetime.now()
    ques = ques+x.strftime("%x")
    newques = re.sub(r'[^a-zA-Z0-9_]', ' ', ques)
    pdf.write(10, myresp)

    # folder_path = "\\uploads"
    # os.makedirs(folder_path, exist_ok=True)


    # pdf_file_path = os.path.join(folder_path,f"{newques}.pdf")
    return pdf.output(dest='S').encode('latin1')
    # return newques

    # buffer = BytesIO()
    # pdf.output(buffer)
    
    # # Get the content of the buffer as bytes
    # pdf_bytes = buffer.getvalue()
    # return pdf_bytes







def get_pdf_text(pdf_docs):
    text=""
    for pdf in pdf_docs:
        pdf_reader=PdfReader(pdf)
        for page in pdf_reader.pages:
            text+=page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000,chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store= FAISS.from_texts(text_chunks,embedding= embeddings)
    vector_store.save_local("faiss_index")

def get_conversational_chain():

    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
    provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro",temperature=0.3)

    prompt = PromptTemplate(template = prompt_template, input_variables = ["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain



@st.cache_resource
def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    
    new_db = FAISS.load_local("faiss_index", embeddings)
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()

    
    response = chain(
        {"input_documents":docs, "question": user_question}
        , return_only_outputs=True)

    #client = MongoClient("mongodb+srv://samccl:yreuow1XR14ullxU@cclmpr.hmggktk.mongodb.net/?retryWrites=true&w=majority&appName=cclmpr")
    db = client.LLM
    db.posts.insert_one({'user':st.session_state["login"],'ques':user_question,'reply':response['output_text']})
    st.write("Reply: ", response["output_text"])



def add_container(count):
    db2 = client.LLM
    myquery = { "user": st.session_state["login"] }
    items = db2.posts.find(myquery,{'_id':0,'user':0})
    # if "replies" not in st.session_state:
    #     st.session_state["replies"] = items
    # for x in items:
    #     print(x)

  
    # st.write("Reply: ", response["output_text"])
    # newitems = st.session_state["replies"]
    for x in items:
        print(x)
        json_data = json.dumps(x, ensure_ascii=True)
        print(json_data)
        
        mytxt=json.loads(json_data)
        myresp = mytxt['reply']
        print("HELLO"+myresp)
        with st.container():
            st.title(x['ques'])
            st.markdown(x['reply'])
            
            count+=1
            print(count)
            if st.button("Generate PDF",key=count):
                newques = generate_pdf(myresp,x['ques'])



                st.success("Generated example.pdf!")
                xa = datetime.datetime.now()
                ques = x['ques']+xa.strftime("%x")
                newquess = re.sub(r'[^a-zA-Z0-9_]', ' ', ques)
                # with open(f'C:\\Users\\Samarth Shetty\\Desktop\\TSEC SEM VI\\MPR\\uploads\\{newques}.pdf',"rb") as f:
                #     st.download_button("Download pdf", f, f'{newques}.pdf')
                st.download_button(label='Download PDF', data=newques, file_name=f'{newquess}.pdf')







    # add_container(response,count)
    
    # db2 = client.LLM
    # myquery = { "user": st.session_state["login"] }
    # items = db2.posts.find(myquery,{'_id':0,'user':0})
    # # if "replies" not in st.session_state:
    # #     st.session_state["replies"] = items
    # # for x in items:
    # #     print(x)

    # st.write("Reply: ", response["output_text"])
    # # newitems = st.session_state["replies"]
    # for x in items:
    #     print(x)
    #     json_data = json.dumps(x, ensure_ascii=True)
    #     print(json_data)
        
    #     mytxt=json.loads(json_data)
    #     myresp = mytxt['reply']
    #     print("HELLO"+myresp)
    #     with st.container():
    #         st.title(x['ques'])
    #         st.markdown(x['reply'])

    #         count+=1
    #         print(count)
    #         if st.button("Generate PDF",key=count):
    #             newques = generate_pdf(myresp,x['ques'])
    #             st.success("Generated example.pdf!")

    #             with open(f'C:\\Users\\Samarth Shetty\\Desktop\\TSEC SEM VI\\MPR\\uploads\\{newques}.pdf',"rb") as f:
    #                 st.download_button("Download pdf", f, f'{newques}.pdf')


 




def are_pdfs_uploaded(uploaded_files):
    """
    Check if PDFs are uploaded.
    """
    return len(uploaded_files) > 0




def main():
    # st.set_page_config(page_title="Dr. PDF")
    count = 0
    st.header("Chat with Dr.PDF 🩺")

    user_question = st.text_input("Ask a Question from the PDF Files")

    if user_question:
        user_input(user_question)
        
    add_container(count)





    with st.sidebar:
        st.title("📜 Your Documents")
        pdf_docs = st.file_uploader("📤 Upload your PDF Files and Click on the Submit Button", accept_multiple_files=True)
        if st.button("✅ Submit"):
            if not are_pdfs_uploaded(pdf_docs):
                error_placeholder = st.empty()
                error_placeholder.error("Please upload at least one PDF file.")
                time.sleep(3)
                error_placeholder.empty()
            else:
                with st.spinner("✍ Processing..."):
                    raw_text = get_pdf_text(pdf_docs)
                    text_chunks = get_text_chunks(raw_text)
                    get_vector_store(text_chunks)
                    st.success("Done")
  



# if __name__ == "__main__":
if 'login' in st.session_state:
    main()
else:
    st.title("Login with your user credentials")