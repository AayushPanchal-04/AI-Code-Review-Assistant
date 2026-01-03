import streamlit as st
import requests
import json

# Page configuration
st.set_page_config(
    page_title="Code Review Assistant",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4F46E5;
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #4338CA;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🔍 Code Review Assistant")
st.markdown("Get AI-powered optimization and readability suggestions for your code")

# Sidebar for API Key and settings
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_key = st.text_input(
        "Groq API Key",
        type="password",
        help="Enter your Groq API key. Get one at https://console.groq.com"
    )
    
    st.markdown("---")
    
    model = st.selectbox(
        "Select Model",
        [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile", 
            "llama-3.1-8b-instant",
            "gemma2-9b-it"
        ],
        help="Choose the AI model for code review"
    )
    
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="Lower values = more focused, higher values = more creative"
    )
    
    st.markdown("---")
    st.markdown("""
    ### 📝 How to use:
    1. Enter your Groq API key
    2. Select programming language
    3. Paste your code
    4. Click 'Review Code'
    
    ### 🔑 Get API Key:
    Visit [console.groq.com](https://console.groq.com)
    """)

# Function to call Groq API
def review_code_with_groq(api_key, model, temperature, language, code):
    """Call Groq API to review code"""
    
    prompt = f"""You are an expert code reviewer with years of experience in software development.
Analyze the following {language} code and provide a comprehensive review.

Code to review:
```
{code}
```

Please provide your review in the following JSON format:
{{
    "overall_score": <score from 1-10>,
    "summary": "<brief summary of code quality>",
    "strengths": ["<strength 1>", "<strength 2>", ...],
    "quality_issues": [
        {{"issue": "<description>", "severity": "<high/medium/low>", "suggestion": "<how to fix>"}}
    ],
    "optimizations": [
        {{"current": "<what can be optimized>", "suggestion": "<better approach>", "benefit": "<why it's better>"}}
    ],
    "readability": [
        {{"issue": "<readability concern>", "suggestion": "<improvement>"}}
    ],
    "best_practices": [
        {{"practice": "<best practice to follow>", "reason": "<why it matters>"}}
    ],
    "security_concerns": ["<concern 1>", "<concern 2>", ...],
    "additional_notes": "<any other important observations>"
}}

Provide specific, actionable feedback. Be constructive and helpful."""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are an expert code reviewer. Provide detailed, constructive feedback."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": temperature,
        "max_tokens": 2000
    }
    
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        result = response.json()
        return result['choices'][0]['message']['content']
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📄 Your Code")
    
    language = st.selectbox(
        "Programming Language",
        ["Python", "JavaScript", "Java", "C++", "Go", "Ruby", "PHP", "TypeScript", "Rust", "C#", "Swift", "Kotlin"]
    )
    
    code_input = st.text_area(
        "Paste your code here",
        height=400,
        placeholder="def example():\n    # Your code here...",
        help="Paste the code you want to review"
    )
    
    review_button = st.button("🚀 Review Code", use_container_width=True)

with col2:
    st.subheader("✨ Review Results")
    results_container = st.container()

# Initialize session state for storing results
if 'review_results' not in st.session_state:
    st.session_state.review_results = None

# Code review logic
if review_button:
    if not api_key:
        st.error("❌ Please enter your Groq API key in the sidebar")
    elif not code_input.strip():
        st.error("❌ Please paste some code to review")
    else:
        with st.spinner("🔄 Analyzing your code..."):
            try:
                # Call Groq API
                response = review_code_with_groq(
                    api_key=api_key,
                    model=model,
                    temperature=temperature,
                    language=language,
                    code=code_input
                )
                
                # Try to parse JSON response
                try:
                    # Clean the response to extract JSON
                    response_clean = response.strip()
                    if response_clean.startswith("```json"):
                        response_clean = response_clean[7:]
                    if response_clean.startswith("```"):
                        response_clean = response_clean[3:]
                    if response_clean.endswith("```"):
                        response_clean = response_clean[:-3]
                    
                    review_data = json.loads(response_clean.strip())
                    st.session_state.review_results = review_data
                except json.JSONDecodeError:
                    # If JSON parsing fails, store raw response
                    st.session_state.review_results = {"raw_response": response}
                
                st.success("✅ Code review completed!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Make sure your API key is valid and you have credits available")

# Display results
with results_container:
    if st.session_state.review_results:
        results = st.session_state.review_results
        
        # Check if we have structured data or raw response
        if "raw_response" in results:
            st.markdown("### 📋 Review Feedback")
            st.markdown(results["raw_response"])
        else:
            # Display overall score
            if "overall_score" in results:
                score = results["overall_score"]
                col_a, col_b, col_c = st.columns([1, 2, 1])
                with col_b:
                    st.metric(
                        label="Overall Code Quality Score",
                        value=f"{score}/10",
                        delta=None
                    )
            
            # Display summary
            if "summary" in results:
                st.markdown(f"**Summary:** {results['summary']}")
                st.markdown("---")
            
            # Display strengths
            if "strengths" in results and results["strengths"]:
                with st.expander("💪 Strengths", expanded=True):
                    for strength in results["strengths"]:
                        st.success(f"✓ {strength}")
            
            # Display quality issues
            if "quality_issues" in results and results["quality_issues"]:
                with st.expander("⚠️ Quality Issues", expanded=True):
                    for issue in results["quality_issues"]:
                        severity = issue.get("severity", "medium").upper()
                        color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
                        st.warning(f"{color.get(severity, '🟡')} **{severity}**: {issue['issue']}")
                        st.info(f"💡 Suggestion: {issue['suggestion']}")
                        st.markdown("---")
            
            # Display optimizations
            if "optimizations" in results and results["optimizations"]:
                with st.expander("⚡ Optimization Suggestions", expanded=True):
                    for opt in results["optimizations"]:
                        st.markdown(f"**Current:** {opt['current']}")
                        st.success(f"**Better Approach:** {opt['suggestion']}")
                        st.info(f"**Benefit:** {opt['benefit']}")
                        st.markdown("---")
            
            # Display readability improvements
            if "readability" in results and results["readability"]:
                with st.expander("📖 Readability Improvements", expanded=True):
                    for item in results["readability"]:
                        st.markdown(f"**Issue:** {item['issue']}")
                        st.success(f"**Suggestion:** {item['suggestion']}")
                        st.markdown("---")
            
            # Display best practices
            if "best_practices" in results and results["best_practices"]:
                with st.expander("✅ Best Practices", expanded=True):
                    for practice in results["best_practices"]:
                        st.markdown(f"**Practice:** {practice['practice']}")
                        st.info(f"**Why it matters:** {practice['reason']}")
                        st.markdown("---")
            
            # Display security concerns
            if "security_concerns" in results and results["security_concerns"]:
                with st.expander("🔒 Security Concerns", expanded=False):
                    for concern in results["security_concerns"]:
                        st.error(f"⚠️ {concern}")
            
            # Display additional notes
            if "additional_notes" in results and results["additional_notes"]:
                with st.expander("📝 Additional Notes", expanded=False):
                    st.info(results["additional_notes"])
    else:
        st.info("👈 Paste your code and click 'Review Code' to get started")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6B7280; padding: 1rem;'>
    <p>Powered by Groq API • Built with Streamlit</p>
    <p style='font-size: 0.875rem;'>Get your free Groq API key at <a href='https://console.groq.com' target='_blank'>console.groq.com</a></p>
</div>
""", unsafe_allow_html=True)