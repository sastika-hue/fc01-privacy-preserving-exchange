import streamlit as st
from secret_sharing import split, secure_sum, threshold_check

st.set_page_config(page_title="FC-01: Privacy-Preserving Financial Exchange", page_icon="🔐", layout="wide")

THRESHOLD = 50000

BANK_DB = {
    "CUST001": {"name": "Arjun Menon", "income": 62000},
    "CUST002": {"name": "Divya Rao", "income": 22000},
    "CUST003": {"name": "Karthik Iyer", "income": 48000},
    "CUST004": {"name": "Meena Pillai", "income": 15000},
}
NBFC_DB = {
    "CUST001": {"name": "Arjun Menon", "debt": 8000},
    "CUST002": {"name": "Divya Rao", "debt": 18000},
    "CUST003": {"name": "Karthik Iyer", "debt": 12000},
    "CUST004": {"name": "Meena Pillai", "debt": 9000},
}
BUREAU_DB = {
    "CUST001": {"name": "Arjun Menon", "score": 780},
    "CUST002": {"name": "Divya Rao", "score": 310},
    "CUST003": {"name": "Karthik Iyer", "score": 650},
    "CUST004": {"name": "Meena Pillai", "score": 200},
}

st.title("🔐 FC-01 — Privacy-Preserving Financial Data Exchange")
st.caption("Three institutions jointly compute a loan eligibility decision for a shared customer using additive secret-sharing MPC.")
st.info("This deployed demo runs the identical protocol logic as our local 4-microservice build (see repo/video) in a single process for deployment speed.")
st.divider()

customer_options = {f"{v['name']}  ·  {k}": k for k, v in BANK_DB.items()}
st.subheader("Step 1 — Select a customer")
selected_label = st.selectbox("Shared customer on file at all 3 institutions", list(customer_options.keys()))
cid = customer_options[selected_label]

st.divider()
cols = st.columns(3)
labels = [("🏦 Bank", "Income"), ("💳 NBFC", "Existing Debt"), ("📊 Credit Bureau", "Repayment Score")]
for (title, field), col in zip(labels, cols):
    with col:
        with st.container(border=True):
            st.markdown(f"### {title}")
            st.markdown(f"**{field}**")
            st.markdown("🔒 *private*")

st.divider()
if st.button("🚀 Run Secure Eligibility Check", type="primary", use_container_width=True):
    with st.status("Running the MPC protocol...", expanded=True) as status:
        st.write("🏦 Bank splitting income into 3 shares...")
        bank_shares = split(BANK_DB[cid]["income"])
        st.write("💳 NBFC splitting debt into 3 shares...")
        nbfc_shares = split(NBFC_DB[cid]["debt"])
        st.write("📊 Bureau splitting repayment score into 3 shares...")
        bureau_shares = split(BUREAU_DB[cid]["score"])

        st.write("Aggregator computing secure sum across institutions...")
        summed = secure_sum([bank_shares, nbfc_shares, bureau_shares])
        eligible = threshold_check(summed, THRESHOLD)
        decision = "Eligible" if eligible else "Not Eligible"
        status.update(label="Protocol complete", state="complete")

    st.divider()
    st.subheader("Step 2 — Network trace")
    st.caption("These are the actual share values computed. No raw income, debt, or score value is ever used in the decision math.")
    st.code(f'🏦 Bank -> aggregator: {{"shares": {bank_shares}}}', language="json")
    st.code(f'💳 NBFC -> aggregator: {{"shares": {nbfc_shares}}}', language="json")
    st.code(f'📊 Bureau -> aggregator: {{"shares": {bureau_shares}}}', language="json")

    st.divider()
    st.subheader("Step 3 — Joint decision")
    if decision == "Eligible":
        st.success(f"### ✅ Decision: {decision}")
    else:
        st.error(f"### ❌ Decision: {decision}")

with st.expander("How this works"):
    st.markdown("Each value V is split into 3 shares such that `V = s1 + s2 + s3 (mod p)`. Shares are summed position-wise across institutions, then compared to a threshold -- no individual value is ever reconstructed.")