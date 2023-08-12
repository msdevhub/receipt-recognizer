import streamlit as st
import os
import pandas as pd
from formrecognizer import AzureFormRecognizerClient
from db import PDFDatabase
import base64

import yaml
from yaml.loader import SafeLoader
import streamlit as st
import streamlit_authenticator as stauth

# 添加用户界面元素到左侧侧边栏 
st.set_page_config(page_title="上传和显示表格", layout="wide")

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)
name, authentication_status, username = authenticator.login('Login', 'main')


pdf_parser = AzureFormRecognizerClient()
database = PDFDatabase()
database.create_tables()

# print("Analyze Layouts...",os.getenv('DB_HOST'),  os.getenv('DB_PORT'), os.getenv('DB_NAME'), os.getenv('DB_USER'), os.getenv('DB_PASSWORD'))

def upload_file(file):
    # 显示正在上传的状态
    with st.spinner("正在上传文件..."):
        # 将上传的文件保存到data目录中
        with open(os.path.join("./data", file.name), "wb") as f:
            file_value = file.getvalue()
            values = pdf_parser.analyze_read(file_value)

            database.insert_data_to_mysql(values, file.name, os.path.join("./data", file.name)) # insert pdf data from pdf_parser.analyze_read values first row
            f.write(file_value)
    
    # 显示上传成功消息
    st.sidebar.write("文件上传成功")
    # 更新侧边栏中的文件列表
    st.experimental_rerun()

def main():
    # st.sidebar.title("侧边栏")

    # 获取PDF文件列表
    files = database.get_pdf_files()

    # 显示文件列表
    st.sidebar.subheader("上传的文件列表")
    if len(files) == 0:
        st.sidebar.write("还没有上传任何文件")
    else:
        # 使用radio组件显示文件列表
        selected_file, selected_file_id = st.sidebar.radio("选择要查看的文件", files, format_func=lambda file: file[0])

        # 显示选择的文件信息
        st.sidebar.write(f"选择的文件：{selected_file}，{selected_file_id}")

        # 获取选择文件的收据信息和收据项信息
        receipts = database.get_receipts_by_pdf_id(selected_file_id)
        receipt_items = database.get_receipt_items_by_pdf_id(selected_file_id)

        # 显示收据统计信息，包括收据数量、收据项数量、总金额
        st.title("收据统计信息")
        st.write(f"收据数量：{len(receipts)}")
        st.write(f"收据项数量：{len(receipt_items)}")
        # st.write(f"总金额：{sum([receipt[8] if receipt[0] else 0 for receipt in receipts])}")


        # 显示收据信息
        st.subheader("收据信息：")
        if len(receipts) == 0:
            st.write("没有找到收据信息")
        else:
            receipts_df = pd.DataFrame(receipts, columns=["ID", "PDF ID", "Receipt Type", "Merchant Name", "Transaction Date", "Subtotal", "Total Tax", "Tip", "Total"])
            st.table(receipts_df)

        # 显示收据项信息
        st.subheader("收据项信息：")
        if len(receipt_items) == 0:
            st.write("没有找到收据项信息")
        else:
            receipt_items_df = pd.DataFrame(receipt_items, columns=["ID","PDF", "Receipt","TransactionDate", "Description", "Quantity", "QuantityUnit", "Price", "Total Price"])
            st.table(receipt_items_df)


        # 显示选中的PDF文件
        # st.subheader("PDF预览")
        # with open(os.path.join("./data", selected_file), "rb") as f:
        #     pdf_data = f.read()
        # b64_pdf = base64.b64encode(pdf_data).decode("utf-8")
        # pdf_file_name = os.path.splitext(selected_file)[0]
        # download_link = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_file_name}.pdf">点击此处下载PDF文件</a>'
        # st.markdown(download_link, unsafe_allow_html=True)
        # st.write(f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="600px" style="border: none;"></iframe>', unsafe_allow_html=True)


    with st.sidebar.form("upload_form"):
        st.subheader("选择要上传的文件")
        uploaded_file = st.file_uploader("上传PDF文件", type=["pdf", "jpg", "jpeg"])
        submit_button = st.form_submit_button("上传")

        if submit_button and uploaded_file is not None:
            upload_file(uploaded_file)

if __name__ == '__main__':
    if authentication_status:

        authenticator.logout('Logout', 'main', key='unique_key')
        st.write(f'Welcome *{name}*')
        
        main()
    elif authentication_status is False:
        st.error('Username/password is incorrect')
    elif authentication_status is None:
        st.warning('Please enter your username and password')

