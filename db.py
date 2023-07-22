import pymysql
import os


class PDFDatabase:
    def __init__(self):
        self.connection = pymysql.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )

    def __del__(self):
        print('self.connection.close()')

    def create_tables(self):
        self.connection.connect()
        cursor = self.connection.cursor()

        create_pdfs_table_query = """
        CREATE TABLE IF NOT EXISTS pdfs (
          id INT PRIMARY KEY AUTO_INCREMENT,
          filename VARCHAR(255),
          filepath VARCHAR(255),
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_pdfs_table_query)

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

        create_items_table_query = """
        CREATE TABLE IF NOT EXISTS receipt_items (
          id INT PRIMARY KEY AUTO_INCREMENT,
          pdf_id INT,
          receipt_id INT,
          Description VARCHAR(255),
          Quantity DECIMAL(10, 2),
          QuantityUnit VARCHAR(255),
          Price DECIMAL(10, 2),
          TotalPrice DECIMAL(10, 2),
          FOREIGN KEY (receipt_id) REFERENCES receipts(id)
        )
        """
        cursor.execute(create_items_table_query)

        cursor.close()
        self.connection.close()

    def get_pdf_files(self):
        """
        获取PDF文件列表
        """
        self.connection.connect()
        cursor = self.connection.cursor()
        query_files = "SELECT id, filename FROM pdfs"
        cursor.execute(query_files)
        result = cursor.fetchall()
        files = [(row[1], row[0]) for row in result]
        cursor.close()
        self.connection.close()
        return files

    def get_receipts_by_pdf_id(self, pdf_id):
        """
        根据 PDF ID 获取收据信息列表
        """
        self.connection.connect()
        cursor = self.connection.cursor()
        query_receipts = "SELECT * FROM receipts WHERE pdf_id = %s"
        cursor.execute(query_receipts, (pdf_id,))
        result = cursor.fetchall()
        cursor.close()
        self.connection.close()
        return result

    def get_receipt_items_by_pdf_id(self, pdf_id):
        self.connection.connect()
        cursor = self.connection.cursor()
        query = """
        SELECT ri.id, p.filename, r.MerchantName, r.TransactionDate, ri.Description, ri.Quantity, ri.QuantityUnit, ri.Price, ri.TotalPrice
        FROM receipt_items ri
        INNER JOIN receipts r ON ri.receipt_id = r.id
        INNER JOIN pdfs p ON ri.pdf_id = p.id
        WHERE ri.pdf_id = %s
        """
        cursor.execute(query, (pdf_id,))
        receipt_items = cursor.fetchall()
        cursor.close()
        self.connection.close()
        return receipt_items

    def get_receipt_items_by_receipt_id(self, receipt_id):
        """
        根据收据 ID 获取收据项信息列表
        """
        self.connection.connect()
        cursor = self.connection.cursor()
        query_receipt_items = "SELECT * FROM receipt_items WHERE receipt_id = %s"
        cursor.execute(query_receipt_items, (receipt_id,))
        result = cursor.fetchall()
        cursor.close()
        self.connection.close()
        return result

    def insert_data_to_mysql(self, data_list, pdf_filename, pdf_filepath):
        self.connection.connect()
        cursor = self.connection.cursor()
        check_pdf_query = """
        SELECT id FROM pdfs WHERE filename = %s
        """
        cursor.execute(check_pdf_query, (pdf_filename,))
        existing_pdf = cursor.fetchone()

        if existing_pdf:
            cursor.close()
            raise ValueError(f"PDF file '{pdf_filename}' already exists.")

        insert_pdf_query = """
        INSERT INTO pdfs (filename,filepath)
        VALUES (%s, %s)
        """
        cursor.execute(insert_pdf_query, (pdf_filename, pdf_filepath))
        pdf_id = cursor.lastrowid

        for data in data_list:
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
                    data.get("TransactionDate") if data.get("TransactionDate") != "" else None,
                    data.get("Subtotal", 0) if data.get("Subtotal") != "" else 0,
                    data.get("TotalTax", 0) if data.get("TotalTax") != "" else 0,
                    data.get("Tip", 0) if data.get("Tip") != "" else 0,
                    data.get("Total", 0) if data.get("Total") != "" else 0,
                ),
            )
            receipt_id = cursor.lastrowid

            items = data.get("Items", [])
            for item in items:
                insert_item_query = """
                INSERT INTO receipt_items (pdf_id, receipt_id, Description, Quantity,QuantityUnit, Price, TotalPrice)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(
                    insert_item_query,
                    (
                        pdf_id,
                        receipt_id,
                        item.get("Description", ""),
                        item.get("Quantity", 0) if item.get("Quantity", "") != "" else 0,
                        item.get("QuantityUnit"),
                        item.get("Price", 0) if item.get("Price", "") != "" else 0,
                        item.get("TotalPrice", 0)
                        if item.get("TotalPrice", "") != ""
                        else 0,
                    ),
                )

        self.connection.commit()
        cursor.close()
        self.connection.close()
