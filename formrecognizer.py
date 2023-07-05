"""
This code sample shows Prebuilt Layout operations with the Azure Form Recognizer client library. 
The async versions of the samples require Python 3.6 or later.

To learn more, please visit the documentation - Quickstart: Form Recognizer Python client library SDKs
https://docs.microsoft.com/en-us/azure/applied-ai-services/form-recognizer/quickstarts/try-v3-python-sdk
"""

from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import os
from dotenv import load_dotenv

class AzureFormRecognizerClient:
    def __init__(self, form_recognizer_endpoint: str = None, form_recognizer_key: str = None):

        load_dotenv()

        self.pages_per_embeddings = int(os.getenv('PAGES_PER_EMBEDDINGS', 2))
        self.section_to_exclude = ['footnote', 'pageHeader', 'pageFooter', 'pageNumber']

        self.form_recognizer_endpoint : str = form_recognizer_endpoint if form_recognizer_endpoint else os.getenv('FORM_RECOGNIZER_ENDPOINT')
        self.form_recognizer_key : str = form_recognizer_key if form_recognizer_key else os.getenv('FORM_RECOGNIZER_KEY')


    def analyze_read(self, document):

      document_analysis_client = DocumentAnalysisClient(
            endpoint=self.form_recognizer_endpoint, credential=AzureKeyCredential(self.form_recognizer_key)
        )
      
      poller = document_analysis_client.begin_analyze_document("prebuilt-receipt", document, pages="2-6")
      result = poller.result()

      page_values = []
      for idx, receipt in enumerate(result.documents):
        value = {}
        receipt_type = receipt.doc_type
        value['ReceiptType'] = receipt_type if receipt_type else ""
        
        merchant_name = receipt.fields.get("MerchantName")
        value['MerchantName'] = merchant_name.value if merchant_name else ""
        
        transaction_date = receipt.fields.get("TransactionDate")
        value['TransactionDate'] = transaction_date.value if transaction_date else ""
        
        value['Items'] = []
        items = receipt.fields.get("Items")
        if items:
            for idx, item in enumerate(items.value):
                row = {}
                item_description = item.value.get("Description")
                row['Description'] = item_description.value if item_description else ""
                
                item_quantity = item.value.get("Quantity")
                row['Quantity'] = item_quantity.value if item_quantity else ""
                
                item_price = item.value.get("Price")
                row['Price'] = item_price.value if item_price else ""
                
                item_total_price = item.value.get("TotalPrice")
                row['TotalPrice'] = item_total_price.value if item_total_price else ""
                
                value['Items'].append(row)

        subtotal = receipt.fields.get("Subtotal")
        value['Subtotal'] = subtotal.value if subtotal else ""
        
        tax = receipt.fields.get("TotalTax")
        value['TotalTax'] = tax.value if tax else ""
        
        tip = receipt.fields.get("Tip")
        value['Tip'] = tip.value if tip else ""
        
        total = receipt.fields.get("Total")
        value['Total'] = total.value if total else ""

        page_values.append(value)

      return page_values

