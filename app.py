import streamlit as st
import random
from utils.scraper import scrape_url
from utils.llm_engine import analyze_text
from datasets import load_dataset
from dotenv import load_dotenv
import re

# Load env variables (for local dev)
load_dotenv()

# --- Page Config ---
st.set_page_config(page_title="Green-Truth Auditor", page_icon="🌿", layout="wide")

st.title("🌿 Green-Truth Auditor")
st.markdown("Instantly detect greenwashing and evaluate the actual sustainability of a product or brand.")

# --- Sidebar (Dataset Logic) ---
with st.sidebar:
    st.header("Hackathon Tools")
    st.write("Want to test a real-world example instantly? Pull from the `Emanuse/greenwashing` dataset!")
    
    # Cache dataset loading so it doesn't block the UI unnecessarily on rerun
    @st.cache_data
    def get_dataset_samples():
        try:
            ds = load_dataset("Emanuse/greenwashing", split="train")
            # Pull a few rows
            return ds.select(range(min(100, len(ds)))) 
        except Exception as e:
            return None
    
    ds_samples = get_dataset_samples()
    
    if st.button("Surprise Me! 🎲"):
        if ds_samples is not None:
            random_sample = ds_samples[random.randint(0, len(ds_samples)-1)]
            # We assume the column is named 'text'
            st.session_state["demo_text"] = random_sample.get("text", str(random_sample))
        else:
            st.error("Could not load HuggingFace dataset.")

# --- Main UI ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Input Data")
    
    input_type = st.radio("What do you want to analyze?", ["Text Description", "Website URL"])
    
    user_text = ""
    user_url = ""
    
    if input_type == "Text Description":
        default_val = st.session_state.get("demo_text", "")
        user_text = st.text_area("Product Description:", value=default_val, height=200, placeholder="Paste product marketing copy here...")
    else:
        user_url = st.text_input("Product URL:", placeholder="https://example.com/product/eco-shoes")

    analyze_clicked = st.button("Run Audit", type="primary")

with col2:
    st.subheader("Audit Results")
    
    if analyze_clicked:
        with st.spinner("Analyzing claims..."):
            target_text = ""
            if input_type == "Text Description" and user_text:
                target_text = user_text
            elif input_type == "Website URL" and user_url:
                with st.spinner("Scraping URL..."):
                    target_text = scrape_url(user_url)
                    if not target_text:
                        st.error("Could not extract text from that URL. Try pasting the text directly.")
            else:
                st.warning("Please provide input text or a URL.")
            
            if target_text:
                try:
                    result = analyze_text(target_text)
                    if not result:
                        st.error("Analysis failed. Check your API key or input.")
                    else:
                        st.success("Audit Complete!")
                        
                        score = result.get("score", 0)
                        classification = result.get("classification", "Unknown")
                        buzzwords = result.get("buzzwords", [])
                        explanation = result.get("explanation", "")
                        
                        st.markdown("### 📊 Trust Breakdown")
                        breakdown = result.get("trust_breakdown", {})
                        
                        def render_row(label, val):
                            icon = "✔" if val >= 0 else "❌"
                            color = "green" if val >= 0 else "red"
                            sign = "+" if val >= 0 else ""
                            st.markdown(f"**{label}** <span style='float:right; color:{color};'>{icon} {sign}{val}</span>", unsafe_allow_html=True)
                        
                        col_bd_1, col_bd_2 = st.columns([1, 1])
                        with col_bd_1:
                            render_row("Certifications", breakdown.get("certs", 0))
                            render_row("Measurable Data", breakdown.get("numbers", 0))
                            render_row("Supply Chain", breakdown.get("supply", 0))
                            render_row("Audits/Third-Party", breakdown.get("third", 0))
                        with col_bd_2:
                            render_row("Vague Claims", breakdown.get("vague", 0))
                            render_row("Lack of Evidence", breakdown.get("no_evidence", 0))
                            render_row("Lifecycle Data", breakdown.get("lifecycle", 0))
                            
                        st.markdown("---")
                        
                        badge_color = "red" if "Fluff" in classification else "green"
                        st.markdown(f"### Final Score: `{score}/100` &nbsp; | &nbsp; Classification: <span style='color:{badge_color}'>{classification}</span>", unsafe_allow_html=True)
                        
                        st.info(f"**Explanation:** {explanation}")
                        
                        if score < 50:
                            st.error("🧾 **Recommendation:** Add recognized certifications or measurable data to improve credibility.")
                        else:
                            st.success("🧾 **Recommendation:** Good job providing evidence. Continue to maintain transparency.")
                        
                        st.subheader("Detected Signals")
                        if buzzwords:
                            st.markdown("**Buzzwords:** " + ", ".join([f"`{bw}`" for bw in buzzwords]))
                        
                        strong_signals = result.get("strong_signals", [])
                        if strong_signals:
                            st.markdown("**Verified Signals:** " + ", ".join([f"`{ss.split(':')[0]}`" for ss in strong_signals]))
                            
                            st.markdown("### Parsed Text (Highlighted)")
                            highlighted_text = target_text
                            for bw in buzzwords:
                                regex = re.compile(re.escape(bw), re.IGNORECASE)
                                highlighted_text = regex.sub(f"<span style='color:red; font-weight:bold;'>{bw}</span>", highlighted_text)
                            
                            if len(highlighted_text) > 2000:
                                highlighted_text = highlighted_text[:2000] + "...(truncated)"
                            st.markdown(f"<div style='border: 1px solid #ddd; padding: 10px; border-radius: 5px; background: rgba(0,0,0,0.1);'>{highlighted_text}</div>", unsafe_allow_html=True)
                        else:
                            st.write("No specific buzzwords detected.")
                            
                except ValueError as ve:
                    st.error(str(ve))
                except Exception as e:
                    st.error(f"Something went wrong: {e}")
