import streamlit as st
import requests

st.set_page_config(
    page_title="FC-01: Privacy-Preserving Financial Exchange",
    page_icon="🔐",
    layout="wide",
)

BANK_URL = "http://127.0.0.1:5001"
NBFC_URL = "http://127.0.0.1:5002"
BUREAU_URL = "http://127.0.0.1:5003"
AGGREGATOR_URL = "http://127.0.0.1:5000"

INSTITUTIONS = [
    ("bank", "🏦", "Bank", BANK_URL, "Income"),
    ("nbfc", "💳", "NBFC", NBFC_URL, "Existing Debt"),
    ("bureau", "📊", "Credit Bureau", BUREAU_URL, "Repayment Score"),
]

st.title("🔐 FC-01 — Privacy-Preserving Financial Data Exchange")
st.caption(
    "Three institutions jointly compute a loan eligibility decision for a shared "
    "customer using additive secret-sharing MPC — no institution, and no central "
    "aggregator, ever sees another party's raw data."
)
st.divider()

try:
    customers = requests.get(f"{BANK_URL}/customers", timeout=3).json()
except requests.exceptions.RequestException:
    st.error(
        "Can't reach the bank service on port 5001. Make sure all 4 backend "
        "services (aggregator, bank, nbfc, bureau) are running before using "
        "this dashboard."
    )
    st.stop()

customer_options = {f"{c['name']}  ·  {c['customer_id']}": c["customer_id"] for c in customers}

st.subheader("Step 1 — Select a customer")
selected_label = st.selectbox("Shared customer on file at all 3 institutions", list(customer_options.keys()))
selected_customer_id = customer_options[selected_label]

st.divider()
st.subheader("Step 2 — Each institution's private record")
st.caption("These values are held locally by each institution. They are never sent anywhere in raw form — only as secret shares.")

cols = st.columns(3)
for (key, icon, label, url, field_label), col in zip(INSTITUTIONS, cols):
    with col:
        with st.container(border=True):
            st.markdown(f"### {icon} {label}")
            st.markdown(f"**{field_label}**")
            st.markdown("🔒 *private — not shown here*")

st.divider()

run = st.button("🚀 Run Secure Eligibility Check", type="primary", use_container_width=True)

if run:
    trace = []

    with st.status("Running the MPC protocol...", expanded=True) as status:
        st.write("Resetting aggregator state...")
        requests.post(f"{AGGREGATOR_URL}/reset", timeout=5)

        for key, icon, label, url, field_label in INSTITUTIONS:
            st.write(f"{icon} {label} splitting **{field_label}** into 3 shares and sending to aggregator...")
            resp = requests.post(f"{url}/submit", json={"customer_id": selected_customer_id}, timeout=5).json()
            if "error" in resp:
                status.update(label=f"Error from {label}", state="error")
                st.error(resp["error"])
                st.stop()
            trace.append((label, icon, resp["shares_sent"]))
            final_resp = resp

        decision = final_resp["aggregator_response"].get("decision", "unknown")
        status.update(label="Protocol complete", state="complete")

    st.divider()
    st.subheader("Step 3 — Network trace: what actually crossed the wire")
    st.caption("Every institution sent only these numbers. No income, debt, or score value was ever transmitted.")
    for label, icon, shares in trace:
        st.code(f'{icon} {label} → aggregator:  {{"shares": {shares}}}', language="json")

    st.divider()
    st.subheader("Step 4 — Joint decision")
    if decision == "Eligible":
        st.success(f"### ✅ Decision: {decision}")
    else:
        st.error(f"### ❌ Decision: {decision}")
    st.caption(
        "The aggregator summed shares position-wise across institutions and "
        "reconstructed only the joint total — never any single institution's "
        "private value."
    )

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