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

# Define valid areas
valid_areas = ['kitchen wall', 'kitchen floor', 'kitchen sink', 'kitchen',
               'bathroom wall', 'bathroom floor', 'bathroom counter top', 'bathroom',
               'full house floor', 'full house', 
               'living room', 'entrance']

# Validate areas
def validate_area(area):
    if area.lower() in valid_areas:
        return area
    else:
        return "Invalid Area"

# PDF generation function
def generate_pdf(quote_info, file_name):
    pdf = FPDF()
    pdf.add_page()

    # Set title and header
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, txt="Quote Summary", ln=True, align="C")
    pdf.ln(10)

    # Set table headers
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(40, 10, "Area", 1, 0, 'C')
    pdf.cell(60, 10, "Product No./Service", 1, 0, 'C')
    pdf.cell(20, 10, "QTY.", 1, 0, 'C')
    pdf.cell(30, 10, "Total Price", 1, 1, 'C')
    pdf.ln(5)

    # Set content font
    pdf.set_font("Arial", size=12)

    # Loop through each quote line and add to table
    for line in quote_info.split('\n'):
        parts = line.split(', ')

        # Check if there are enough parts for each field (Area, Product No./Service, QTY, Total Price)
        area = parts[0].split(': ')[1] if len(parts) > 0 and ': ' in parts[0] else "N/A"
        product_service = parts[1].split(': ')[1] if len(parts) > 1 and ': ' in parts[1] else "N/A"
        qty = parts[2].split(': ')[1] if len(parts) > 2 and ': ' in parts[2] else "N/A"
        total_price = parts[3].split(': ')[1] if len(parts) > 3 and ': ' in parts[3] else "N/A"

        # Validate area before adding to PDF
        area = validate_area(area)

        # Add each row to PDF
        pdf.cell(40, 10, area, 1, 0, 'C')
        pdf.cell(60, 10, product_service, 1, 0, 'C')
        pdf.cell(20, 10, qty, 1, 0, 'C')
        pdf.cell(30, 10, total_price, 1, 1, 'C')
        pdf.ln(5)

    # Output PDF
    pdf.output(file_name)

# Streamlit UI
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
        - Ensure each entry is in the format: "Area: [area], Product No./Service: [product number|service name], QTY.: [quantity], Total Price: [total price]."
        - If any piece of information (Area, Product No./Service, QTY., total price) is missing, indicate it as "N/A".
        - Ensure the area is one of the valid areas: {', '.join(valid_areas)}. If not, mark it as "Invalid Area".

        3. The final output should exclusively contain the extracted information formatted as: 
        "Area: [area], Product No./Service: [product number], QTY.: [quantity], Total Price: [total price]".
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
