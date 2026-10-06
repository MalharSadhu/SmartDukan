import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor

st.set_page_config(page_title="SmartDukan - AI Retail Operations", layout="wide", page_icon="⚡")

st.markdown("""
<style>
    .pos-box { background-color: #0F172A; color: #F8FAFC; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 13px; }
    .ai-box { background-color: #042F2C; border-left: 4px solid #10B981; color: #E2E8F0; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 13px; }
    .wa-bubble { 
        background-color: #DCF8C6; 
        color: #0F281E; 
        padding: 16px; 
        border-radius: 10px; 
        border: 1px solid #B8E49D; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        margin-bottom: 12px;
    }
    .wa-header { font-weight: 700; font-size: 14px; color: #1E4620; margin-bottom: 8px; border-bottom: 1px solid #C4E3A8; padding-bottom: 4px; }
    .wa-line { font-size: 13px; margin: 4px 0; line-height: 1.4; }
    .verify-box-pass { background-color: #DEF7EC; border: 1px solid #31C48D; color: #03543F; padding: 12px; border-radius: 6px; margin-top: 8px; font-size: 13px; }
    .verify-box-fail { background-color: #FDE8E8; border: 1px solid #F98080; color: #9B1C1C; padding: 12px; border-radius: 6px; margin-top: 8px; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# ML Engine: Quick Train
# ---------------------------------------------------------
@st.cache_resource
def get_ml_model():
    np.random.seed(42)
    X = pd.DataFrame({
        "day_of_week": np.random.randint(0, 7, 100),
        "is_weekend": np.random.choice([0, 1], 100),
        "festival_spike": np.random.choice([0.0, 0.5, 0.9], 100)
    })
    y = (500 + X["is_weekend"] * 60 + X["festival_spike"] * 240 + np.random.normal(0, 15, 100)).astype(int)
    m = RandomForestRegressor(n_estimators=30, random_state=42)
    m.fit(X, y)
    return m

ml_model = get_ml_model()

# ---------------------------------------------------------
# Session State: Database Initialized with Milk = 0
# ---------------------------------------------------------
if "optech_db" not in st.session_state:
    st.session_state.optech_db = {
        "Milk ½ Ltr": {"category": "Dairy", "stock": 0, "price": 26.0, "batch_age": 1, "shelf_life": 2},
        "Oil 1 Ltr": {"category": "Staple", "stock": 120, "price": 130.0, "batch_age": 20, "shelf_life": 180},
        "Specialty Dal": {"category": "Staple", "stock": 90, "price": 145.0, "batch_age": 25, "shelf_life": 180},
        "Salt 1kg Pkt": {"category": "Staple", "stock": 30, "price": 25.0, "batch_age": 15, "shelf_life": 365},
        "Chilly Masala": {"category": "Spices", "stock": 40, "price": 240.0, "batch_age": 45, "shelf_life": 180},
        "Sambar Masala": {"category": "Spices", "stock": 18, "price": 260.0, "batch_age": 60, "shelf_life": 180},
        "Garam Masala": {"category": "Spices", "stock": 25, "price": 300.0, "batch_age": 80, "shelf_life": 180},
        "Premium Cooker (3L)": {"category": "Appliances", "stock": 8, "price": 3000.0, "batch_age": 15, "shelf_life": 1825},
        "Rava Pack (500g)": {"category": "Grains", "stock": 40, "price": 45.0, "batch_age": 10, "shelf_life": 15},
    }

today = datetime.now()
st.session_state.customer_registry = {
    "8830729227": [{"sku": "Rava Pack (500g)", "purchase_date": (today - timedelta(days=32)).strftime("%Y-%m-%d"), "days_ago": 32, "paid": 45.0}],
    "9527418608": [{"sku": "Premium Cooker (3L)", "purchase_date": (today - timedelta(days=68)).strftime("%Y-%m-%d"), "days_ago": 68, "paid": 3000.0}],
    "9876543210": [
        {"sku": "Rava Pack (500g)", "purchase_date": (today - timedelta(days=32)).strftime("%Y-%m-%d"), "days_ago": 32, "paid": 45.0},
        {"sku": "Oil 1 Ltr", "purchase_date": (today - timedelta(days=2)).strftime("%Y-%m-%d"), "days_ago": 2, "paid": 130.0}
    ],
    "9123456789": [{"sku": "Garam Masala", "purchase_date": (today - timedelta(days=4)).strftime("%Y-%m-%d"), "days_ago": 4, "paid": 300.0}],
    "9988776655": [{"sku": "Milk ½ Ltr", "purchase_date": (today - timedelta(days=5)).strftime("%Y-%m-%d"), "days_ago": 5, "paid": 26.0}]
}

if "pending_alerts" not in st.session_state:
    st.session_state.pending_alerts = ["RESTOCK", "MARKDOWN"]

if "audit_log" not in st.session_state:
    st.session_state.audit_log = []

if "verification_results" not in st.session_state:
    st.session_state.verification_results = {}

# ---------------------------------------------------------
# Sidebar: Live Demo & Testing Suite
# ---------------------------------------------------------
with st.sidebar:
    st.header("🎮 Live Demo Testing Suite")
    st.caption("Trigger edge cases live in front of the evaluator.")
    
    festival_mode = st.toggle("🎉 Simulate Festival Demand Surge (+35%)", value=True)
    
    st.divider()
    st.subheader("⚡ 1-Click Anomaly Triggers")
    
    c_side1, c_side2 = st.columns(2)
    with c_side1:
        if st.button("🚨 Milk = 0", use_container_width=True):
            st.session_state.optech_db["Milk ½ Ltr"]["stock"] = 0
            if "RESTOCK" not in st.session_state.pending_alerts:
                st.session_state.pending_alerts.append("RESTOCK")
            st.rerun()
            
    with c_side2:
        if st.button("📦 Milk = 40", use_container_width=True):
            st.session_state.optech_db["Milk ½ Ltr"]["stock"] = 40
            if "RESTOCK" not in st.session_state.pending_alerts:
                st.session_state.pending_alerts.append("RESTOCK")
            st.rerun()

    if st.button("⏳ Force Aging Masala (Day 85)", use_container_width=True):
        st.session_state.optech_db["Garam Masala"]["batch_age"] = 85
        st.session_state.optech_db["Garam Masala"]["price"] = 300.0
        if "MARKDOWN" not in st.session_state.pending_alerts:
            st.session_state.pending_alerts.append("MARKDOWN")
        st.rerun()

    st.divider()
    st.subheader("🛠️ Quick Stock Adjuster")
    sku_to_tune = st.selectbox("Select SKU:", list(st.session_state.optech_db.keys()))
    
    # SAFETY GUARD: Ensure value is never below min_value 0
    current_val = max(0, int(st.session_state.optech_db[sku_to_tune]["stock"]))
    new_stock = st.number_input("Set Stock Level:", min_value=0, max_value=2000, value=current_val, step=10)
    
    if st.button(f"Apply to {sku_to_tune}", use_container_width=True):
        st.session_state.optech_db[sku_to_tune]["stock"] = max(0, new_stock)
        if sku_to_tune == "Milk ½ Ltr":
            if new_stock <= 80 and "RESTOCK" not in st.session_state.pending_alerts:
                st.session_state.pending_alerts.append("RESTOCK")
            elif new_stock > 80 and "RESTOCK" in st.session_state.pending_alerts:
                st.session_state.pending_alerts.remove("RESTOCK")
        st.rerun()

    st.divider()
    if st.button("🔄 Factory Reset Demo", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ---------------------------------------------------------
# ML Forecast Prediction
# ---------------------------------------------------------
features = pd.DataFrame([{"day_of_week": today.weekday(), "is_weekend": 1 if today.weekday() >= 5 else 0, "festival_spike": 0.8 if festival_mode else 0.0}])
ml_milk_demand = int(ml_model.predict(features)[0])

# ---------------------------------------------------------
# Top Bar Metrics
# ---------------------------------------------------------
st.title("⚡ Optech POS ↔ SmartDukan AI Bridge")
st.caption("TRL 4 Prototype: Autonomous Reordering, Markdown Execution & Fraud Shield[cite: 1, 4]")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Optech POS", "Connected")
m2.metric("ML Forecast (Milk)", f"{ml_milk_demand} pkts/day", delta="+Festival Surge" if festival_mode else "Normal")
milk_curr = st.session_state.optech_db['Milk ½ Ltr']['stock']
m3.metric("Milk Stock Status", f"{milk_curr} pkts", delta="-ZERO STOCK" if milk_curr == 0 else "Sufficient", delta_color="inverse")
m4.metric("Pending Approvals", f"{len(st.session_state.pending_alerts)} Actions")

st.divider()

col_pos, col_ai = st.columns([1.1, 0.9], gap="large")

# =========================================================
# RIGHT: AI COPILOT (Clean WhatsApp Cards)
# =========================================================
with col_ai:
    st.subheader("🤖 SmartDukan AI Copilot")
    st.markdown('<div class="ai-box"><b>[AGENT STATUS: ACTIVE]</b><br>• ML Restock Forecaster: RUNNING<br>• Batch Markdown Agent: MONITORING<br>• Human-in-the-Loop Gateway: READY[cite: 1]</div>', unsafe_allow_html=True)
    st.write("")
    
    st.markdown("##### 📱 Owner WhatsApp Action Stream")

    if not st.session_state.pending_alerts:
        st.success("✅ All actions approved! Inventory updated in Optech POS[cite: 4].")
    else:
        # Card 1: Milk Restock
        if "RESTOCK" in st.session_state.pending_alerts:
            current_milk_stock = st.session_state.optech_db["Milk ½ Ltr"]["stock"]
            stock_warning = "🚨 <b>OUT OF STOCK: 0 packets on shelf!</b>" if current_milk_stock == 0 else f"📊 <b>Current Stock:</b> {current_milk_stock} packets (depletes in &lt;2 hrs!)[cite: 2]"
            
            st.markdown(f"""
            <div class="wa-bubble">
                <div class="wa-header">🚨 CRITICAL RESTOCK ALERT: Milk ½ Ltr</div>
                <div class="wa-line">{stock_warning}</div>
                <div class="wa-line">📈 <b>ML Forecast:</b> <b>{ml_milk_demand} pkts/day</b> (includes festival surge)[cite: 2]</div>
                <div class="wa-line">🚚 <b>Supplier Lead Time:</b> 24 hours[cite: 2]</div>
                <div class="wa-line">👉 <b>Proposed PO:</b> Order <b>1,500 pkts</b> from Dairy Distributor[cite: 3, 4]</div>
            </div>
            """, unsafe_allow_html=True)

            b1, b2 = st.columns(2)
            with b1:
                if st.button("✅ 1-Click Approve PO (Milk)", key="btn_milk_app", use_container_width=True):
                    st.session_state.optech_db["Milk ½ Ltr"]["stock"] += 1500
                    st.session_state.audit_log.insert(0, {
                        "Time": datetime.now().strftime("%H:%M:%S"),
                        "Trigger": "RESTOCK",
                        "SKU": "Milk ½ Ltr",
                        "Action": "Sent PO for 1,500 pkts via WhatsApp. On-hand restocked.",
                        "Status": "SYNCED TO POS"
                    })
                    st.session_state.pending_alerts.remove("RESTOCK")
                    st.rerun()
            with b2:
                if st.button("❌ Dismiss (Milk)", key="btn_milk_dis", use_container_width=True):
                    st.session_state.pending_alerts.remove("RESTOCK")
                    st.rerun()

        # Card 2: Markdown
        if "MARKDOWN" in st.session_state.pending_alerts:
            st.markdown("""
            <div class="wa-bubble">
                <div class="wa-header">🏷️ AGING BATCH ALERT: Garam Masala</div>
                <div class="wa-line">⏳ <b>Batch Age:</b> 80 days old (Safety threshold: 75 days)[cite: 2, 4]</div>
                <div class="wa-line">⚠️ <b>Risk:</b> Only 40 days left before mandatory 4-month total write-off[cite: 2, 4]</div>
                <div class="wa-line">📉 <b>Current Runway:</b> 1.5 kg/day (will not clear before Month 4)[cite: 2, 4]</div>
                <div class="wa-line">👉 <b>Proposed Action:</b> Apply <b>15% discount</b> (₹300 ➔ <b>₹255.00</b>)[cite: 2, 4]</div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ 1-Click Approve Discount (Masala)", key="btn_masala_app", use_container_width=True):
                    st.session_state.optech_db["Garam Masala"]["price"] = 255.0
                    st.session_state.audit_log.insert(0, {
                        "Time": datetime.now().strftime("%H:%M:%S"),
                        "Trigger": "MARKDOWN",
                        "SKU": "Garam Masala",
                        "Action": "Applied 15% markdown (₹300 ➔ ₹255.00) in Optech POS.",
                        "Status": "SYNCED TO POS"
                    })
                    st.session_state.pending_alerts.remove("MARKDOWN")
                    st.rerun()
            with c2:
                if st.button("❌ Dismiss (Masala)", key="btn_masala_dis", use_container_width=True):
                    st.session_state.pending_alerts.remove("MARKDOWN")
                    st.rerun()

# =========================================================
# LEFT: OPTECH POS (Returns & Live Inventory)
# =========================================================
with col_pos:
    st.subheader("🖥️ Optech Cloud POS Register")
    pos_mode = st.radio("Counter Mode:", ["🔄 Customer Returns Desk", "🛒 Cashier Checkout"], horizontal=True)

    if pos_mode == "🔄 Customer Returns Desk":
        st.markdown('<div class="pos-box"><b>[OPTECH RETURNS DESK]</b> — FRAUD SHIELD ACTIVE</div>', unsafe_allow_html=True)
        phone = st.text_input("Enter Customer Phone Number:", value="8830729227").strip()

        if phone in st.session_state.customer_registry:
            items = st.session_state.customer_registry[phone]
            st.success(f"Customer Verified: Found {len(items)} purchase record(s).")
            
            for idx, item in enumerate(items):
                sku = item["sku"]
                shelf = st.session_state.optech_db[sku]["shelf_life"]
                days = item["days_ago"]
                paid = item["paid"]

                col_txt, col_btn = st.columns([3, 1])
                with col_txt:
                    st.write(f"**{sku}** | ₹{paid:.2f} | Purchased {days}d ago ({item['purchase_date']}) | Shelf-life: {shelf}d[cite: 2]")
                with col_btn:
                    if st.button("Verify Return", key=f"ret_{phone}_{idx}", use_container_width=True):
                        if days > shelf:
                            st.session_state.verification_results[f"{phone}_{idx}"] = {
                                "type": "fail",
                                "msg": f"🚨 <b>REFUND REJECTED: EXPIRED GOODS</b><br>Bought {days} days ago with a {shelf}-day shelf-life[cite: 2]. Expired {days - shelf} days ago in customer's home[cite: 2]. Store saved ₹{paid:.2f}[cite: 2]!"
                            }
                            st.session_state.audit_log.insert(0, {"Time": datetime.now().strftime("%H:%M:%S"), "Trigger": "FRAUD_BLOCK", "SKU": sku, "Action": f"Rejected expired return. Saved ₹{paid:.2f}[cite: 2].", "Status": "BLOCKED"})
                        elif days > 14:
                            st.session_state.verification_results[f"{phone}_{idx}"] = {
                                "type": "fail",
                                "msg": f"⚠️ <b>REFUND REJECTED: PAST 14-DAY POLICY</b><br>Item was purchased {days} days ago[cite: 2]. Cash refund window is closed[cite: 2]."
                            }
                            st.session_state.audit_log.insert(0, {"Time": datetime.now().strftime("%H:%M:%S"), "Trigger": "POLICY_REJECT", "SKU": sku, "Action": f"Rejected return past 14d policy[cite: 2].", "Status": "BLOCKED"})
                        else:
                            st.session_state.verification_results[f"{phone}_{idx}"] = {
                                "type": "pass",
                                "msg": f"✅ <b>VALID RETURN APPROVED</b><br>Purchased {days} days ago[cite: 2]. Refund of ₹{paid:.2f} issued to customer[cite: 2]."
                            }
                            st.session_state.audit_log.insert(0, {"Time": datetime.now().strftime("%H:%M:%S"), "Trigger": "VALID_RETURN", "SKU": sku, "Action": f"Approved refund of ₹{paid:.2f}[cite: 2].", "Status": "REFUNDED"})
                        st.rerun()

                res_key = f"{phone}_{idx}"
                if res_key in st.session_state.verification_results:
                    r = st.session_state.verification_results[res_key]
                    box_class = "verify-box-pass" if r["type"] == "pass" else "verify-box-fail"
                    st.markdown(f"<div class='{box_class}'>{r['msg']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='verify-box-fail'>❌ <b>NO RECORD FOUND</b><br>No purchase on file for {phone}[cite: 2]. Refund rejected[cite: 2].</div>", unsafe_allow_html=True)

    else:
        st.markdown('<div class="pos-box"><b>[OPTECH CASHIER CHECKOUT]</b> — BILLING</div>', unsafe_allow_html=True)
        bsku = st.selectbox("Select Item:", list(st.session_state.optech_db.keys()))
        bqty = st.number_input("Quantity:", min_value=1, max_value=50, value=10)
        price = st.session_state.optech_db[bsku]["price"]
        st.write(f"Price: **₹{price:.2f}** | Total: **₹{price * bqty:.2f}**")
        if st.button("💳 Accept Payment & Deduct Stock", use_container_width=True):
            # Clamp deduction so stock never drops below 0
            st.session_state.optech_db[bsku]["stock"] = max(0, st.session_state.optech_db[bsku]["stock"] - bqty)
            st.success(f"Billed {bqty} units of {bsku}.")
            st.rerun()

    st.write("")
    st.markdown("##### 📦 Live Optech Store Inventory")
    df = pd.DataFrame([
        {"SKU": k, "Category": v["category"], "On Hand": v["stock"], "Batch Age": f"{v['batch_age']}d", "Price": f"₹{v['price']:.2f}"}
        for k, v in st.session_state.optech_db.items()
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)

# =========================================================
# AUDIT LOG
# =========================================================
st.divider()
st.subheader("📜 Two-Way System Audit Trail (TRL 4 Live Sync Log)")
if st.session_state.audit_log:
    st.dataframe(pd.DataFrame(st.session_state.audit_log), use_container_width=True, hide_index=True)
else:
    st.caption("Actions taken on WhatsApp or at the Returns desk will appear here.")