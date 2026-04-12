import streamlit as st
import pandas as pd
from model_bridge import generate_report

st.set_page_config(layout="wide", page_title="SOC Auto-Completion UI")
st.title("🛡️ Context-Aware Incident Report Auto-Completion")

# 1. Load BOTH datasets into memory efficiently
@st.cache_data
def load_datasets():
    # Load the raw data for Panels 1 & 2
    df_splits = pd.read_csv("data/splits/test.csv")
    
    # Load the formatted inputs for the Model (Panel 3)
    df_model = pd.read_csv("data/model_ready/test.csv")
    
    # Create the clean dropdown label exactly as you requested (ID - Type)
    df_splits['dropdown_label'] = df_splits['incident_id'].astype(str) + " - " + df_splits['incident_type'].astype(str)
    
    return df_splits, df_model

df_splits, df_model = load_datasets()

# 2. Setup the Dropdown
# Convert the labels to a list for the selectbox
options = df_splits['dropdown_label'].tolist()
selected_label = st.selectbox("Select an Incident to Analyze:", options)

# Format the output text
def format_report(text):
    # Normalize spacing
    text = text.replace("Root Cause:", "\nRoot Cause:\n")
    text = text.replace("Resolution:", "\nResolution:\n")
    text = text.replace("Preventive Action:", "\nPreventive Action:\n")

    # Remove extra spaces at start of lines
    lines = [line.strip() for line in text.split("\n")]

    # Add spacing after each section
    formatted = ""
    for line in lines:
        if line in ["Root Cause:", "Resolution:", "Preventive Action:"]:
            formatted += f"\n{line}\n"
        elif line != "":
            formatted += f"{line}\n\n"   # 👈 adds space after each sentence

    return formatted.strip()


if st.button("Run Preprocessing & NLP Pipeline"):
    
    # 3. Find the critical Index (i)
    selected_index = df_splits[df_splits['dropdown_label'] == selected_label].index[0]
    
    # 4. Extract data using the index
    raw_data = df_splits.iloc[selected_index]
    model_input_text = df_model.iloc[selected_index]['input_text']
    
    # --- NEW: Grab the ground truth just in case ---
    ground_truth_report = df_model.iloc[selected_index]['target_text']
    
    # 5. Run Live Inference with Graceful Fallback
    with st.spinner('Running Stage 1 Normalization and FLAN-T5 Inference...'):
        try:
            # Attempt to hit the local FLAN-T5 model
            live_model_output = generate_report(model_input_text)
            st.success("Pipeline execution complete! (Live Inference)")
            
        except Exception as e:
            # If the model crashes, times out, or fails for any reason
            st.warning(f"Live model unavailable. Displaying Ground Truth data. (Error: {e})")
            live_model_output = ground_truth_report
            
    # --- Three-Panel Layout ---
    col1, col2, col3 = st.columns(3)

    # PANEL 1: Raw Inputs from df_splits
    with col1:
        st.header("1. Raw Inputs")
        st.text_area("System Logs", raw_data.get('logs', 'N/A'), height=150, disabled=True)
        st.text_area("Chat Transcripts", raw_data.get('chat_transcript', 'N/A'), height=150, disabled=True)
        st.text_area("Executed Commands", raw_data.get('commands_executed', 'N/A'), height=80, disabled=True)

    # PANEL 2: Stage 1 JSON from df_splits
    with col2:
        st.header("2. Pipeline Output")
        st.caption("Clean, structured JSON representation (Stage 1).")
        import json
        try:
            parsed_json = json.loads(raw_data.get('stage1_json', '{}'))
            st.json(parsed_json)
        except:
            st.code(raw_data.get('stage1_json', 'N/A'))

    # PANEL 3: Live Output from our Model Bridge
    with col3:
        st.header("3. Auto-Completed Report")
        st.caption("NLP-driven insights directly from FLAN-T5 (or Ground Truth fallback).")
        st.text_area("✨ Model Output ✨", format_report(live_model_output), height=350)

    # --- Export Functionality ---
        # --- Export Functionality ---
    st.divider()
    st.subheader("📥 Export Final Report")

    import json

    logs_text = raw_data.get("logs", "N/A")
    chat_text = raw_data.get("chat_transcript", "N/A")
    commands_text = raw_data.get("commands_executed", "N/A")

    # stage1_json_raw = raw_data.get("stage1_json", "{}")
    # try:
    #     parsed_stage1 = json.loads(stage1_json_raw)
    #     stage1_pretty = json.dumps(parsed_stage1, indent=4)
    # except Exception:
    #     stage1_pretty = str(stage1_json_raw)

    report_text = f"""
=========================================
INCIDENT REPORT: {selected_label.upper()}
=========================================

1. RAW INPUTS
-----------------------------------------
System Logs:
{logs_text}

Chat Transcripts:
{chat_text}

Executed Commands:
{commands_text}

3. MODEL INFERENCE / REPORT
-----------------------------------------
{format_report(live_model_output)}
"""

    st.download_button(
        label="Download Report as TXT",
        data=report_text,
        file_name=f"{selected_label}_full_report.txt",
        mime="text/plain"
    )

    # c:\AIG_Sem2\NLP\LAB\aig230_assignment1_Shrunga\aig230-env\Scripts\streamlit.exe run src/model_app.py