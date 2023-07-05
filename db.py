import pymysql
import os


def get_pdf_files():
    """
    获取PDF文件列表
    """
    # 建立数据库连接
    connection = pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

    # 创建游标对象
    cursor = connection.cursor()

    # 查询PDF表中的文件列表及其对应的 PDF ID
    query_files = "SELECT id, filename FROM pdfs"
    cursor.execute(query_files)
    result = cursor.fetchall()
    files = [(row[1], row[0]) for row in result]


    # 关闭游标和连接
    cursor.close()
    connection.close()

    return files


def get_receipts_by_pdf_id(pdf_id):
    """
    根据 PDF ID 获取收据信息列表
    """
    # 建立数据库连接
    connection = pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

    # 创建游标对象
    cursor = connection.cursor()

    # 查询指定 PDF ID 的收据信息
    query_receipts = "SELECT * FROM receipts WHERE pdf_id = %s"
    cursor.execute(query_receipts, (pdf_id,))
    result = cursor.fetchall()

    # 关闭游标和连接
    cursor.close()
    connection.close()

    return result

def get_receipt_items_by_pdf_id(pdf_id):
    # 建立数据库连接
    connection = pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

    # 创建游标对象
    cursor = connection.cursor()

    # 查询指定 PDF ID 的收据项
    query = """
    SELECT *
    FROM receipt_items
    WHERE pdf_id = %s
    """
    cursor.execute(query, (pdf_id,))
    receipt_items = cursor.fetchall()

    # 关闭游标和连接
    cursor.close()
    connection.close()

    return receipt_items


def get_receipt_items_by_receipt_id(receipt_id):
    """
    根据收据 ID 获取收据项信息列表
    """
    # 建立数据库连接
    connection = pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

    # 创建游标对象
    cursor = connection.cursor()

    # 查询指定收据 ID 的收据项信息
    query_receipt_items = "SELECT * FROM receipt_items WHERE receipt_id = %s"
    cursor.execute(query_receipt_items, (receipt_id,))
    result = cursor.fetchall()

    # 关闭游标和连接
    cursor.close()
    connection.close()

    return result

def insert_data_to_mysql(data_list, pdf_filename, pdf_filepath):
    # 建立数据库连接
    connection = pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

    # 创建游标对象
    cursor = connection.cursor()

    # 检查是否已存在相同的 PDF 文件
    check_pdf_query = """
    SELECT id FROM pdfs WHERE filename = %s
    """
    cursor.execute(check_pdf_query, (pdf_filename,))
    existing_pdf = cursor.fetchone()

    if existing_pdf:
        cursor.close()
        connection.close()
        raise ValueError(f"PDF file '{pdf_filename}' already exists.")

    # 创建PDF表
    create_pdfs_table_query = """
    CREATE TABLE IF NOT EXISTS pdfs (
      id INT PRIMARY KEY AUTO_INCREMENT,
      filename VARCHAR(255),
      filepath VARCHAR(255),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(create_pdfs_table_query)

    # 创建收据表
    create_receipts_table_query = """
    CREATE TABLE IF NOT EXISTS receipts (
      id INT PRIMARY KEY AUTO_INCREMENT,
      pdf_id INT,
      ReceiptType VARCHAR(255),
      MerchantName VARCHAR(255),
      TransactionDate DATE,
      Subtotal DECIMAL(10, 2),
      TotalTax DECIMAL(10, 2),
      Tip DECIMAL(10, 2),
      Total DECIMAL(10, 2),
      FOREIGN KEY (pdf_id) REFERENCES pdfs(id)
    )
    """
    cursor.execute(create_receipts_table_query)

    # 创建收据项表
    create_items_table_query = """
    CREATE TABLE IF NOT EXISTS receipt_items (
      id INT PRIMARY KEY AUTO_INCREMENT,
      pdf_id INT,
      receipt_id INT,
      Description VARCHAR(255),
      Quantity DECIMAL(10, 2),
      Price DECIMAL(10, 2),
      TotalPrice DECIMAL(10, 2),
      FOREIGN KEY (receipt_id) REFERENCES receipts(id)
    )
    """
    cursor.execute(create_items_table_query)

    # 插入PDF信息
    insert_pdf_query = """
    INSERT INTO pdfs (filename, filepath)
    VALUES (%s, %s)
    """
    cursor.execute(insert_pdf_query, (pdf_filename, pdf_filepath))
    pdf_id = cursor.lastrowid

    # 插入收据信息和收据项信息
    for data in data_list:
        # 插入收据信息
        insert_receipt_query = """
        INSERT INTO receipts (pdf_id, ReceiptType, MerchantName, TransactionDate, Subtotal, TotalTax, Tip, Total)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            insert_receipt_query,
            (
                pdf_id,
                data.get("ReceiptType"),
                data.get("MerchantName"),
                data.get("TransactionDate"),
                data.get("Subtotal", 0) if data.get("Subtotal") != "" else 0,
                data.get("TotalTax", 0) if data.get("TotalTax") != "" else 0,
                data.get("Tip", 0) if data.get("Tip") != "" else 0,
                data.get("Total", 0) if data.get("Total") != "" else 0,
            ),
        )
        receipt_id = cursor.lastrowid

        # 插入收据项信息
        items = data.get("Items", [])
        for item in items:
            insert_item_query = """
            INSERT INTO receipt_items (pdf_id, receipt_id, Description, Quantity, Price, TotalPrice)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                insert_item_query,
                (
                    pdf_id,
                    receipt_id,
                    item.get("Description", ""),
                    item.get("Quantity", 0) if item.get("Quantity", "") != "" else 0,
                    item.get("Price", 0) if item.get("Price", "") != "" else 0,
                    item.get("TotalPrice", 0)
                    if item.get("TotalPrice", "") != ""
                    else 0,
                ),
            )

    # 提交事务
    connection.commit()

    # 关闭游标和连接
    cursor.close()
    connection.close()
