import os
import streamlit as st
from langchain_openai import OpenAI
from fpdf import FPDF

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# LLM function
def extract_information(prompt_ExtractInfo):
    llm = OpenAI(
        model_name="gpt-3.5-turbo-instruct",
        temperature=0,
        max_tokens=500
    )
    response = llm.generate([prompt_ExtractInfo])
    return response.generations[0][0].text.strip()


# Predefined products and their unit prices
product_details = {
    'SIEMENS IMA1608': 50.00,
    'Whirlpool SCEBM0401MT': 60.00,
    'SCEBM0402MT': 55.00,
    'TMCDH0904': 45.00,
    'SIEMENS LU83S750HK': 4000.00,
}


class CustomPDF(FPDF):
    def header(self):
        self.set_xy(158, 8)
        self.image('virpluz_logo.jpg', h=15)

        self.set_xy(10, 18)
        self.set_font("Arial", style='B', size=20)
        self.cell(20, 10, txt="QUOTATION", ln=True, align="L")
        self.ln(3)
        
        self.set_font("Arial", size=12)
        self.cell(100, 6, txt="Kitchee Foundation Ltd.", ln=1, align='L')
        self.cell(100, 6, txt="23 On Muk Street,", ln=1, align='L')
        self.cell(100, 6, txt="Shek Mun,", ln=1, align='L')
        self.cell(100, 6, txt="Shatin,", ln=1, align='L')
        self.cell(100, 6, txt="New Territories.", ln=1, align='L')
        self.ln(3) 
        
        self.cell(15, 6, txt="Attn: ", ln=0, align='R')
        self.cell(30, 6, txt="Wilson Ng", ln=1, align='L')

        self.cell(15, 6, txt="Tel: ", ln=0, align='R')
        self.cell(30, 6, txt="852 - 28389326", ln=1, align='L')

        self.cell(15, 6, txt="Email: ", ln=0, align='R')
        self.cell(30, 6, txt="wilson.ng@kitchee.com", ln=1, align='L')
        self.ln(4) 

        self.set_font('Arial', style='B', size=16)
        self.cell(100, 8, txt="Project: Kitchee 1/F", ln=True, align='L')

        self.set_line_width(0.8)
        self.line(5, 84, 205, 84)

        # Quoter Information
        self.set_font('Arial', size=12)
        self.set_xy(-85, 46)
        self.cell(30, 6, txt="Ref. No: ", ln=0, align="R")
        self.cell(50, 6, txt="HQ240949FTS-00", ln=1, align="L")

        self.set_xy(-85, 52)
        self.cell(30, 6, txt="Date: ", ln=0, align="R")
        self.cell(50, 6, txt="25 Sep 2024", ln=1, align="L")

        self.set_xy(-85, 58)
        self.cell(30, 6, txt="Salesman: ", ln=0, align="R")
        self.cell(50, 6, txt="Jess Cheung", ln=1, align="L")

        self.set_xy(-85, 64)
        self.cell(30, 6, txt="Sales Tel: ", ln=0, align="R")
        self.cell(50, 6, txt="852 - 21025588", ln=1, align="L")

        self.set_xy(-85, 70)
        self.cell(30, 6, txt="Sales MP: ", ln=0, align="R")
        self.cell(50, 6, txt="852 - 92276073", ln=1, align="L")

        self.set_xy(-85, 76)
        self.cell(30, 6, txt="Sales Email: ", ln=0, align="R")
        self.cell(50, 6, txt="jess@virpluz.io", ln=1, align="L")

    def footer(self):
        self.set_y(-15)  # Set position from the bottom of the page
        self.set_font("Arial", size=11)
        
        # Combine the reference number and page number, separated by a pipe or dash
        ref_number = "HQ240949FTS-00"
        page_number = "Page " + str(self.page_no())

        self.cell(0, 10, f"{ref_number} | {page_number}", align='R')
        
# PDF generation function with integrated table and custom header/footer
def generate_pdf(quote_info, file_name):
    pdf = CustomPDF()
    pdf.add_page()

    # Set table headers
    pdf.set_font('Arial', size=10)
    pdf.set_xy(10, 94)
    pdf.cell(190, 6, "kitchen and bathroom tiling & range hood", ln=True, align='L')

    pdf.set_xy(5, 104)
    pdf.set_font("Arial", style='BU', size=12)
    pdf.cell(15, 7, "Item", align='C')
    pdf.cell(65, 7, "Description", align='L')
    pdf.cell(40, 7, "Product No.", align='L')
    pdf.cell(25, 7, "Unit HKD", align='R')
    pdf.cell(25, 7, "QTY.", align='C')
    pdf.cell(25, 7, "Amount HKD", align='C')
    pdf.ln(10)

    # Set content font for table rows
    pdf.set_font("Arial", size=11)

    grand_total = 0.0

    # Loop through each quote line and add to table with improved formatting
    for i, line in enumerate(quote_info.split('\n'), start = 1):
        parts = line.split(', ')

        try:
            description = parts[0].split(': ')[1] if len(parts) > 0 and ': ' in parts[0] else "N/A"
            product_service = parts[1].split(': ')[1] if len(parts) > 1 and ': ' in parts[1] else "N/A"
            qty_str = parts[2].split(': ')[1] if len(parts) > 2 and ': ' in parts[2] else "N/A"

            try:
                qty = float(qty_str)
            except ValueError:
                qty = 0

        except IndexError:
            description, product_service, qty = "N/A", "N/A", 0

        # Retrieve unit price from predefined dictionary, or set to "N/A" if not found
        unit_price = product_details.get(product_service, "N/A")

        total_price = "N/A"
        if unit_price != "N/A" and qty > 0:
            total_price = qty * unit_price
            grand_total += total_price  # Add to grand total
            total_price = "{:.2f}".format(qty * unit_price)

        # Add each row to the PDF with right-aligned numeric columns
        pdf.set_x(5)
        pdf.cell(15, 10, str(i), 0, 0, 'C')
        pdf.cell(65, 10, description, 0, 0, 'L')
        pdf.cell(40, 10, product_service, 0, 0, 'L')
        pdf.cell(25, 10, str(unit_price), 0, 0, 'R')
        pdf.cell(25, 10, str(qty), 0, 0, 'C')
        pdf.cell(25, 10, str(total_price), 0, 1, 'R')

    # After the loop, print the total amount
    pdf.ln(5)  # Add space before total
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(170, 10, "Total Amount (HKD):", align='R')
    pdf.cell(21, 10, "{:.2f}".format(grand_total), align='R')
    

    # Add a new page with terms and conditions
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.set_xy(10, 95)
    pdf.cell(20, 10, "Terms & Conditions", align='L')

    # Output the PDF
    pdf.output(file_name)


# Streamlit UI
def main():
    st.set_page_config(page_title="Quote Generator", page_icon=":page_facing_up:")
    st.title("Quote Generator")
    st.caption("An Estimate & Quote Generator Powered by OpenAI.")
    
    sample_text = st.text_area("Enter Your Quote Details, Please Include Area, Product No./Service & Quantity.",
                           height=300)
                           
    if st.button("Generate Quote"):
        if sample_text:
            prompt_ExtractInfo = f"""
        
        For text: {sample_text}, please follow these steps and ONLY display the final extracted information as outlined below.

        1. Split texts into separate itemized quotes.
        Split the following string into separate itemized quotes based on distinct job descriptions.
        - Do NOT output the itemized quotes or any intermediary results. 
        - This step is only for internal processing.

        2. Extract information from each itemized quotes
        Extract the following information from the text and return it in the format: Area, Product No., QTY..
        - Ensure each entry is in the format: "Description: [simple description of this itemized quote in which area], Product No./Service: [product number|service name], QTY.: [quantity (digits)]."
        - If any piece of information (Description, Product No., QTY.) is missing, indicate it as "N/A".
 
        3. The final output should exclusively contain the extracted information formatted as: 
        "Description: [simple description of this itemized quote in which area], Product No.: [product number], QTY.: [quantity (digits)]".
        - Do NOT include any additional text, explanations, or itemized quotes from Step 1.

        """
            
            extracted_info = extract_information(prompt_ExtractInfo)

            # Validate the extracted areas
            validated_info = []
            for line in extracted_info.split('\n'):

                validated_info.append(line)

            validated_info_str = "\n".join(validated_info)

            # Display the validated information
            def calculate_height(validated_info_str):
                chars_per_line = 80
                total_chars = len(validated_info_str)
                line_count = (total_chars // chars_per_line) + validated_info_str.count('\n') + 1
                height = min(400, max(100, line_count *25))
                return height
        
            st.text_area("Itemized Quote(s)", 
                         validated_info_str, 
                         height=calculate_height(validated_info_str)
                         )

            file_name = "quote.pdf"

            generate_pdf(validated_info_str, file_name)
        
            with open(file_name, "rb") as file:
                st.download_button(label="Download PDF", data=file, file_name=file_name)

if __name__ == '__main__':
    main()