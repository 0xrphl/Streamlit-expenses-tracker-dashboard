def get_custom_css():
    """Return custom CSS for the dashboard."""
    return """
    <style>
    /* Main app styling */
    .stApp { 
        color: #e8e8e8;
        background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%);
    }
    
    /* Metric styling */
    .stMetric {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a7b 100%);
        padding: 12px;
        border-radius: 10px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .stMetricLabel, .stMetricDelta, .st-emotion-cache-1xarl3l, .st-emotion-cache-10trblm { 
        color: #e8e8e8 !important;
        font-weight: 600;
        font-size: 0.9rem !important;
    }
    
    .stMetricValue {
        font-size: 1.3rem !important;
    }
    
    .st-emotion-cache-1v0mbdj svg text { 
        fill: #e8e8e8 !important; 
    }
    
    /* Header styling */
    h1 {
        background: linear-gradient(90deg, #3b82f6 0%, #2dd4bf 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 1.8rem !important;
        margin-bottom: 0.3rem !important;
    }
    
    h2 {
        color: #3b82f6;
        font-weight: 600;
        font-size: 1.3rem !important;
        margin-top: 0.8rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h3 {
        color: #3b82f6;
        font-weight: 600;
        font-size: 1.1rem !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.3rem !important;
    }
    
    /* Caption/subtitle styling */
    .stMarkdown p {
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1e 100%);
        border-right: 2px solid rgba(59, 130, 246, 0.3);
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Card-like containers */
    .element-container {
        transition: all 0.3s ease;
    }
    
    /* Custom divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #3b82f6 50%, transparent 100%);
        margin: 2rem 0;
    }
    </style>
    """
