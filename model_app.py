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

# if st.button("Run Preprocessing & NLP Pipeline"):
    
#     # 3. Find the critical Index (i)
#     # Get the exact index of the row the user selected
#     selected_index = df_splits[df_splits['dropdown_label'] == selected_label].index[0]
    
#     # 4. Extract data using the index
#     raw_data = df_splits.iloc[selected_index]
#     model_input_text = df_model.iloc[selected_index]['input_text']
    
#     # 5. Run Live Inference ONLY on the selected row
#     with st.spinner('Running Stage 1 Normalization and FLAN-T5 Inference...'):
#         live_model_output = generate_report(model_input_text)
        
#     st.success("Pipeline execution complete!")
    
#     # --- Three-Panel Layout ---
#     col1, col2, col3 = st.columns(3)

#     # PANEL 1: Raw Inputs from df_splits
#     with col1:
#         st.header("1. Raw Inputs")
#         st.text_area("System Logs", raw_data.get('logs', 'N/A'), height=100, disabled=True)
#         st.text_area("Chat Transcripts", raw_data.get('chat_transcript', 'N/A'), height=100, disabled=True)
#         st.text_area("Executed Commands", raw_data.get('commands_executed', 'N/A'), height=80, disabled=True)

#     # PANEL 2: Stage 1 JSON from df_splits
#     with col2:
#         st.header("2. Pipeline Output")
#         st.caption("Clean, structured JSON representation (Stage 1).")
#         # Ensure it reads the string as JSON for pretty-printing if it's stored as a string in the CSV
#         import json
#         try:
#             parsed_json = json.loads(raw_data.get('stage1_json', '{}'))
#             st.json(parsed_json)
#         except:
#             st.code(raw_data.get('stage1_json', 'N/A'))

#     # PANEL 3: Live Output from our Model Bridge
#     with col3:
#         st.header("3. Auto-Completed Report")
#         st.caption("NLP-driven insights directly from FLAN-T5.")
#         st.text_area("✨ Model Output ✨", live_model_output, height=350)

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
        st.text_area("✨ Model Output ✨", live_model_output, height=350)

    # --- Export Functionality ---
    st.divider()
    st.subheader("📥 Export Final Report")
    
    report_text = f"""
    =========================================
    INCIDENT REPORT: {selected_label.upper()}
    =========================================

    MODEL INFERENCE / REPORT:
    {live_model_output}
    """

    st.download_button(
        label="Download Report as TXT",
        data=report_text,
        file_name=f"{selected_label}_report.txt",
        mime="text/plain"
    )

else:
    st.info("Select an incident and click the button to run the pipeline.")

    # Format the report text
    # report_text = f"""
    # =========================================
    # INCIDENT REPORT: {mock_incident['stage1_json']['incident_id']}
    # SEVERITY: {mock_incident['stage2_predictions']['severity']}
    # =========================================

    # SUMMARY:
    # {mock_incident['stage2_predictions']['summary']}

    # ROOT CAUSE: 
    # Brute Force Authentication Attempt

    # RESOLUTION STEPS:
    # """
    # for step in mock_incident['stage1_json']['resolution_steps']:
    #     report_text += f"\t- {step}\n"

    # report_text += f"\nPREVENTIVE ACTIONS:\n{mock_incident['stage2_predictions']['recommended_prevention']}"

    # # The Download Button
    # st.download_button(
    #     label="Download Report as TXT",
    #     data=report_text,
    #     file_name=f"{mock_incident['stage1_json']['incident_id']}_report.txt",
    #     mime="text/plain"
    # )