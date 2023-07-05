import streamlit as st
import pandas as pd
import os
from formrecognizer import AzureFormRecognizerClient
from db import insert_data_to_mysql

pdf_parser = AzureFormRecognizerClient()

def read_upload_file(file_path):
    """
    读取并显示给定路径的CSV文件
    """
    df = pd.read_csv(file_path)
    st.write("上传的数据帧：")
    st.write(df)
    st.write("表格：")
    st.table(df)

def main():
    st.set_page_config(page_title="上传和显示表格", layout="wide")
    st.sidebar.title("侧边栏")

    # 获取data目录中的CSV文件列表
    files = []
    for filename in os.listdir("./data"):
        # if filename.endswith(".csv"):
        files.append(filename)

    # 显示文件列表
    st.sidebar.subheader("上传的文件列表")
    if len(files) == 0:
        st.sidebar.write("还没有上传任何文件")
    else:
        # 使用radio组件显示文件列表
        selected_file = st.sidebar.radio("选择要查看的文件", files)
        file_path = os.path.join("./data", selected_file)
        read_upload_file(file_path)

    # 上传文件
    st.sidebar.subheader("选择要上传的文件")
    uploaded_file = st.sidebar.file_uploader("上传CSV文件", type=["pdf","jpg","jpeg", "csv"])
    if uploaded_file is not None:
        # 检查文件名是否已存在
        if uploaded_file.name in files:
            st.sidebar.write("文件名已存在，请重新命名文件")
        else:
            # 将上传的文件保存到data目录中
            with open(os.path.join("./data", uploaded_file.name), "wb") as f:
                file_value = uploaded_file.getvalue()
                values = pdf_parser.analyze_read(file_value)
                df = pd.json_normalize(values, ['Items'], ['MerchantName', 'TransactionDate', 'Total', 'Subtotal', 'TotalTax', 'Tip'])
                st.write(df)
                print(df)
                print(values)
                insert_data_to_mysql(values)
                f.write(file_value)
            # 自动刷新侧边栏中的文件列表
            # st.experimental_rerun()
            # 显示上传的文件
            # read_upload_file(uploaded_file)

if __name__ == '__main__':
    main()