import os
import streamlit as st
from langchain_openai import OpenAI
from pdf_format import generate_pdf


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



# Streamlit UI
def main():
    st.set_page_config(page_title="Quote Generator", page_icon=":page_facing_up:")
    st.title("Quote Generator")
    st.caption("An Estimate & Quote Generator Powered by OpenAI.")
    
    sample_text = st.text_area("Enter Your Quote Details, Please Specifically Include Product No./Service & Quantity.",
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