import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO

# Set page config
st.set_page_config(
    page_title="Ad Copy A/B Tester (No AI)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'ab_test_results' not in st.session_state:
    st.session_state.ab_test_results = None
if 'ad_copies' not in st.session_state:
    st.session_state.ad_copies = ["", "", ""]

# Sidebar for A/B test settings
with st.sidebar:
    st.title("🧪 A/B Test Settings")
    st.markdown("---")
    base_conversion = st.slider("Expected Base Conversion Rate (%)", 0.1, 10.0, 2.0, 0.1) / 100
    sample_size = st.number_input("Sample Size per Variation", 1000, 100000, 10000, 1000)
    st.info("💡 Enter your ad copies below, then run the simulation!")

# Main app
st.title("📊 Ad Copy A/B Tester (No AI Required)")
st.markdown("Enter your own ad copy variations and simulate A/B test performance!")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Enter Ad Copies", "A/B Test Results", "Performance Dashboard", "Insights & Export"])

with tab1:
    st.subheader("✏️ Enter Your Ad Copy Variations")
    st.markdown("Fill in 2 or 3 versions of your ad copy to test:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        copy1 = st.text_area("Variation 1", value=st.session_state.ad_copies[0], height=200)
    with col2:
        copy2 = st.text_area("Variation 2", value=st.session_state.ad_copies[1], height=200)
    with col3:
        copy3 = st.text_area("Variation 3", value=st.session_state.ad_copies[2], height=200)
    
    if st.button("💾 Save Ad Copies", type="primary"):
        st.session_state.ad_copies = [copy1, copy2, copy3]
        st.success("Ad copies saved! Go to 'A/B Test Results' to simulate.")
        st.session_state.ab_test_results = None

with tab2:
    if not any(st.session_state.ad_copies):
        st.info("Please enter at least one ad copy in the 'Enter Ad Copies' tab.")
    else:
        if st.button("🚀 Run A/B Test Simulation", type="primary"):
            variations = [v for v in st.session_state.ad_copies if v.strip()]
            if len(variations) == 0:
                st.warning("Please enter at least one ad copy.")
            else:
                results = []
                for i, variation in enumerate(variations):
                    conversion_rate = base_conversion * (1 + np.random.uniform(-0.2, 0.5))
                    conversions = np.random.binomial(sample_size, conversion_rate)
                    results.append({
                        'Variation': f'Variation {i+1}',
                        'Ad Copy': variation[:100] + "..." if len(variation) > 100 else variation,
                        'Impressions': sample_size,
                        'Conversions': conversions,
                        'Conversion Rate': conversions / sample_size,
                        'CTR': np.random.uniform(0.02, 0.1)
                    })
                
                st.session_state.ab_test_results = pd.DataFrame(results)
                st.success("✅ Simulation complete!")
        
        if st.session_state.ab_test_results is not None:
            df = st.session_state.ab_test_results
            st.subheader("📈 Simulated Results")
            st.dataframe(
                df.style.format({
                    'Conversion Rate': '{:.2%}',
                    'CTR': '{:.2%}'
                }),
                use_container_width=True
            )
            
            winner_idx = df['Conversion Rate'].idxmax()
            winner = df.loc[winner_idx, 'Variation']
            st.success(f"🏆 **{winner}** wins with **{df.loc[winner_idx, 'Conversion Rate']:.2%}** conversion rate!")

with tab3:
    if st.session_state.ab_test_results is None:
        st.info("Run an A/B test in the 'A/B Test Results' tab to see the dashboard.")
    else:
        df = st.session_state.ab_test_results
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Impressions", f"{df['Impressions'].sum():,}")
        with col2:
            st.metric("Total Conversions", f"{df['Conversions'].sum():,}")
        with col3:
            st.metric("Avg. Conversion Rate", f"{df['Conversion Rate'].mean():.2%}")
        with col4:
            st.metric("Best Conversion Rate", f"{df['Conversion Rate'].max():.2%}")
        
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.bar(df, x='Variation', y='Conversion Rate', title="Conversion Rate by Variation")
            fig1.update_layout(yaxis_tickformat='.1%')
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            fig2 = px.bar(df, x='Variation', y='CTR', title="Click-Through Rate (CTR)")
            fig2.update_layout(yaxis_tickformat='.1%')
            st.plotly_chart(fig2, use_container_width=True)
        
        st.subheader("💡 Recommendations")
        best_idx = df['Conversion Rate'].idxmax()
        st.markdown(f"""
        - Deploy **{df.loc[best_idx, 'Variation']}** in your campaigns
        - Its conversion rate is **{((df.loc[best_idx, 'Conversion Rate'] / df['Conversion Rate'].mean()) - 1):+.0%}** above average
        - Consider testing elements from this version in future ads
        """)

# === NEW TAB: Insights & Export ===
with tab4:
    if st.session_state.ab_test_results is None:
        st.info("Run an A/B test in the 'A/B Test Results' tab to generate insights.")
    else:
        df = st.session_state.ab_test_results
        best_idx = df['Conversion Rate'].idxmax()
        winner = df.loc[best_idx, 'Variation']
        winner_cr = df.loc[best_idx, 'Conversion Rate']
        avg_cr = df['Conversion Rate'].mean()
        lift = (winner_cr / avg_cr - 1) * 100

        # Generate insights text
        insights = f"""
Ad Copy A/B Test Insights Report
{'='*40}

Test Configuration:
- Base Conversion Rate: {base_conversion:.2%}
- Sample Size per Variation: {sample_size:,}

Results Summary:
- Total Variations Tested: {len(df)}
- Winning Variation: {winner}
- Winner Conversion Rate: {winner_cr:.2%}
- Average Conversion Rate: {avg_cr:.2%}
- Relative Lift: {lift:+.1f}%

Recommendations:
1. Deploy {winner} as your primary ad copy.
2. The winning variation outperforms the average by {abs(lift):.1f}%, indicating strong performance.
3. Consider qualitative analysis of the winning ad copy's messaging, tone, or CTA for future campaigns.
4. Run a follow-up test with refined versions of the winner to further optimize.

Variation Details:
"""
        for _, row in df.iterrows():
            insights += f"\n- {row['Variation']}:\n"
            insights += f"  • Conversion Rate: {row['Conversion Rate']:.2%}\n"
            insights += f"  • CTR: {row['CTR']:.2%}\n"
            insights += f"  • Ad Copy Snippet: \"{row['Ad Copy']}\"\n"

        st.subheader("📄 Generated Insights")
        st.text_area("Insights Summary", insights, height=500)

        # Download button
        st.download_button(
            label="📥 Download Insights Report (.txt)",
            data=insights,
            file_name="ad_copy_ab_test_insights.txt",
            mime="text/plain"
        )

st.markdown("---")