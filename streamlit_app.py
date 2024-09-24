import os
import streamlit as st
from langchain_openai import OpenAI
from fpdf import FPDF

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'


# Predefined products and their unit prices
product_prices = {
    'SIEMENS IMA1608': 50.00,
    'Whirlpool SCEBM0401MT': 60.00,
    'SCEBM0402MT': 55.00,
    'TMCDH0904': 45.00,
    'SIEMENS LU83S750HK': 4000.00,
}

# Define valid areas
valid_areas = ['kitchen wall', 'kitchen floor', 'kitchen sink', 'kitchen',
               'bathroom wall', 'bathroom floor', 'bathroom counter top', 'bathroom',
               'full house floor', 'full house', 
               'living room', 'entrance']

def validate_area(area):
    if area.lower() in valid_areas:
        return area
    else:
        return "Invalid Area"


# ----------------------PDF generation function----------------------
def generate_pdf(quote_info, file_name):
    pdf = FPDF()
    pdf.add_page()

    # Set title and header with improved formatting
    pdf.set_font("Arial", style='B', size=20)
    pdf.cell(200, 10, txt="Quote Summary", ln=True, align="C")
    pdf.ln(10)

    # Add company or contact information
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Company Name: Example Corp.", ln=True, align="C")
    pdf.cell(200, 10, "Address: 123 Example St., City, Country", ln=True, align="C")
    pdf.cell(200, 10, "Contact: +123 456 789", ln=True, align="C")
    pdf.ln(10)

    # Add date or reference number
    pdf.cell(100, 10, "Date: 23-Sep-2024", ln=True)
    pdf.cell(100, 10, "Reference No: HQ240949FTS-00", ln=True)
    pdf.ln(10)

    # Set table headers with background color
    pdf.set_fill_color(200, 200, 200)  # Light gray background for headers
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(40, 10, "Area", 1, 0, 'C', fill=True)
    pdf.cell(60, 10, "Product No./Service", 1, 0, 'C', fill=True)
    pdf.cell(20, 10, "QTY", 1, 0, 'C', fill=True)
    pdf.cell(30, 10, "Unit Price", 1, 0, 'C', fill=True)
    pdf.cell(30, 10, "Total Price", 1, 1, 'C', fill=True)
    pdf.ln(5)

    # Set content font
    pdf.set_font("Arial", size=12)

    # Loop through each quote line and add to table with improved formatting
    for line in quote_info.split('\n'):
        parts = line.split(', ')

        # Ensure there are enough parts in the line (handle missing data)
        if len(parts) < 4:
            continue

        try:
            area = parts[0].split(': ')[1].strip() if len(parts) > 0 and ': ' in parts[0] else "N/A"
            product_service = parts[1].split(': ')[1].strip() if len(parts) > 1 and ': ' in parts[1] else "N/A"
            qty_str = parts[2].split(': ')[1].strip() if len(parts) > 2 and ': ' in parts[2] else "N/A"

            # Ensure the quantity is numeric and handle invalid quantities
            try:
                qty = float(qty_str)
            except ValueError:
                qty = 0  # Default to 0 if quantity is invalid or "N/A"
            
        except IndexError:
            area, product_service, qty = "N/A", "N/A", 0

        # Validate area before adding to PDF
        area = validate_area(area)

        # Retrieve unit price from predefined dictionary, or set to "N/A" if not found
        unit_price = product_prices.get(product_service, "N/A")

        total_price = "N/A"
        if unit_price != "N/A" and qty > 0:
            total_price = "{:.2f}".format(qty * unit_price)

        # Add each row to the PDF with right-aligned numeric columns
        pdf.cell(40, 10, area, 1, 0, 'C')
        pdf.cell(60, 10, product_service, 1, 0, 'L')  # Left-align the service/product column
        pdf.cell(20, 10, str(qty), 1, 0, 'R')  # Right-align for quantity
        pdf.cell(30, 10, str(unit_price), 1, 0, 'R')  # Right-align for unit price
        pdf.cell(30, 10, str(total_price), 1, 1, 'R')  # Right-align for total price
        pdf.ln(5)

    # Footer (Optional)
    pdf.set_y(-30)  # Position at 30 mm from bottom
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, 'Thank you for your business!', 0, 0, 'C')
    pdf.cell(0, 10, 'Page %s' % pdf.page_no(), 0, 0, 'R')  # Add page numbers

    # Output PDF
    pdf.output(file_name)


# ----------------------LLM function----------------------
def extract_information(prompt_ExtractInfo):
    llm = OpenAI(
        model_name="gpt-3.5-turbo-instruct",
        temperature=0,
        max_tokens=500
    )
    response = llm.generate([prompt_ExtractInfo])
    return response.generations[0][0].text.strip()

# ----------------------Streamlit UI----------------------
def main():
    st.set_page_config(page_title="Quote Generator", page_icon=":page_facing_up:")
    st.title("Quote Generator")
    st.caption("An Estimate & Quote Generator Powered by OpenAI.")
    
    sample_text = st.text_area("Enter Your Quote Details, Please Include Area, Product No./Service, Quantity, Unit Price.",
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
        Extract the following information from the text and return it in the format: Area, Product/Service, QTY., Total Price.
        - Ensure each entry is in the format: "Area: [area], Product No./Service: [product number|service name], QTY.: [quantity], Unit Price:[unit price], Total Price: [total price]."
        - If any piece of information (Area, Product No./Service, QTY., unit price, total price) is missing, indicate it as "N/A".
        - Ensure the area is one of the valid areas: {', '.join(valid_areas)}. If not, mark it as "Invalid Area".

        3. The final output should exclusively contain the extracted information formatted as: 
        "Area: [area], Product No./Service: [product number], QTY.: [quantity], Unit Price:[unit price], Total Price: [total price]".
        - List the results numerically.
        - Do NOT include any additional text, explanations, or itemized quotes from Step 1.

        """
            
            extracted_info = extract_information(prompt_ExtractInfo)

            # Additional check to remove any intermediary text (e.g., if model didn't follow prompt)
            if "itemized" in extracted_info.lower() or "step" in extracted_info.lower():
                extracted_info = "\n".join(
                    [line for line in extracted_info.splitlines() if not ("itemized" in line.lower() or "step" in line.lower())]
                    )

            # Validate the extracted areas
            validated_info = []
            for line in extracted_info.split('\n'):
                if "Area:" in line:
                    try:
                        # Safely extract and validate the area
                        area_part = line.split('Area:')[1].split(',')[0].strip()
                        valid_area = validate_area(area_part)
                        # Replace the area part with the validated one
                        line = line.replace(area_part, valid_area)
                    except IndexError:
                        line = "Invalid Format: Missing Area Information"
            
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
