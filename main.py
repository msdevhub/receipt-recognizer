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

custom_html = '''
<!DOCTYPE html><html><head><style>.right-eye {  position: absolute;  width: 45px;  height: 106px;  top: 81px;  left: 261.5px;  background: var(--eye-4);  border-radius: 50%;  transform: rotate(-5deg);}.right-eye::before {  content: "";  position: absolute;  width: 32px;  height: 67px;  top: 34px;  left: 6px;  background: linear-gradient(to top, var(--eye-2) 10%, var(--eye-3) 30%);  border-radius: 50%;}.right-eye::after {  content: "";  position: absolute;  width: inherit;  height: inherit;  background:  radial-gradient(        100% 100% at 50% 50%,        var(--eye-1) 49%,        var(--t) 0%      )      50% 11% / 24px 37px,          radial-gradient(100% 100% at 50% 50%, var(--eye-2) 49%, var(--t) 50%) 50%      7% / 31px 44px,          radial-gradient(100% 100% at 50% 50%, var(--eye-4) 49%, var(--t) 50%) 50%      58% / 35px 45px;  background-repeat: no-repeat;  filter: blur(0.5px);  border-radius: 50%;}.left-eye {  position: absolute;  width: 44px;  height: 102px;  top: 88px;  left: 176px;  background: var(--eye-4);  border-radius: 50%;  background-repeat: no-repeat;  transform: rotate(0deg);}.left-eye::before {  content: "";  position: absolute;  width: 32px;  height: 67px;  top: 31px;  left: 5px;  background: linear-gradient(to top, var(--eye-2) 10%, var(--eye-3) 30%);  border-radius: 50%;  transform: rotate(-3deg);}.left-eye::after {  content: "";  position: absolute;  width: inherit;  height: inherit;  background:  radial-gradient(        100% 100% at 50% 50%,        var(--eye-1) 49%,        var(--t) 50%      )      50% 11% / 24px 37px,          radial-gradient(100% 100% at 50% 50%, var(--eye-2) 49%, var(--t) 50%) 50%      7% / 31px 44px,          radial-gradient(100% 100% at 50% 50%, var(--eye-4) 49%, var(--t) 50%) 50%      58% / 39px 45px;  background-repeat: no-repeat;  filter: blur(0.5px);  border-radius: 50%;}.cheek-mark {  position: absolute;  width: 54px;  height: 41px;  top: 175px;  left: 109px;  background: var(--body-5);  border-radius: 50%;  filter: blur(2px);  box-shadow: 217px -10px 2px 0 var(--body-5);}.mouth {  position: absolute;  width: 62px;  height: 53px;  top: 193px;  left: 214px;  background: var(--mouth-2);  clip-path: path(    "M 32,1 C 57,2 70,12 50,39 C 48,41 34,60 17,44 C -12,15 3,2 32,1"  );}.mouth::after {  content: "";  position: absolute;  width: 62px;  height: 53px;  background:       radial-gradient(      100% 100% at 50% 50%,      var(--mouth-4),      var(--mouth-1) 49%,      var(--t) 50%    )    50% 93% / 61px 30px;  background-repeat: no-repeat;  transform: rotate(-2deg);  filter: blur(0.5px);}.body {  position: absolute;  width: 365px;  height: 358px;  top: 25px;  left: 64px;  background: radial-gradient(      100% 100% at 50% 50%,      var(--body-1) 25%,      var(--body-2),      var(--body-4) 49%,      var(--t) 50%    )    80% 83% / 355px 358px;  background-repeat: no-repeat;  filter: drop-shadow(2px 15px 5px var(--shadow));}.left-arm {  position: absolute;  width: 140px;  height: 110px;  top: 154px;  left: 17px;  background: radial-gradient(    at 20% 30%,    var(--body-2) 5%,    var(--body-3),    var(--body-5)  );  border-radius: 50%;  transform: rotate(-32deg);}.right-arm {  position: absolute;  width: 125px;  height: 135px;  top: 87px;  left: 356px;  background: radial-gradient(    at 50% 30%,    var(--body-1) 5%,    var(--body-2),    var(--body-4) 60%  );  border-radius: 50%;  filter: drop-shadow(0px 5px 10px var(--shadow));}.right-foot {  position: absolute;  width: 153px;  height: 234px;  top: 240px;  left: 251px;  background: radial-gradient(    circle at 50% 75%,    var(--feet-1) 10%,    var(--feet-2) 50%  );  border-radius: 50%;  background-repeat: no-repeat;  transform: rotate(12deg);}.left-foot {  position: absolute;  width: 213px;  height: 151px;  top: 252px;  left: 40px;  background: radial-gradient(at 45% 50%, var(--feet-2), var(--feet-1));  border-radius: 50%;  transform: rotate(41deg);  filter: drop-shadow(2px -1px 5px var(--shadow));}.left-foot::before {  content: "";  position: absolute;  width: 213px;  height: 151px;  background:   radial-gradient(        100% 100% at 50% 50%,        var(--feet-4) 49%,        var(--t) 50%      )      27% 21% / 80px 25px,          radial-gradient(100% 100% at 50% 50%, var(--feet-3) 49%, var(--t) 50%) 55%      80% / 185px 96px;  background-repeat: no-repeat;  border-radius: 50%;  filter: blur(10px);}:root {    --t: transparent;    --body-1: hsla(322, 100%, 86%, 1);  --body-2: hsla(329, 100%, 84%, 1);  --body-3: hsla(340, 97%, 77%, 1);  --body-4: hsla(341, 92%, 74%, 1);  --body-5: hsla(328, 100%, 69%, 1);    --eye-1: hsla(300, 100%, 100%, 1);  --eye-2: hsla(224, 78%, 51%, 1);  --eye-3: hsla(226, 77%, 18%, 1);  --eye-4: hsla(0, 0%, 0%, 1);    --mouth-1: hsla(357, 78%, 54%, 1);  --mouth-2: hsla(353, 98%, 17%, 1);  --mouth-3: hsla(0, 0%, 100%, 0.08);  --mouth-4: hsla(356, 78%, 43%, 1);    --feet-1: hsla(347, 97%, 59%, 1);  --feet-2: hsla(342, 100%, 33%, 1);  --feet-3: hsla(345, 95%, 29%, 1);  --feet-4: hsla(347, 97%, 60%, 1);    --shadow: hsla(240, 0%, 26%, 0.5);}body {  margin: 0;  padding: 0;  height: 100vh;  display: flex;  justify-content: center;  align-items: center;  flex-wrap: wrap;}.container {  width: 500px;  height: 500px;    background: transparent;  position: relative;  display: flex;  justify-content: center;  align-items: center;  border-radius: 1px;  zoom: 0.5;}</style></head><body><div class="container" id="follower"><div class="character"><div class="left-arm"></div><div class="right-foot"></div><div class="body"></div><div class="cheek-mark"></div><div class="right-arm"></div><div class="right-eye"></div><div class="left-eye"></div><div class="mouth"></div><div class="left-foot"></div></div></div><script>  setTimeout(()=>{document.body.addEventListener('mousemove', function(event) {debugger;  var follower = document.getElementById('follower');  follower.style.left = -550+event.clientX + 'px';  follower.style.top = -50+event.clientY + 'px';}); },1500)  </script></body></html>
'''

st.markdown(custom_html, unsafe_allow_html=True)


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

