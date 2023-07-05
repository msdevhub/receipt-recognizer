import streamlit as st
import os
import pandas as pd
from formrecognizer import AzureFormRecognizerClient
from db import get_pdf_files, get_receipt_items_by_pdf_id, insert_data_to_mysql, get_receipts_by_pdf_id, get_receipt_items_by_receipt_id

pdf_parser = AzureFormRecognizerClient()

def main():
    st.set_page_config(page_title="上传和显示表格", layout="wide")
    st.sidebar.title("侧边栏")

    # 获取PDF文件列表
    files = get_pdf_files()

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
        receipts = get_receipts_by_pdf_id(selected_file_id)
        receipt_items = get_receipt_items_by_pdf_id(selected_file_id)

        # 显示收据信息
        st.write("收据信息：")
        if len(receipts) == 0:
            st.write("没有找到收据信息")
        else:
            receipts_df = pd.DataFrame(receipts, columns=["ID", "PDF ID", "Receipt Type", "Merchant Name", "Transaction Date", "Subtotal", "Total Tax", "Tip", "Total"])
            st.table(receipts_df)

        # 显示收据项信息
        st.write("收据项信息：")
        if len(receipt_items) == 0:
            st.write("没有找到收据项信息")
        else:
            receipt_items_df = pd.DataFrame(receipt_items, columns=["ID","PDF ID", "Receipt ID", "Description", "Quantity", "Price", "Total Price"])
            st.table(receipt_items_df)

    # 上传文件
    st.sidebar.subheader("选择要上传的文件")
    uploaded_file = st.sidebar.file_uploader("上传PDF文件", type=["pdf", "jpg", "jpeg"])
    if uploaded_file is not None:
        # 检查文件名是否已存在
        if uploaded_file.name in files:
            st.sidebar.write("文件名已存在，请重新命名文件")
        else:
            # 将上传的文件保存到data目录中
            with open(os.path.join("./data", uploaded_file.name), "wb") as f:
                file_value = uploaded_file.getvalue()
                values = pdf_parser.analyze_read(file_value)
                insert_data_to_mysql(values, uploaded_file.name, os.path.join("./data", uploaded_file.name))
                f.write(file_value)
            # 自动刷新侧边栏中的文件列表
            st.experimental_rerun()

if __name__ == '__main__':
    main()
