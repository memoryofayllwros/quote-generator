# ----------input details----------
product_details = {
    'SIEMENS IMA1608': {
        'unit_price': 50.00,
        'size': '1608 mm',
        'color': 'White'
    },
    'Whirlpool SCEBM0401MT': {
        'unit_price': 60.00,
        'size': '0401 mm',
        'color': 'Silver'
    },
    'SCEBM0402MT': {
        'unit_price': 55.00,
        'size': '0402 mm',
        'color': 'Black'
    },
    'TMCDH0904': {
        'unit_price': 45.00,
        'size': '0904 mm',
        'color': 'Blue'
    },
    'SIEMENS LU83S750HK': {
        'unit_price': 4000.00,
        'size': '750 mm',
        'color': 'Stainless Steel'
    }
}

quotee_details = [
    {
        "project": "Kitchee 1/F",
        "attn": "Wilson Ng",
        "phone_number": "852-28389326",
        "email": "wilson.ng@kitchee.com",
        "address": {
            "floor&unit": "1/F",
            "street": "23 On Muk Street",
            "district": "Sha Tin",
            "region": "New Territories"
        }
    },
    {
        "project": "TechHub Office 3/F",
        "attn": "Alice Hui",
        "phone_number": "852-56781234",
        "email": "alice.hui@techhub.com",
        "address": {
            "floor&unit": "10/F",
            "street": "45 Innovation Road",
            "district": "Kowloon",
            "region": "Kowloon"
        }
    },
    {
        "project": "Green Energy Plant",
        "attn": "David Chan",
        "phone_number": "852-29876543",
        "email": "david.chan@greenenergy.com",
        "address": {
            "floor&unit": "Ground Floor",
            "street": "100 Greenway Avenue",
            "district": "Tuen Mun",
            "region": "New Territories"
        }
    },
    {
        "project": "Smart City Development",
        "attn": "Jessica Li",
        "phone_number": "852-31415926",
        "email": "jessica.li@smartcity.com",
        "address": {
            "floor&unit": "3/F",
            "street": "66 Future Way",
            "district": "Central",
            "region": "Hong Kong Island"
        }
    },
    {
        "project": "Luxury Resort",
        "attn": "Michael Ho",
        "phone_number": "852-34567890",
        "email": "michael.ho@luxuryresort.com",
        "address": {
            "floor&unit": "Lobby",
            "street": "88 Paradise Drive",
            "district": "Lantau Island",
            "region": "New Territories"
        }
    },
    {
        "project": "Community Center Renovation",
        "attn": "Rachel Cheng",
        "phone_number": "852-98765432",
        "email": "rachel.cheng@communitycenter.org",
        "address": {
            "floor&unit": "2/F",
            "street": "12 Community Lane",
            "district": "Yuen Long",
            "region": "New Territories"
        }
    },
]


sales_details = [
    {
        "sales_attn": "Jess Cheung",
        "sales_tel": "852-28389326",
        "sales_mp": "852-92276073",
        "sales_email": "jess@virpluz.io",
        "sales_company": "Virpluz Limited Ltd.",
    },
    {
        "sales_attn": "Tara Ho",
        "sales_tel": "852-21234567",
        "sales_mp": "852-91234567",
        "sales_email": "tara.hui@virpluz.io",
        "sales_company": "Virpluz Limited Ltd.",
    },
    {
        "sales_attn": "Brian Chan",
        "sales_tel": "852-29876543",
        "sales_mp": "852-98765432",
        "sales_email": "brian.chan@virpluz.io",
        "sales_company": "Virpluz Limited Ltd.",
    },
    {
        "sales_attn": "Nancy Lee",
        "sales_tel": "852-27654321",
        "sales_mp": "852-96543210",
        "sales_email": "nancy.lee@virpluz.io",
        "sales_company": "Virpluz Limited Ltd.",
    },
    {
        "sales_attn": "Kevin Hui",
        "sales_tel": "852-23456789",
        "sales_mp": "852-92345678",
        "sales_email": "kevin.ho@virpluz.io",
        "sales_company": "Virpluz Limited Ltd.",
    }
]







import os
from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
from langchain.output_parsers.regex import RegexParser

import io
import base64
import streamlit as st
from streamlit_modal import Modal
from concurrent.futures import ThreadPoolExecutor


os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

llm = OpenAI(model_name="gpt-3.5-turbo-instruct")

# ----------splitting prompt for quotation contents and terms----------
split_text_prompt = PromptTemplate(
    input_variables=["text"],
    template="""
    Split the following text into three sections: 
    1. Quotation Contents (product and service details).
    2. Quotation Terms (financial, legal, and contractual information).
    
    Provide the split sections clearly labeled as "Quotation Contents", and "Quotation Terms".

    Text:
    {text}
    """
)

# ----------extracting quotation contents and terms----------
content_output_parser = RegexParser(
    regex=r"Description:\s*(?P<description>.*),\s*Product No.:\s*(?P<product_no>.*),\s*QTY.:\s*(?P<qty>\d+)",
    output_keys=["description", "product_no", "qty"]
)


quotation_content_prompt = PromptTemplate(
    input_variables=["text"],
    template="""
    You are an expert in identifying quotation contents from documents. 
    The quotation content includes product information, installation details, and services provided. 
    Extract the quotation contents from the following text: {text}
    Then, for the extracted quotation texts, please follow these steps and ONLY display the final extracted information as outlined below, that is, Description: [concise description], Product No.: [product/service ID], QTY.: [quantity (digits)].

    1. Split texts into separate itemized quotes.
    Split the following string into separate itemized quotes based on distinct job descriptions.
    - Do NOT output the itemized quotes or any intermediary results. 
    - This step is only for internal processing.

    2. Extract information from each itemized quotes
    Extract the following information from the text and return it in the format: Area, Product No., QTY..
    - Ensure each entry is in the format: "Description: [simple description of this itemized quote in which area], Product No./Service: [product number|service name], QTY.: [quantity (digits)]."
    - If any piece of information (Description, Product No., QTY.) is missing, indicate it as "N/A".
 
    **Reminder**: The final output should exclusively contain the extracted information formatted as: 
    Description: [concise description], Product No.: [product/service ID], QTY.: [quantity (digits)].
    
    - Do NOT include any additional text, explanations, or itemized quotes except for "Description: [concise description], Product No.: [product/service ID], QTY.: [quantity (digits)]".

    """,
    output_parser=content_output_parser
)

quotation_terms_prompt = PromptTemplate(
    input_variables=["text"],
    template="""
    You are an expert in identifying legal and contractual terms from texts and good at answering in concise and comprehensive manner. 
    The quotation terms usually include topics such as payment details, delivery information, and legal obligations.
    Extract the quotation terms from the following text: {text}

    For the extracted quotation texts, please follow these steps and ONLY display the final extracted information as outlined below.

    1. Split texts into separate itemized terms based on their topics.
    
    2. Rephrase them separarely in professional and legitimate manner to eliminate potential contractual risks.

    3. Ensure each entry is in the format, 
    "[Topic]: 
    - [details]"

    For example:
    "
    5. Delivery:
    Stock Item - 3-5 days from the date receiving your deposit and order confirmation, subject to stock unsold.
    Indent item - 10-12 weeks from the date receiving your deposit and order confirmation, subject to final confirmation by our supplier.
    "
    
    Importantly, each sentence must be completed and accurate.
    """
)

split_text_chain = split_text_prompt | llm
quotation_content_chain = quotation_content_prompt | llm
quotation_terms_chain = quotation_terms_prompt | llm


#----------retrieve details from dict----------
def get_quotee_details(project_name):
    for quotee_info in quotee_details:
        if quotee_info["project"] == project_name:
            return quotee_info
    return None


def get_sales_details(sales_name):
    for sales_info in sales_details:
        if sales_info["sales_attn"] == sales_name:
            return sales_info
    return None

# ----------generate PDF----------
from fpdf import FPDF

w = 210
h = 297

from datetime import datetime
import pytz
hk_timezone = pytz.timezone('Asia/Hong_Kong')
today_date = datetime.now(hk_timezone).strftime("%d %B %Y")

ref_counter = 0

def generate_ref_no():
    global ref_counter
    today_date_numerical = datetime.now(hk_timezone).strftime("%Y%m%d")
    last_six_digits = today_date_numerical[2:]
    count_part = f"{ref_counter:02d}"

    ref_no = f"VIR-Q{last_six_digits}-{count_part}"
    ref_counter += 1

    return ref_no

ref_no = generate_ref_no()

class CustomPDF(FPDF):
    def __init__(self, project_name, sales_name):
        super().__init__()
        self.project_name = project_name
        self.sales_name = sales_name

    def header(self):
        quotee_info = get_quotee_details(self.project_name)
        sales_info = get_sales_details(self.sales_name)

        if quotee_info and sales_info:
            address = quotee_info["address"]
            attn = quotee_info["attn"]
            phone = quotee_info["phone_number"]
            email = quotee_info["email"]
            floorunit = address["floor&unit"]
            street = address["street"]
            district = address["district"]
            region = address["region"]

            self.set_xy(158, 10)
            self.image('virpluz_logo.jpg', h=15)

            self.set_xy(10, 18)
            self.set_font("Arial", style='B', size=20)
            self.cell(20, 10, txt="QUOTATION", ln=True, align="L")
            self.ln(3)
        
            self.set_font("Arial", size=12)
            self.cell(100, 6, txt="", ln=1, align='L')
            self.cell(100, 6, txt=floorunit + ",", ln=1, align='L')
            self.cell(100, 6, txt=street + ",", ln=1, align='L')
            self.cell(100, 6, txt=district + ",", ln=1, align='L')
            self.cell(100, 6, txt=region, ln=1, align='L')
            self.ln(3) 
        
            self.cell(15, 6, txt="Attn: ", ln=0, align='R')
            self.cell(30, 6, txt=attn, ln=1, align='L')

            self.cell(15, 6, txt="Tel: ", ln=0, align='R')
            self.cell(30, 6, txt=phone, ln=1, align='L')

            self.cell(15, 6, txt="Email: ", ln=0, align='R')
            self.cell(30, 6, txt=email, ln=1, align='L')
            self.ln(4) 

            self.set_font('Arial', style='B', size=16)
            self.cell(100, 8, txt=f"Project: {self.project_name}", ln=True, align='L')

            self.set_line_width(0.8)
            self.line(5, 84, 205, 84)
    
            #quoter info
            self.set_font('Arial', size=12)
            self.set_xy(-85, 46)
            self.cell(30, 6, txt="Ref. No: ", ln=0, align="R")
            self.cell(50, 6, txt=ref_no, ln=1, align="L")

            self.set_xy(-85, 52)
            self.cell(30, 6, txt="Date: ", ln=0, align="R")
            self.cell(50, 6, txt=today_date, ln=1, align="L")

            self.set_xy(-85, 58)
            self.cell(30, 6, txt="Salesman: ", ln=0, align="R")
            self.cell(50, 6, txt=sales_info['sales_attn'], ln=1, align="L")

            self.set_xy(-85, 64)
            self.cell(30, 6, txt="Sales Tel: ", ln=0, align="R")
            self.cell(50, 6, txt=sales_info['sales_tel'], ln=1, align="L")

            self.set_xy(-85, 70)
            self.cell(30, 6, txt="Sales MP: ", ln=0, align="R")
            self.cell(50, 6, txt=sales_info['sales_mp'], ln=1, align="L")

            self.set_xy(-85, 76)
            self.cell(30, 6, txt="Sales Email: ", ln=0, align="R")
            self.cell(50, 6, txt=sales_info['sales_email'], ln=1, align="L")

        else:
            st.error("Project details not found.")

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", size=11)
        current_page = self.page_no()
        footer_text = f"{ref_no} | Page {current_page}"
        self.cell(0, 10, footer_text, align = "R")

    def add_signature_section(self):
        quotee_info = get_quotee_details(self.project_name)
        sales_info = get_sales_details(self.sales_name)
        signature_height = 60

        if self.get_y() + signature_height > 297 - 10:
            self.add_page()
 
        self.ln(10) 
        self.set_xy(10, -60)
        self.set_font("Arial", size=12)

        # Quoter's signature
        self.cell(30, 6, txt="For and on behalf of", ln=0, align='L')
        self.cell(80, 6, "", ln=0)  
        self.cell(30, 6, txt="Confirmed and Accepted By", ln=1, align='L')

        self.set_font("Arial", style='B', size=12)
        self.cell(30, 6, txt=sales_info["sales_company"], ln=0, align='L')
        self.cell(80, 6, "", ln=0)  
        self.cell(30, 6, txt="", ln=1, align='C')  

        self.set_font("Arial", size=12)
        self.cell(80, 10, "_______________________", ln=0, align='L')
        self.cell(30, 10, "", ln=0)
        self.cell(80, 10, "_______________________", ln=1, align='L')

        self.set_font("Arial", style='B', size=12)
        self.cell(80, 6, txt=sales_info["sales_attn"], ln=0, align='L')
        self.cell(30, 6, "", ln=0)
        self.cell(80, 6, "Customer's Signature", ln=1, align='L')

        # Additional lines for dates or company stamps
        self.cell(30, 6, "Sales Manager", ln=0, align='L')
        self.cell(80, 6, "", ln=0)
        self.cell(30, 6, "Date: ", ln=1, align='L')


# PDF generation function with integrated table and custom header & footer
def generate_pdf(quotation_contents, quotation_terms, pdf_output, project_name, sales_name):
    pdf = CustomPDF(project_name, sales_name)
    pdf.add_page()

    pdf.set_font('Arial', size=9)
    pdf.set_xy(10, 94)
    pdf.cell(190, 6, "", ln=True, align='L')

    pdf.set_xy(5, 104)
    pdf.set_font("Arial", style='BU', size=12)
    pdf.cell(15, 7, "Item", align='C')
    pdf.cell(65, 7, "Description", align='L')
    pdf.cell(40, 7, "Product No.", align='L')
    pdf.cell(25, 7, "Unit Price", align='R')
    pdf.cell(25, 7, "QTY.", align='C')
    pdf.cell(25, 7, "Amount HKD", align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=10)

    grand_total = 0.0

    # Loop through each quote line and add to table with improved formatting
    for i, line in enumerate(quotation_contents.split('\n'), start=1):
        if not line.strip():
            continue

        parts = line.split(', ')

    # Check if there are enough parts in the line to proceed
        if len(parts) < 3:
            continue

        try:
            description = parts[0].split(': ')[1] if len(parts) > 0 and ': ' in parts[0] else ""
            product_service = parts[1].split(': ')[1] if len(parts) > 1 and ': ' in parts[1] else ""
            qty_str = parts[2].split(': ')[1] if len(parts) > 2 and ': ' in parts[2] else ""

            try:
                qty = float(qty_str)
            except ValueError:
                qty = 0

        except IndexError:
            description, product_service, qty = "", "", 0

    # Skip line if essential fields are missing
        if not description or not product_service or qty == 0:
            continue

    # Retrieve unit price from predefined dictionary, or skip if not foun
        product_info = product_details.get(product_service)
        if product_info is None:
            continue

        unit_price = product_info.get('unit_price')
        total_price = qty * unit_price
        grand_total += total_price
        total_price = "{:.2f}".format(qty * unit_price)

        # Add each row to the PDF with right-aligned numeric columns
        pdf.set_x(5)
        pdf.cell(15, 10, str(i), 0, 0, 'C')

        description_height = pdf.get_string_width(description) / 65
        pdf.multi_cell(65, 10, description, 0, 'L')
        pdf.set_xy(pdf.get_x() + 80, pdf.get_y() - description_height * 10)

        pdf.cell(40, 10, product_service, 0, 0, 'L')
        pdf.cell(25, 10, str(unit_price), 0, 0, 'R')
        pdf.cell(25, 10, str(qty), 0, 0, 'C')
        pdf.cell(25, 10, str(total_price), 0, 1, 'R')

    # After the loop, print the total amount
    pdf.ln(5)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(170, 10, "Total Amount (HKD):", align='R')
    pdf.cell(21, 10, "{:.2f}".format(grand_total), align='R')

    pdf.ln(10)

# Terms and conditions title
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.set_xy(10, 97)
    pdf.cell(0, 10, "Terms & Conditions", align='L', ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    terms_lines = quotation_terms.split("\n")

    # Add each term to the PDF
    for term in terms_lines:
        if pdf.get_y() > 260:
            pdf.add_page()
            pdf.set_xy(10, 97)

        pdf.multi_cell(0, 5, term)

    pdf.ln(20)
    pdf.add_signature_section()

    pdf_output.write(pdf.output(dest='S').encode('latin1'))


# ----------Streamlit UI----------

def process_quotation_content(quotation_content_text):
    return quotation_content_chain.invoke({"text": quotation_content_text})

def process_quotation_terms(quotation_terms_text):
    return quotation_terms_chain.invoke({"text": quotation_terms_text})

def main():
    st.set_page_config(page_title="Quote Generator", page_icon=":page_facing_up:")
    st.title("Quote Generator")
    st.caption("An Estimate & Quote Generator Powered by OpenAI.")

    project_name = st.text_input("Project", placeholder="e.g., TechHub Office 3/F", key="project_name")
    sales_name = st.text_input("Quoter", placeholder="e.g., Tara Ho", key="sales_name")

    sample_text = st.text_area(
        "Enter Your Quote Details, Please Specifically Include Product No./Service & Quantity.",
        height=300
    )

    modal = Modal(key="materials_modal", title="Additional Materials Reminder")

    if st.button("Generate Quote"):
        if sample_text:
            split_result = split_text_chain.invoke({"text": sample_text})
            quotation_content_text = split_result.split("Quotation Terms:")[0].replace("Quotation Contents:", "").strip()
            quotation_terms_text = split_result.split("Quotation Terms:")[1].strip()

            # run both chains in parallel
            with ThreadPoolExecutor() as executor:
                content_future = executor.submit(process_quotation_content, quotation_content_text)
                terms_future = executor.submit(process_quotation_terms, quotation_terms_text)

                quotation_contents_result = content_future.result()
                quotation_terms_result = terms_future.result()

            st.session_state['quotation_items'] = quotation_contents_result
            st.session_state['quotation_terms'] = quotation_terms_result

            with modal.container():
                st.markdown("""
                    **Reminder:** 
                    Would you like to include additional materials, such as cements, in your quotation?
                """)
                if st.button("Yes, I need additional materials"):
                    st.write("Additional materials will be included in the quotation.")
                elif st.button("No, please proceed"):
                    st.write("Proceeding without additional materials.")


    # Ensure contents and terms are available for download and preview
    if 'quotation_items' in st.session_state and 'quotation_terms' in st.session_state:
        st.subheader("Quotation Info Check:")
        st.write(f"This quotation is generated for {project_name} from {sales_name}.")
            
        if not project_name or not sales_name:
            st.error("Please enter both Project Name and Sales Name.")
            
        quotation_items_editable = st.text_area("Quotation Items", st.session_state['quotation_items'], height=200)
        quotation_terms_editable = st.text_area("Quotation Terms", st.session_state['quotation_terms'], height=200)

        pdf_buffer = io.BytesIO()

        if st.button("Generate PDF"):
            generate_pdf(quotation_items_editable, quotation_terms_editable, pdf_buffer, project_name, sales_name)

            st.subheader("PDF Preview")
            pdf_buffer.seek(0)  # Move to the start of the BytesIO buffer
            pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')

            st.write(
                f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="700" height="800"></iframe>',
                unsafe_allow_html=True,
                )

            st.download_button(
                label="Download Quotation",
                data=pdf_buffer.getvalue(),
                file_name="quote.pdf",
                mime="application/pdf"
                )

if __name__ == '__main__':
    main()

