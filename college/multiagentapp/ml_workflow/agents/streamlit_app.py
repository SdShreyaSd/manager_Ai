import os
import streamlit as st
from dotenv import load_dotenv
import logging
import pandas as pd
import json

# Import Web Flow Agents
from requirements_agent import RequirementsAgent
from design_agent import create_design
from coder_agent import CoderAgent
from deploy_agent import parse_and_save_coder_output

# Import ML Flow Agents
from data_agent import DataAgent
from model_agent import MLModelAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize session states
if 'server_process' not in st.session_state:
    st.session_state.server_process = None
if 'current_flow' not in st.session_state:
    st.session_state.current_flow = None
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'data_info' not in st.session_state:
    st.session_state.data_info = None
if 'preprocessed_data' not in st.session_state:
    st.session_state.preprocessed_data = None
if 'requirements_analysis' not in st.session_state:
    st.session_state.requirements_analysis = None
if 'model_results' not in st.session_state:
    st.session_state.model_results = None

# Page config
st.set_page_config(page_title="Multi-Agent Development System", layout="wide")
st.title("Multi-Agent Development System")

# Flow Selection
flow_type = st.radio(
    "Select Development Flow:",
    ["ML Development", "Web Development"],
    help="Choose between ML model development or web application development"
)

st.session_state.current_flow = flow_type

# Sidebar for model selection
st.sidebar.title("Model Selection")
if flow_type == "Web Development":
    st.sidebar.write("Select models for each agent (except Coder Agent which uses Blackbox.ai)")
else:
    st.sidebar.write("Select models for ML development agents")

# Model selection options
model_options = [
    "llama3-8b-8192",
    "Groq/Llama-3-Groq-8B-Tool-Use",
    "Groq/Llama-3-Groq-70B-Tool-Use",
    "HF/mistralai/Mixtral-8x7B-Instruct-v0.1"
]

if flow_type == "ML Development":
    # ML Flow Implementation
    st.write(
        "Enter your ML project requirements and upload your data. "
        "The system will analyze requirements, process data, and develop models."
    )
    
    # ML Flow model selection
    req_model = st.sidebar.selectbox("Requirements Agent Model:", model_options, index=0)
    
    # Initialize ML agents
    data_agent = DataAgent()
    requirements_agent = RequirementsAgent()
    model_agent = MLModelAgent()

    # Data Upload Section
    st.subheader("1. Data Upload and Processing")
    uploaded_file = st.file_uploader(
        "Upload your dataset (CSV, Excel)", 
        type=['csv', 'xlsx', 'xls'],
        help="Upload the dataset you want to analyze"
    )

    if uploaded_file:
        try:
            # Load and display data preview
            if uploaded_file.name.endswith('.csv'):
                data = pd.read_csv(uploaded_file)
            else:
                data = pd.read_excel(uploaded_file)
            
            st.session_state.uploaded_data = data
            
            # Display data preview
            st.write("Data Preview:")
            st.dataframe(data.head())
            
            # Process data and store info
            st.session_state.data_info = {
                "rows": len(data),
                "columns": len(data.columns),
                "column_types": data.dtypes.astype(str).to_dict(),
                "missing_values": data.isnull().sum().to_dict(),
                "numeric_columns": data.select_dtypes(include=['int64', 'float64']).columns.tolist(),
                "categorical_columns": data.select_dtypes(include=['object']).columns.tolist()
            }
            
            # Display data info
            st.write("Dataset Information:")
            st.json(st.session_state.data_info)
            
        except Exception as e:
            st.error(f"Error reading data: {str(e)}")

    # Requirements Input Section
    st.subheader("2. Project Requirements")
    target_column = None
    if st.session_state.uploaded_data is not None:
        target_column = st.selectbox(
            "Select Target Column:",
            st.session_state.uploaded_data.columns.tolist(),
            help="Select the column you want to predict"
        )

    prompt = st.text_area(
        "Enter your ML project requirements:",
        height=150,
        help="Describe your ML project goals and requirements"
    )

    # Process button for ML Flow
    if st.button("Generate ML Model"):
        if not prompt:
            st.error("Please enter project requirements.")
        elif st.session_state.uploaded_data is None:
            st.error("Please upload your dataset.")
        elif target_column is None:
            st.error("Please select a target column.")
        else:
            try:
                # 1. Data Processing
                with st.expander("1. Data Processing", expanded=True):
                    st.write("📊 Processing data...")
                    processed_data = data_agent.preprocess_data(
                        st.session_state.uploaded_data.copy(),
                        target_column
                    )
                    st.session_state.preprocessed_data = processed_data
                    st.write("✅ Data processing complete!")

                # 2. Requirements Analysis
                with st.expander("2. Requirements Analysis", expanded=True):
                    st.write("🔍 Analyzing requirements...")
                    # Include data info in requirements analysis
                    full_prompt = f"""
                    Project Requirements: {prompt}
                    
                    Dataset Information:
                    {json.dumps(st.session_state.data_info, indent=2)}
                    
                    Target Column: {target_column}
                    """
                    requirements = requirements_agent.analyze_requirements(full_prompt, req_model)
                    st.session_state.requirements_analysis = requirements
                    st.markdown(requirements)

                # 3. Model Development
                if st.session_state.preprocessed_data and st.session_state.requirements_analysis:
                    with st.expander("3. Model Development", expanded=True):
                        st.write("🤖 Training and evaluating model...")
                        # Determine if classification or regression
                        is_classification = st.session_state.uploaded_data[target_column].dtype == 'object' or \
                                         len(st.session_state.uploaded_data[target_column].unique()) < 10
                        
                        model_results = model_agent.train_and_evaluate(
                            st.session_state.preprocessed_data,
                            target_column,
                            'classification' if is_classification else 'regression'
                        )
                        
                        st.session_state.model_results = model_results
                        
                        # Display metrics
                        st.write("Model Performance Metrics:")
                        st.json(model_results['metrics'])
                        
                        # Display feature importance
                        st.write("Feature Importance:")
                        st.json(model_results['feature_importance'])
                        
                        # Display best parameters
                        st.write("Best Model Parameters:")
                        st.json(model_results['best_params'])

            except Exception as e:
                st.error(f"Error in workflow: {str(e)}")
                logger.error(f"Error in workflow: {str(e)}", exc_info=True)

else:  # Web Development Flow
    st.write(
        "Enter your website requirements below. The system will analyze requirements, "
        "create a design specification, generate code using Blackbox.ai, and deploy the result."
    )
    
    # Web Flow model selection
    req_model = st.sidebar.selectbox("Requirements Agent Model:", model_options, index=0)
    design_model = st.sidebar.selectbox("Design Agent Model:", model_options, index=0)
    
    # Initialize Web agents
    requirements_agent = RequirementsAgent()
    coder_agent = CoderAgent()
    # Input prompt for Web Flow
    prompt = st.text_area(
        "Enter your website requirements:",
        height=150,
        help="Describe your desired website, including layout, features, and design preferences"
    )

    # Process button for Web Flow
    if st.button("Generate Website"):
        if not prompt:
            st.error("Please enter website requirements.")
        else:
            try:
                # 1. Requirements Analysis
                with st.expander("1. Requirements Analysis", expanded=True):
                    st.write("🔍 Analyzing requirements...")
                    requirements = requirements_agent.analyze_requirements(prompt, req_model)
                    st.markdown(requirements)

                # 2. Design Specification
                with st.expander("2. Design Specification", expanded=True):
                    st.write("🎨 Creating design specification...")
                    design = create_design(requirements, design_model)
                    st.markdown(design)

                # 3. Code Generation
                with st.expander("3. Code Generation", expanded=True):
                    st.write("💻 Generating code using Blackbox.ai...")
                    code = coder_agent.generate_code(design)
                    st.code(code)

                # 4. Deployment
                with st.expander("4. Deployment", expanded=True):
                    st.write("🚀 Deploying website...")
                    deployment_result = parse_and_save_coder_output(code)
                    st.success(deployment_result)

            except Exception as e:
                st.error(f"Error in workflow: {str(e)}")
                logger.error(f"Error in workflow: {str(e)}", exc_info=True) 