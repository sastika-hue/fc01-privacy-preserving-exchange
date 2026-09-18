import streamlit as st
import requests

st.set_page_config(page_title="FC-01: Privacy-Preserving Financial Exchange", layout="wide")

BANK_URL = "http://127.0.0.1:5001"
NBFC_URL = "http://127.0.0.1:5002"
BUREAU_URL = "http://127.0.0.1:5003"
AGGREGATOR_URL = "http://127.0.0.1:5000"

st.title("FC-01 — Privacy-Preserving Financial Data Exchange")
st.caption("Additive secret-sharing MPC demo — Bank, NBFC, and Credit Bureau jointly compute a loan eligibility decision without revealing their private values to each other or to the aggregator.")

st.divider()

st.subheader("Step 1 — Set each institution's private value")
col1, col2, col3 = st.columns(3)
with col1:
    bank_value = st.number_input("Bank: Customer income", min_value=0, value=45000, step=1000)
with col2:
    nbfc_value = st.number_input("NBFC: Existing debt", min_value=0, value=15000, step=1000)
with col3:
    bureau_value = st.number_input("Credit Bureau: Repayment score", min_value=0, value=720, step=10)

st.divider()

if st.button("Run Secure Eligibility Check", type="primary"):
    trace = []

    with st.status("Running the MPC protocol...", expanded=True) as status:
        st.write("Resetting aggregator state...")
        requests.post(f"{AGGREGATOR_URL}/reset", timeout=5)

        st.write("Configuring institution values...")
        requests.post(f"{BANK_URL}/set-value", json={"value": int(bank_value)}, timeout=5)
        requests.post(f"{NBFC_URL}/set-value", json={"value": int(nbfc_value)}, timeout=5)
        requests.post(f"{BUREAU_URL}/set-value", json={"value": int(bureau_value)}, timeout=5)

        st.write("Bank splitting income into 3 shares and sending to aggregator...")
        bank_resp = requests.post(f"{BANK_URL}/submit", timeout=5).json()
        trace.append(("Bank", bank_resp["shares_sent"]))

        st.write("NBFC splitting debt into 3 shares and sending to aggregator...")
        nbfc_resp = requests.post(f"{NBFC_URL}/submit", timeout=5).json()
        trace.append(("NBFC", nbfc_resp["shares_sent"]))

        st.write("Credit Bureau splitting repayment score into 3 shares and sending to aggregator...")
        bureau_resp = requests.post(f"{BUREAU_URL}/submit", timeout=5).json()
        trace.append(("Credit Bureau", bureau_resp["shares_sent"]))

        decision = bureau_resp["aggregator_response"].get("decision", "unknown")
        status.update(label="Protocol complete", state="complete")

    st.divider()
    st.subheader("Step 2 — Network trace (what actually crossed the wire)")
    st.caption("Each institution only ever sent these numbers. No raw income, debt, or score value was ever transmitted.")
    for name, shares in trace:
        st.code(f'{name} -> aggregator: {{"institution": "...", "shares": {shares}}}', language="json")

    st.divider()
    st.subheader("Step 3 — Joint decision")
    if decision == "Eligible":
        st.success(f"Decision: {decision}")
    else:
        st.error(f"Decision: {decision}")
    st.caption("The aggregator never reconstructed any single institution's private value — only the joint sum was checked against the threshold.")

st.divider()
with st.expander("How this works"):
    st.markdown("""
    Each institution splits its private value V into 3 random shares such that
    `V = s1 + s2 + s3 (mod p)`. Any single share looks like a random number and
    reveals nothing about V on its own.

    The aggregator sums shares **position-wise across institutions** (never
    combining one institution's own 3 shares together), then checks the
    reconstructed total against a threshold. This means the aggregator learns
    the joint total — but never any individual institution's value.
    """)