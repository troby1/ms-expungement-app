import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import os
import datetime
import uuid

# === CONFIG ===
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="MS Expungement Decider", layout="centered")
st.title("⚖️ Mississippi Expungement Decider")
st.write("This tool checks whether your record may be eligible for expungement under Mississippi law.")

# --- Form Inputs ---
with st.form("expungement_form"):
    charge = st.text_input("Charge (e.g., Shoplifting, DUI, Assault)")
    offense_type = st.selectbox("Offense Type", ["Misdemeanor", "Felony"])
    convicted = st.radio("Were you convicted?", ["Yes", "No"])
    sentence_completed = st.date_input("Date Sentence Completed")
    first_offense = st.radio("Is this your first offense?", ["Yes", "No"])
    county = st.text_input("County of Offense")
    age = st.number_input("Your age at the time of offense", min_value=10, max_value=100)
    submitted = st.form_submit_button("Check Eligibility")

if submitted:
    st.info("Analyzing your eligibility...")

    # Build prompt
    user_info = f"""
Charge: {charge}
Type: {offense_type}
Convicted: {convicted}
Date Sentence Completed: {sentence_completed}
First Offense: {first_offense}
County: {county}
Age at Time: {age}
"""
    prompt = f"""
You are an expungement eligibility assistant for Mississippi law.
Using MS Code § 99-19-71 and related rules, evaluate the following record:
{user_info}

Return:
1. Whether the offense is eligible for expungement
2. If not, any possible workarounds
3. Earliest eligibility date
4. Required documents
5. Court/jurisdiction
6. A plain-language summary with a disclaimer that this is not legal advice
Respond in markdown.
"""

    # Run GPT
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a legal assistant that helps users understand expungement eligibility under Mississippi law."},
            {"role": "user", "content": prompt}
        ]
    )
    result = response.choices[0].message.content
    st.markdown(result)

    # --- Generate unique PDF summary ---
    file_id = str(uuid.uuid4())[:8]
    filename = f"expungement_summary_{file_id}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Expungement Summary for {charge}\n\n{result}")
    pdf.output(filename)

    with open(filename, "rb") as f:
        st.download_button("📥 Download Expungement Summary (PDF)", f, file_name=filename)

    st.success("Analysis complete. Summary saved with ID: " + file_id)
