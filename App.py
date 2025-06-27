import streamlit as st # type: ignore
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
import requests # type: ignore
from sklearn.ensemble import RandomForestClassifier # type: ignore
from sklearn.model_selection import train_test_split # type: ignore
from sklearn.preprocessing import LabelEncoder # type: ignore
import os
import seaborn as sns # type: ignore
import matplotlib.pyplot as plt # type: ignore
import smtplib
from email.message import EmailMessage
import base64

# --- Email sending function using smtplib ---
def send_email(to, subject, body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = st.secrets["email"]["user"]
    msg['To'] = to
    msg.set_content(body)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(st.secrets["email"]["user"], st.secrets["email"]["password"])
        smtp.send_message(msg)

# --- Email sending function with QR code attachment ---
def send_email_with_qr(to, subject, body, qr_base64):
    import base64
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = st.secrets["email"]["user"]
    msg['To'] = to
    msg.set_content(body)

    # Extract base64 part if data URL
    if qr_base64.startswith("data:image"):
        qr_base64 = qr_base64.split(",", 1)[-1]
    try:
        img_bytes = base64.b64decode(qr_base64)
        msg.add_attachment(img_bytes, maintype='image', subtype='png', filename='payment_qr.png')
    except Exception as e:
        print(f"Failed to attach QR image: {e}")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(st.secrets["email"]["user"], st.secrets["email"]["password"])
        smtp.send_message(msg)

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Fee Warning Automation",
    layout="wide",  # Use wide layout for better mobile experience
    page_icon=":school:"
)

# Add viewport meta tag for mobile scaling
st.markdown(
    """
    <meta name="viewport" content="width=device-width, initial-scale=1">
    """,
    unsafe_allow_html=True
)

# Enhanced Custom CSS for a more interactive, colorful, and modern dark UI
st.markdown(
    """
    <style>
    html, body {
        max-width: 100vw;
        overflow-x: hidden;
        background: linear-gradient(120deg, #181c2f 0%, #232946 100%) !important;
        color: #f4f4f4 !important;
    }
    .main, .dark-main {
        background: linear-gradient(120deg, #232946 0%, #181c2f 100%) !important;
        border-radius: 22px;
        box-shadow: 0 6px 32px rgba(20, 30, 60, 0.25);
        padding: 2.7rem 2.2rem 2.2rem 2.2rem;
        margin-top: 1.7rem;
        animation: fadeIn 1.2s;
        max-width: 100vw;
        box-sizing: border-box;
        border: 2.5px solid #232946;
    }
    .stButton>button {
        background: linear-gradient(90deg, #F7CA18 0%, #2E86C1 60%, #117A65 100%);
        color: #181c2f;
        border-radius: 12px;
        font-weight: bold;
        font-size: 1.13em;
        padding: 0.7em 2.2em;
        border: none;
        transition: 0.2s;
        box-shadow: 0 2px 12px #2e86c13a;
        width: 100%;
        max-width: 350px;
        letter-spacing: 1.2px;
    }
    .stButton>button:hover {
        filter: brightness(1.1) drop-shadow(0 0 10px #F7CA18cc);
        background: linear-gradient(90deg, #117A65 0%, #F7CA18 100%);
        color: #232946;
    }
    .stDataFrame, .stTable {
        background: #232946cc !important;
        border-radius: 12px;
        box-shadow: 0 2px 12px #2e86c13a;
        color: #F7CA18 !important;
        font-size: 1.05em;
    }
    .stMetric {
        background: linear-gradient(90deg, #2E86C1 0%, #117A65 100%);
        border-radius: 14px;
        padding: 0.9em 0.7em;
        margin: 0.3em;
        box-shadow: 0 2px 12px #117A6588;
        color: #fff !important;
        font-weight: 700;
        font-size: 1.1em;
        letter-spacing: 1.1px;
    }
    .stExpanderHeader {
        font-size: 1.1em;
        color: #F7CA18;
        font-weight: bold;
    }
    .stFileUploader {
        background: #232946cc !important;
        border-radius: 10px;
        color: #F7CA18 !important;
        padding: 0.7em;
        box-shadow: 0 2px 8px #2e86c13a;
    }
    .stTextInput>div>input, .stTextArea>div>textarea, .stNumberInput>div>input {
        background: #181c2f !important;
        color: #F7CA18 !important;
        border-radius: 8px;
        border: 1.5px solid #2E86C1;
        font-weight: 600;
    }
    .stTextInput>div>input:focus, .stTextArea>div>textarea:focus, .stNumberInput>div>input:focus {
        border: 2px solid #F7CA18;
        outline: none;
    }
    .stDownloadButton>button {
        background: linear-gradient(90deg, #F7CA18 0%, #2E86C1 100%);
        color: #181c2f;
        border-radius: 10px;
        font-weight: bold;
        font-size: 1.1em;
        border: none;
        box-shadow: 0 2px 8px #F7CA1844;
        margin-top: 0.5em;
    }
    .stDownloadButton>button:hover {
        filter: brightness(1.1) drop-shadow(0 0 10px #2E86C1cc);
        background: linear-gradient(90deg, #117A65 0%, #F7CA18 100%);
        color: #232946;
    }
    .stCheckbox>label {
        color: #F7CA18 !important;
        font-weight: 600;
    }
    .stSlider>div>div>div>div {
        background: #2E86C1 !important;
    }
    .stSlider>div>div>div>div>div {
        background: #F7CA18 !important;
    }
    .stSelectbox>div>div>div>div {
        background: #232946 !important;
        color: #F7CA18 !important;
        border-radius: 8px;
    }
    .stSelectbox>div>div>div>div>div {
        color: #F7CA18 !important;
    }
    .stDataEditor {
        background: #181c2f !important;
        color: #F7CA18 !important;
        border-radius: 10px;
        font-size: 1.05em;
    }
    .stDataEditor thead tr {
        background: #2E86C1 !important;
        color: #fff !important;
    }
    .stDataEditor tbody tr {
        background: #232946cc !important;
        color: #F7CA18 !important;
    }
    .stInfo {
        background: linear-gradient(90deg, #117A65 0%, #2E86C1 100%) !important;
        color: #fff !important;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1.1em;
        box-shadow: 0 2px 8px #117A6588;
    }
    @media (max-width: 600px) {
        .main, .dark-main { padding: 1.2rem 0.5rem 1.2rem 0.5rem; }
        .stMetric { font-size: 0.95em; }
        .stButton>button { font-size: 1em; padding: 0.6em 1em; }
        .stDataFrame, .stTable { font-size: 0.95em; }
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(30px);}
        to { opacity: 1; transform: translateY(0);}
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Animated, interactive header with unique, modern, and even more engaging title styling (DARK THEME)
st.markdown(
    """
    <div class="main dark-main">
        <div class="title-flex">
            <img src="https://img.icons8.com/color/96/000000/school-building.png" class="title-icon left" width="70">
            <div class="title-center">
                <h1 class="school-title-unique">
                    <span class="shine">Ambition Public School of Excellence</span>
                    <span class="sparkle">✨</span>
                </h1>
                <span class="school-subtitle">
                    <span class="subtitle-anim">📧 Fee Warning & AI Automation Dashboard</span>
                </span>
            </div>
            <img src="https://img.icons8.com/color/96/000000/artificial-intelligence.png" class="title-icon right" width="70">
        </div>
        <div class="ribbon">Empowering Education with AI</div>
        <hr class="title-hr">
    </div>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@900&family=Pacifico&display=swap');
    html, body, .main, .dark-main {
        background: linear-gradient(120deg, #1a2233 0%, #232946 100%) !important;
        color: #f4f4f4 !important;
    }
    .dark-main {
        background: linear-gradient(120deg, #232946 0%, #1a2233 100%) !important;
        border-radius: 22px;
        box-shadow: 0 6px 32px rgba(20, 30, 60, 0.25);
        padding: 2.7rem 2.2rem 2.2rem 2.2rem;
        margin-top: 1.7rem;
        animation: fadeIn 1.2s;
        max-width: 100vw;
        box-sizing: border-box;
        border: 2.5px solid #232946;
    }
    .title-flex {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: -10px;
        gap: 18px;
        flex-wrap: wrap;
    }
    .title-icon {
        animation: bounce 1.5s infinite alternate;
        filter: drop-shadow(0 2px 8px #23294699);
        transition: transform 0.3s;
    }
    .title-icon.right {
        animation: pulse 2s infinite;
    }
    .title-center {
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 260px;
    }
    .school-title-unique {
        font-family: 'Montserrat', 'Segoe UI', 'Arial', sans-serif;
        font-size: 2.9em;
        font-weight: 900;
        background: linear-gradient(90deg, #F7CA18 0%, #2E86C1 40%, #117A65 80%, #F7CA18 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-fill-color: transparent;
        letter-spacing: 2.5px;
        text-shadow: 0 4px 24px #232946cc, 0 1px 0 #fff, 0 0 8px #F7CA18aa;
        position: relative;
        margin-bottom: 0.2em;
        animation: titleSlideIn 1.2s cubic-bezier(.4,0,.2,1);
        cursor: pointer;
        transition: text-shadow 0.3s, filter 0.3s;
        display: flex;
        align-items: center;
        gap: 0.2em;
    }
    .school-title-unique .shine {
        background: linear-gradient(90deg, #F7CA18 0%, #2E86C1 50%, #117A65 100%);
        background-size: 200% auto;
        color: #fff;
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shineMove 3s linear infinite;
        filter: drop-shadow(0 0 8px #F7CA18cc);
    }
    .school-title-unique .sparkle {
        font-family: 'Pacifico', cursive;
        font-size: 0.7em;
        color: #F7CA18;
        animation: sparkleTwinkle 1.5s infinite alternate;
        margin-left: 0.2em;
        filter: drop-shadow(0 0 8px #F7CA18cc);
    }
    .school-title-unique:hover {
        filter: brightness(1.18) drop-shadow(0 0 22px #F7CA18cc);
        text-shadow: 0 10px 36px #117A6588, 0 1px 0 #fff, 0 0 20px #F7CA18cc;
    }
    .school-subtitle {
        font-size: 1.3em;
        color: #F7CA18;
        font-weight: 700;
        margin-top: 0.2em;
        letter-spacing: 1.2px;
        text-shadow: 0 1px 0 #232946, 0 0 6px #2e86c13a;
        display: block;
    }
    .subtitle-anim {
        display: inline-block;
        animation: subtitleFadeIn 2s cubic-bezier(.4,0,.2,1);
    }
    .ribbon {
        display: inline-block;
        background: linear-gradient(90deg, #232946 0%, #117A65 100%);
        color: #F7CA18;
        font-family: 'Pacifico', cursive;
        font-size: 1.1em;
        padding: 0.2em 1.2em;
        border-radius: 18px;
        margin: 0.7em auto 0.2em auto;
        box-shadow: 0 2px 12px #23294699;
        letter-spacing: 1.5px;
        animation: ribbonPop 1.2s cubic-bezier(.4,0,.2,1);
        text-align: center;
        border: 1.5px solid #F7CA18;
    }
    .title-hr {
        margin-top: 10px;
        margin-bottom: 0;
        border: none;
        border-top: 2.5px dashed #F7CA18;
        width: 80%;
        opacity: 0.7;
        animation: hrGrow 1.2s cubic-bezier(.4,0,.2,1);
    }
    @keyframes titleSlideIn {
        from { opacity: 0; transform: translateY(-40px) scale(0.95); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    @keyframes shineMove {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    @keyframes subtitleFadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes hrGrow {
        from { width: 0; opacity: 0; }
        to { width: 80%; opacity: 0.7; }
    }
    @keyframes bounce {
        0% { transform: translateY(0);}
        100% { transform: translateY(-10px);}
    }
    @keyframes pulse {
        0% { filter: brightness(1);}
        50% { filter: brightness(1.3);}
        100% { filter: brightness(1);}
    }
    @keyframes sparkleTwinkle {
        0% { opacity: 1; filter: blur(0px); }
        100% { opacity: 0.5; filter: blur(2px); }
    }
    @keyframes ribbonPop {
        from { opacity: 0; transform: scale(0.7); }
        to { opacity: 1; transform: scale(1); }
    }
    @media (max-width: 600px) {
        .school-title-unique { font-size: 1.2em; }
        .school-subtitle { font-size: 0.95em; }
        .title-flex { gap: 8px; }
        .title-icon { width: 36px !important; }
        .ribbon { font-size: 0.9em; padding: 0.15em 0.7em; }
        .dark-main { padding: 1.2rem 0.5rem 1.2rem 0.5rem; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Interactive info box with icon and animation
st.info(
    "✨ **Upload the student fee data Excel file and send smart, personalized reminders to parents.**<br>"
    "💡 _Tip: You can preview the data, filter, and customize your message before sending!_",
    icon="ℹ️"
)

# Path to QR code image
QR_IMAGE_PATH = os.path.join(os.getcwd(), "QR Pay.png")

# ---------- STEP 1: Upload Excel or CSV ----------
uploaded_file = st.file_uploader("📂 **Upload Student Data File (Excel or CSV)**", type=["xlsx", "csv"])
df = None
if uploaded_file:
    with st.spinner("Processing your data..."):
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.success("File uploaded and data loaded successfully!")

    df.columns = df.columns.str.strip()
    st.write("Columns found:", list(df.columns))

    # Accept both possible column names
    dues_col = None
    if "Total Payment Dues" in df.columns:
        dues_col = "Total Payment Dues"
    elif "Total Payment Dues (₹)" in df.columns:
        dues_col = "Total Payment Dues (₹)"

    if "Email" not in df.columns or dues_col is None:
        st.error("Excel must contain 'Email' and 'Total Payment Dues' columns.")
    else:
        # Generate personalized payment links (dummy example)
        PAYMENT_BASE_URL = "https://pay.ambitionschool.com/pay?student_id="
        if "Student ID" in df.columns:
            df["Payment Link"] = df["Student ID"].apply(lambda sid: f"{PAYMENT_BASE_URL}{sid}")
        else:
            df["Payment Link"] = df["Student Name"].apply(lambda name: f"{PAYMENT_BASE_URL}{name.replace(' ', '').lower()}")

        # Optionally, generate QR codes for each payment link (requires qrcode library)
        import qrcode # type: ignore
        import base64

        def generate_qr_code_base64(link):
            qr = qrcode.make(link)
            buf = io.BytesIO()
            qr.save(buf, format="PNG")
            img_bytes = buf.getvalue()
            base64_img = base64.b64encode(img_bytes).decode()
            return f"data:image/png;base64,{base64_img}"

        df["Payment QR"] = df["Payment Link"].apply(generate_qr_code_base64)

        # ---------- 3. 🔍 Smart Filters & Search ----------
        st.header("🔍 Smart Filters & Search")

        filtered_df = df.copy()

        # Filter by Class
        if "Class" in df.columns:
            class_options = sorted(df["Class"].dropna().unique())
            selected_classes = st.multiselect("Filter by Class", class_options, default=class_options)
            filtered_df = filtered_df[filtered_df["Class"].isin(selected_classes)]

        # Filter by Due Amount Range
        min_due = int(df[dues_col].min())
        max_due = int(df[dues_col].max())
        due_range = st.slider("Filter by Due Amount Range (₹)", min_due, max_due, (min_due, max_due))
        filtered_df = filtered_df[(filtered_df[dues_col] >= due_range[0]) & (filtered_df[dues_col] <= due_range[1])]

        # Filter by City/Address
        city_col = None
        for col in ["City", "Address"]:
            if col in df.columns:
                city_col = col
                break
        city_query = st.text_input(f"Search by {city_col if city_col else 'City/Address'} (optional)").strip()
        if city_col and city_query:
            filtered_df = filtered_df[filtered_df[city_col].str.contains(city_query, case=False, na=False)]

        # Only show students with dues > 0
        due_df = filtered_df[filtered_df[dues_col] > 0].copy()

        # ---------- 1. 📊 Class-wise Fee Summary Dashboard ----------
        st.header("📊 Class-wise Fee Summary Dashboard")

        # Bar chart: Class vs Total Pending Fees
        if "Class" in filtered_df.columns:
            class_dues = filtered_df.groupby("Class")[dues_col].sum().reset_index()
            fig_class_dues = px.bar(
                class_dues,
                x="Class",
                y=dues_col,
                title="Class vs Total Pending Fees",
                labels={dues_col: "Total Pending Fees (₹)"}
            )
            st.plotly_chart(fig_class_dues, use_container_width=True)

            # Find worst performing class (max dues)
            worst_class_row = class_dues.loc[class_dues[dues_col].idxmax()]
            st.info(f"🔴 **Worst Performing Class:** {worst_class_row['Class']} (₹{worst_class_row[dues_col]:,.0f} pending)")

            # Pie chart: Class-wise distribution of defaulters
            defaulters_per_class = due_df.groupby("Class")["Student Name"].count().reset_index()
            defaulters_per_class = defaulters_per_class.rename(columns={"Student Name": "Defaulter Count"})
            fig_defaulters_pie = px.pie(
                defaulters_per_class,
                names="Class",
                values="Defaulter Count",
                title="Class-wise Distribution of Defaulters"
            )
            st.plotly_chart(fig_defaulters_pie, use_container_width=True)

        # ---------- 3. 🛠️ Edit Dues Manually Inside the App (Excel-Free Mode) ----------
        st.header("🛠️ Edit Dues Manually (Excel-Free Mode)")

        # Show editable table for all students (filtered_df)
        if "Student Name" in filtered_df.columns and dues_col:
            st.markdown("You can edit the dues directly below. Changes are saved in real time (session only).")
            edited_df = st.data_editor(
                filtered_df,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    dues_col: st.column_config.NumberColumn(
                        "Total Payment Dues",
                        min_value=0,
                        step=1,
                        format="₹{:.0f}"
                    )
                },
                key="editable_dues"
            )
            # Update the filtered_df and due_df with the edited values
            filtered_df = edited_df
            due_df = filtered_df[filtered_df[dues_col] > 0].copy()
        else:
            st.warning("Cannot enable editing: 'Student Name' or dues column missing.")

        # ---------- 1. 📊 Real-Time Dashboard Analytics ----------
        st.header("📊 Real-Time Dashboard Analytics")

        col1, col2, col3 = st.columns(3)
        col1.metric("🔢 Total Students", len(filtered_df))
        col2.metric("💰 Total Fee Pending (₹)", f"₹{filtered_df[dues_col].sum():,.0f}")
        col3.metric("🧑‍🎓 Number of Defaulters", len(due_df))

        # 📚 Class-wise Dues (Bar Chart)
        if "Class" in filtered_df.columns:
            class_dues = filtered_df.groupby("Class")[dues_col].sum().reset_index()
            fig_class = px.bar(class_dues, x="Class", y=dues_col, title="Class-wise Dues (₹)", labels={dues_col: "Total Dues (₹)"})
            st.plotly_chart(fig_class, use_container_width=True)

        # 📍 City-wise Dues (Pie Chart)
        if "City" in filtered_df.columns:
            city_dues = filtered_df.groupby("City")[dues_col].sum().reset_index()
            fig_city = px.pie(city_dues, names="City", values=dues_col, title="City-wise Dues (₹)")
            st.plotly_chart(fig_city, use_container_width=True)

        st.success(f"{len(due_df)} students have pending dues.")
        st.dataframe(due_df)

        # --- Student Profile Drilldown ---
        st.subheader("🧑‍🎓 Student Profile Drilldown")
        student_names = due_df["Student Name"].unique()
        selected_student = st.selectbox("Select a student to view profile", student_names)
        if selected_student:
            profile = due_df[due_df["Student Name"] == selected_student].iloc[0]
            st.markdown(f"### Profile: {profile['Student Name']}")
            st.write(f"**Class:** {profile['Class']}")
            st.write(f"**Parent Email:** {profile['Email']}")
            if 'Phone' in profile:
                st.write(f"**Parent Phone:** {profile['Phone']}")
            st.write(f"**Total Payment Dues:** ₹{profile[dues_col]:,.0f}")
            if "Past Delay Count" in profile:
                st.write(f"**Past Delay Count:** {profile['Past Delay Count']}")
            if "Payment Link" in profile:
                st.markdown(f"**Payment Link:** [Pay Now]({profile['Payment Link']})")
            if "Payment QR" in profile:
                st.markdown("**Scan to Pay:**")
                st.image(profile["Payment QR"])
            # Payment history & dues trend (if you have monthly columns)
            payment_cols = [col for col in due_df.columns if "Month" in col or "Paid" in col]
            if payment_cols:
                st.write("**Payment History:**")
                st.write(profile[payment_cols])
                st.line_chart(profile[payment_cols])
            # Communication log (from email_log)
            if "email_log" in st.session_state:
                comm_log = pd.DataFrame(st.session_state.email_log)
                if "Student Name" in comm_log.columns:
                    comm_log = comm_log[comm_log["Student Name"] == selected_student]
                    if not comm_log.empty:
                        st.write("**Communication Log:**")
                        st.dataframe(comm_log)
                    else:
                        st.info("No communication log found for this student.")
                else:
                    st.info("No communication log found for this student.")

        # ---------- STEP 2: Email Credentials ----------
        st.header("🔐 Email Configuration")
        sender_email = st.text_input("Enter your Gmail address", value="ambitionschool.notice@gmail.com", help="Use a Gmail address with App Password enabled.")
        sender_password = st.text_input("Enter your Gmail app password", type="password", help="Generate an App Password from your Google Account Security settings.")

        # ---------- 5. 📧 Dynamic Email Personalization with Templates ----------
        st.header("📧 Email Template Selection & Preview")

        # Add language selector
        language = st.selectbox("Choose Language", ["English", "Hindi", "Marathi", "Maithili"])

        def get_email_templates(language):
            if language == "Maithili":
                return {
                    "Standard Reminder": (
                        "जरूरी: {student_name} लेल फीस बकाया सूचना",
                        """आदरणीय अभिभावक,

अहाँक बच्चा **{student_name}** (कक्षा **{student_class}**) केर स्कूल फीस अबधि तक जमा नै भेल अछि।

🧾 **बकाया राशि**: ₹{due_amount}

कृपया शीघ्र फीस जमा करू। धन्यवाद。
**Ambition Public School**
"""
                    ),
                    "Junior Student Friendly": (
                        "फीस स्मरण: {student_name} (जूनियर सेक्शन)",
                        """प्रिय अभिभावक,

आशा अछि जे अहाँक बच्चा, **{student_name}** (कक्षा **{student_class}**), स्कूल में पढ़ाई के आनंद ल' रहल छथि!

हमर रिकॉर्ड अनुसार, **₹{due_amount}** के बकाया राशि अछि। कृपया शीघ्र फीस जमा करू ताकि स्कूल गतिविधि में बाधा नै आबय।

अहाँक त्वरित ध्यान लेल धन्यवाद।

सादर,  
**Ambition Public School**
"""
                    ),
                    "Senior Section Strict": (
                        "अंतिम सूचना: {student_name} लेल फीस बकाया (सीनियर सेक्शन)",
                        """प्रिय अभिभावक,

ई अंतिम सूचना अछि जे **{student_name}** (कक्षा **{student_class}**) केर फीस बकाया अछि।

🧾 **बकाया राशि**: ₹{due_amount}

कृपया तुरंत फीस जमा करू, अन्यथा अगिला कार्रवाई कएल जा सकैत अछि। यदि अहाँ फीस जमा क' चुकल छी, त' कृपया ई सूचना नजरअंदाज करू।

सादर,  
**Ambition Public School**
"""
                    ),
                }
            elif language == "Hindi":
                return {
                    "Standard Reminder": (
                        "महत्वपूर्ण: {student_name} के लिए शुल्क बकाया सूचना",
                        """आदरणीय अभिभावक,

आपके बच्चे **{student_name}** (कक्षा **{student_class}**) की स्कूल फीस अभी बकाया है।

🧾 **बकाया राशि**: ₹{due_amount}

कृपया शीघ्र भुगतान करें। धन्यवाद।
**Ambition Public School**
"""
                    ),
                    "Junior Student Friendly": (
                        "शुल्क याददाश्त: {student_name} (जूनियर सेक्शन)",
                        """प्रिय अभिभावक,

हमें आशा है कि आपका बच्चा, **{student_name}** (कक्षा **{student_class}**), हमारे साथ अपनी सीखने की यात्रा का आनंद ले रहा है!

हमारे रिकॉर्ड के अनुसार, **₹{due_amount}** की एक बकाया राशि है। कृपया सुनिश्चित करें कि शुल्क जल्द से जल्द भरा जाए ताकि स्कूल गतिविधियों में कोई रुकावट न आए।

आपकी त्वरित ध्यान देने के लिए धन्यवाद।

सादर,  
**Ambition Public School**
"""
                    ),
                    "Senior Section Strict": (
                        "अंतिम सूचना: {student_name} के लिए शुल्क बकाया (सीनियर सेक्शन)",
                        """प्रिय अभिभावक/अभिभाविका,

यह **{student_name}** (कक्षा **{student_class}**) के लिए बकाया शुल्क के संबंध में अंतिम अनुस्मारक है।

🧾 **बकाया राशि**: ₹{due_amount}

कृपया ध्यान दें कि तत्काल भुगतान आवश्यक है अन्यथा आगे की कार्रवाई की जा सकती है। यदि आपने पहले ही भुगतान कर दिया है, तो कृपया इस सूचना को नजरअंदाज करें।

सादर,  
**Ambition Public School**
"""
                    ),
                }
            elif language == "Marathi":
                return {
                    "Standard Reminder": (
                        "{student_name} साठी शुल्क थकबाकीची सूचना",
                        """आदरणीय पालक,

आपल्या मुलाचे **{student_name}** (इयत्ता **{student_class}**) शाळेचे शुल्क थकबाकी आहे.

🧾 **थकबाकी रक्कम**: ₹{due_amount}

कृपया लवकरात लवकर शुल्क भरा. धन्यवाद.
**Ambition Public School**
"""
                    ),
                    "Junior Student Friendly": (
                        "शुल्क याददाश्त: {student_name} (जूनियर सेक्शन)",
                        """प्रिय पालक,

आपल्या लहानग्या मित्रा/मित्रिणीचा, **{student_name}** (इयत्ता **{student_class}**), आमच्यासोबत शिकण्याच्या प्रवासाचा आनंद घेत असल्याची आशा आहे!

आमच्या रेकॉर्डनुसार, **₹{due_amount}** ची एक थकबाकी रक्कम आहे. कृपया लवकरात लवकर थकबाकी भरण्यासाठी सुनिश्चित करा जेणेकरून शाळेच्या क्रियाकलापांमध्ये कोणतीही अडचण येऊ नये.

आपल्या त्वरित लक्षासाठी धन्यवाद.

सादर,  
**Ambition Public School**
"""
                    ),
                    "Senior Section Strict": (
                        "अंतिम सूचना: {student_name} साठी शुल्क थकबाकी (सीनियर सेक्शन)",
                        """प्रिय पालक/पालकिणी,

ही **{student_name}** (इयत्ता **{student_class}**) साठी थकबाकी शुल्काबद्दलची अंतिम सूचना आहे.

🧾 **बकाया रक्कम**: ₹{due_amount}

कृपया तात्काळ भुगतान आवश्यक आहे अन्यथा पुढील कारवाई केली जाईल. जर आपण आधीच भुगतान केले असेल, तर कृपया या सूचनेकडे दुर्लक्ष करा.

सादर,  
**Ambition Public School**
"""
                    ),
                }
            else:
                return {
                    "Standard Reminder": (
                        "Urgent: Fee Due Reminder for {student_name}",
                        """Dear Parent/Guardian,

This is a reminder that the school fee for your child, **{student_name}**, studying in Class **{student_class}**, is still unpaid.

🧾 **Outstanding Amount**: ₹{due_amount}

Please clear the dues at the earliest to avoid a **daily penalty**. Timely payment ensures your child continues to receive academic support.

If you've already paid, kindly ignore this message.

Warm regards,  
**Ambition Public School**
"""
                    ),
                    "Junior Student Friendly": (
                        "Fee Reminder for {student_name} (Junior Section)",
                        """Dear Parent,

We hope your little one, **{student_name}** (Class **{student_class}**), is enjoying their learning journey with us!

Our records show a pending fee of **₹{due_amount}**. Kindly clear the dues soon to ensure uninterrupted participation in school activities.

Thank you for your prompt attention.

Best wishes,  
**Ambition Public School**
"""
                    ),
                    "Senior Section Strict": (
                        "Final Notice: Fee Due for {student_name} (Senior Section)",
                        """Dear Parent/Guardian,

This is a final reminder regarding the outstanding fee for **{student_name}** (Class **{student_class}**).

🧾 **Amount Due**: ₹{due_amount}

Immediate payment is required to avoid further action. Please disregard this notice if payment has already been made.

Sincerely,  
**Ambition Public School**
"""
                    ),
                }

        templates = get_email_templates(language)
        template_names = list(templates.keys())
        selected_template = st.selectbox("Choose Email Template", template_names)

        # Optionally, auto-select template based on class (junior/senior)
        junior_classes = ["Nursery", "KG", "Prep", "1", "2", "3", "4", "5"]
        senior_classes = ["9", "10", "11", "12"]

        # Preview for the first student in due_df
        preview_row = None
        if not due_df.empty:
            preview_row = due_df.iloc[0]
            # Auto-select template if enabled
            if str(preview_row["Class"]) in junior_classes:
                auto_template = "Junior Student Friendly"
            elif str(preview_row["Class"]) in senior_classes:
                auto_template = "Senior Section Strict"
            else:
                auto_template = "Standard Reminder"
            # If admin wants auto, uncomment below:
            # selected_template = auto_template

            subject_template, body_template = templates[selected_template]
            preview_subject = subject_template.format(
                student_name=preview_row["Student Name"],
                student_class=preview_row["Class"],
                due_amount=preview_row[dues_col]
            )
            preview_body = body_template.format(
                student_name=preview_row["Student Name"],
                student_class=preview_row["Class"],
                due_amount=preview_row[dues_col]
            )
            st.subheader("📄 Email Preview")
            st.markdown(f"**Subject:** {preview_subject}")
            st.markdown(preview_body)

        # ---------- 2. 📥 Sent Email Log with Download Option ----------
        if "email_log" not in st.session_state:
            st.session_state.email_log = []

        # ---------- 4. 📱 SMS Alert System Integration ----------
        st.header("📱 SMS Alert System (Fast2SMS)")

        send_sms = st.checkbox("Also send SMS alerts to parents' mobile numbers (India only)")
        sms_message_template = st.text_area(
            "SMS Message Template (use {student_name}, {student_class}, {due_amount})",
            value="Dear Parent, Fee due for {student_name} (Class {student_class}): ₹{due_amount}. Please pay soon. - Ambition School"
        )

        # Optionally, let user select the phone column
        phone_col = None
        for col in ["Phone", "Mobile", "Parent Phone", "Parent Mobile"]:
            if col in df.columns:
                phone_col = col
                break
        if send_sms and not phone_col:
            st.warning("No phone number column found in your Excel. Please ensure a column named 'Phone', 'Mobile', 'Parent Phone', or 'Parent Mobile' exists.")

        # Add your Fast2SMS API key here (for demo, use env variable or config in production)
        FAST2SMS_API_KEY = "RF2uxDjgks3PndJLweQTA4chSoEZCiazGN0tmblHfWyM6V8BOUA9wu6baJPNUvjLc4BXy5KS8de1ihxl"

        def send_sms_via_fast2sms(phone, message):
            url = "https://www.fast2sms.com/dev/bulkV2"
            headers = {
                "authorization": FAST2SMS_API_KEY
            }
            payload = {
                "route": "q",
                "message": message,
                "language": "english",
                "flash": 0,
                "numbers": phone
            }
            try:
                response = requests.post(url, headers=headers, data=payload)
                # Debug: print response for troubleshooting
                print("Fast2SMS response:", response.status_code, response.text)
                if response.status_code == 200 and response.json().get("return"):
                    return "Success", ""
                else:
                    return "Failed", response.text
            except Exception as e:
                return "Failed", str(e)

        if st.button("🚀 Send Warning Emails"):
            if not sender_email or not sender_password:
                st.error("Please enter your email and password.")
            else:
                try:
                    # No need to create yagmail.SMTP instance
                    with st.spinner("Sending emails and SMS..."):
                        success_count = 0
                        sms_success_count = 0
                        email_log = []
                        for _, row in due_df.iterrows():
                            # Auto-select template based on class
                            if str(row["Class"]) in junior_classes:
                                template_key = "Junior Student Friendly"
                            elif str(row["Class"]) in senior_classes:
                                template_key = "Senior Section Strict"
                            else:
                                template_key = selected_template
                            subject_template, body_template = templates[template_key]
                            subject = subject_template.format(
                                student_name=row["Student Name"],
                                student_class=row["Class"],
                                due_amount=row[dues_col]
                            )
                            payment_link = row.get("Payment Link", "")
                            body = body_template.format(
                                student_name=row["Student Name"],
                                student_class=row["Class"],
                                due_amount=row[dues_col]
                            )
                            if payment_link:
                                body += f"\n\n[Click here to pay now]({payment_link})"
                            status = "Success"
                            error_msg = ""
                            sms_status = ""
                            sms_error = ""
                            try:
                                # Send email with QR code attachment if available
                                qr_base64 = row.get("Payment QR", None)
                                if qr_base64:
                                    send_email_with_qr(
                                        to=row["Email"],
                                        subject=subject,
                                        body=body,
                                        qr_base64=qr_base64
                                    )
                                else:
                                    send_email(
                                        to=row["Email"],
                                        subject=subject,
                                        body=body
                                    )
                                success_count += 1
                            except Exception as e:
                                status = "Failed"
                                error_msg = str(e)
                                st.error(f"Failed to send email to {row['Email']} – {e}")

                            # Send SMS if enabled and phone column exists
                            if send_sms and phone_col and pd.notna(row[phone_col]):
                                # Clean phone number: remove spaces, +, -, country code, etc.
                                phone_str = str(row[phone_col])
                                phone_digits = ''.join(filter(str.isdigit, phone_str))
                                # Remove country code if present (assume Indian numbers)
                                if phone_digits.startswith('91') and len(phone_digits) > 10:
                                    phone_digits = phone_digits[-10:]
                                # Now check if it's a valid 10-digit number
                                if len(phone_digits) == 10:
                                    sms_message = sms_message_template.format(
                                        student_name=row["Student Name"],
                                        student_class=row["Class"],
                                        due_amount=row[dues_col]
                                    )
                                    sms_status, sms_error = send_sms_via_fast2sms(phone_digits, sms_message)
                                    if sms_status == "Success":
                                        sms_success_count += 1
                                    else:
                                        st.error(f"Failed to send SMS to {phone_digits} – {sms_error}")
                                else:
                                    st.error(f"Invalid phone number format: {row[phone_col]}")

                            email_log.append({
                                "Date-Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "Status": status,
                                "Student Name": row["Student Name"],
                                "Parent Email": row["Email"],
                                "Parent Phone": row[phone_col] if phone_col and pd.notna(row[phone_col]) else "",
                                "SMS Status": sms_status,
                                "SMS Error": sms_error,
                                "Error": error_msg
                            })
                        st.session_state.email_log = email_log
                    st.success(f"✅ Emails sent successfully to {success_count} parents.")
                    if send_sms and phone_col:
                        st.success(f"✅ SMS sent successfully to {sms_success_count} parents.")
                except Exception as e:
                    st.error(f"❌ Failed to connect to email server: {e}")

        # Show Email Log Table & Download Option
        if st.session_state.get("email_log"):
            st.header("📥 Sent Email/SMS Log")
            log_df = pd.DataFrame(st.session_state.email_log)
            display_cols = ["Date-Time", "Status", "Student Name", "Parent Email"]
            if "Parent Phone" in log_df.columns:
                display_cols.append("Parent Phone")
            st.dataframe(log_df[display_cols])

            # Download option
            csv = log_df.to_csv(index=False)
            st.download_button(
                "📥 Download Log as CSV",
                csv,
                "email_sms_log.csv",
                "text/csv",
                key="download-csv"
            )

        # ---------- Predictive Analytics: Advanced Fee Defaulter Predictor ----------
        st.header("🤖 Predictive Analytics: Fee Defaulter Risk (Advanced)")

        required_ai_cols = ["Past Delay Count", "Class", dues_col]
        ai_ready = all(col in df.columns for col in required_ai_cols)
        if not ai_ready:
            st.warning("To use the predictor, your Excel must have columns: Past Delay Count, Class, and Total Payment Dues.")
        else:
            # Prepare features
            ai_df = df.copy()
            # Encode class as number
            le = LabelEncoder()
            ai_df["Class_encoded"] = le.fit_transform(ai_df["Class"].astype(str))
            # Feature engineering: you can add more features here
            features = ["Past Delay Count", "Class_encoded", dues_col]
            if "City" in ai_df.columns:
                le_city = LabelEncoder()
                ai_df["City_encoded"] = le_city.fit_transform(ai_df["City"].astype(str))
                features.append("City_encoded")
            X = ai_df[features]
            # If Defaulter column exists, use it; else, simulate
            if "Defaulter" in ai_df.columns:
                y = ai_df["Defaulter"]
            else:
                y = ((ai_df["Past Delay Count"] > 0) & (ai_df[dues_col] > 0)).astype(int)
            # Train/test split
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            # Advanced ML model: RandomForest (can be replaced with XGBoost, etc.)
            clf = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)
            clf.fit(X_train, y_train)
            # Predict risk for all students
            ai_df["Defaulter_Risk_Score"] = clf.predict_proba(X)[:,1]
            ai_df["High_Risk"] = ai_df["Defaulter_Risk_Score"] > 0.5

            # --- Interactive Filtering/Sorting ---
            st.subheader("🎯 Filter & Sort by Defaulter Risk Score")
            min_risk, max_risk = float(ai_df["Defaulter_Risk_Score"].min()), float(ai_df["Defaulter_Risk_Score"].max())
            risk_range = st.slider("Select risk score range", 0.0, 1.0, (0.5, 1.0), step=0.01)
            filtered_risk_df = ai_df[(ai_df["Defaulter_Risk_Score"] >= risk_range[0]) & (ai_df["Defaulter_Risk_Score"] <= risk_range[1])]
            sort_by = st.selectbox("Sort by", ["Defaulter_Risk_Score", dues_col, "Past Delay Count"], index=0)
            filtered_risk_df = filtered_risk_df.sort_values(sort_by, ascending=False)

            st.write(f"Showing {len(filtered_risk_df)} students with risk score in selected range.")
            st.dataframe(filtered_risk_df[["Student Name", "Class", dues_col, "Past Delay Count", "Defaulter_Risk_Score", "High_Risk"]])

            # Show top 10 high-risk students
            st.subheader("🚨 Top 10 High-Risk Students Likely to Default Next Month")
            st.write("These students have a high predicted risk of fee delay next month. Consider calling their parents proactively.")
            st.dataframe(filtered_risk_df[["Student Name", "Class", dues_col, "Past Delay Count", "Defaulter_Risk_Score"]].head(10))

            # Recommendations
            if not filtered_risk_df.empty:
                st.info(f"Recommendation: Call the parents of these {min(10, len(filtered_risk_df))} students for early fee reminders.")

            # Visualize risk distribution
            st.subheader("📊 Risk Score Distribution")
            fig_risk = px.histogram(ai_df, x="Defaulter_Risk_Score", nbins=20, title="Distribution of Defaulter Risk Scores")
            st.plotly_chart(fig_risk, use_container_width=True)

        # ---------- EDA: Exploratory Data Analysis ----------
        st.header("📈 Exploratory Data Analysis (EDA)")

        if st.checkbox("Show Data Overview"):
            st.subheader("Data Overview")
            st.write(df.describe(include='all'))

        if st.checkbox("Show Missing Values"):
            st.subheader("Missing Values")
            st.write(df.isnull().sum())

        if st.checkbox("Show Sample Data"):
            st.subheader("Sample Data")
            st.write(df.head(10))

        # Interactive: Select column for distribution plot
        st.subheader("📊 Column Distribution")
        eda_col = st.selectbox("Select column to visualize distribution", df.select_dtypes(include=['number', 'object']).columns)
        if eda_col:
            if pd.api.types.is_numeric_dtype(df[eda_col]):
                st.bar_chart(df[eda_col].value_counts().sort_index())
            else:
                st.bar_chart(df[eda_col].value_counts())

        # Correlation heatmap for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 1 and st.checkbox("Show Correlation Heatmap"):
            st.subheader("Correlation Heatmap")
            fig, ax = plt.subplots()
            sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="Blues", ax=ax)
            st.pyplot(fig)

        # Pie chart for categorical columns
        cat_cols = df.select_dtypes(include=['object']).columns
        cat_col = st.selectbox("Select categorical column for pie chart", cat_cols)
        if cat_col:
            st.subheader(f"Pie Chart: {cat_col}")
            pie_data = df[cat_col].value_counts()
            fig_pie = px.pie(values=pie_data.values, names=pie_data.index, title=f"Distribution of {cat_col}")
            st.plotly_chart(fig_pie, use_container_width=True)

        # Scatter plot for two numeric columns
        if len(numeric_cols) >= 2:
            st.subheader("Scatter Plot")
            x_col = st.selectbox("X-axis", numeric_cols, key="scatter_x")
            y_col = st.selectbox("Y-axis", numeric_cols, key="scatter_y")
            if x_col and y_col:
                fig_scatter = px.scatter(df, x=x_col, y=y_col, color="Class" if "Class" in df.columns else None,
                                     title=f"{x_col} vs {y_col}")
                st.plotly_chart(fig_scatter, use_container_width=True)

        # ---------- Feature Engineering Example ----------
        st.header("🛠️ Feature Engineering")
        if st.button("Add Features"):
            df['Is_High_Due'] = df[dues_col] > df[dues_col].mean()
            st.write("Added 'Is_High_Due' column (True if dues above average).")
            st.write(df[['Student Name', dues_col, 'Is_High_Due']].head())

    # ---------- Bulk Edit All Student Data ----------
    st.header("📝 Bulk Edit Student Data (All Columns)")
    st.markdown("Edit any field below. Changes are session-only unless exported.")
    edited_bulk_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        key="bulk_edit_all"
    )
    df = edited_bulk_df

    # ---------- Export Filtered/Edited Data ----------
    st.header("⬇️ Export Data (Excel, CSV, PDF)")
    # Export as Excel
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)
    st.download_button(
        label="Download as Excel (.xlsx)",
        data=excel_buffer.getvalue(),
        file_name="student_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    # Export as CSV
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download as CSV",
        data=csv_data,
        file_name="student_data.csv",
        mime="text/csv"
    )
    # Export as PDF (simple table)
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=8)
        col_width = pdf.w / (len(df.columns) + 1)
        row_height = pdf.font_size * 1.5
        # Helper function to clean text for PDF
        def clean_text_for_pdf(text):
            if isinstance(text, str):
                # Replace rupee symbol and remove other non-latin1 chars
                text = text.replace("₹", "Rs.")
                return text.encode('latin1', 'replace').decode('latin1')
            return str(text)
        # Header
        for col in df.columns:
            pdf.cell(col_width, row_height, clean_text_for_pdf(str(col)), border=1)
        pdf.ln(row_height)
        # Rows (limit to 30 for performance)
        for i, row in df.head(30).iterrows():
            for item in row:
                pdf.cell(col_width, row_height, clean_text_for_pdf(item), border=1)
            pdf.ln(row_height)
        pdf_buffer = pdf.output(dest='S').encode('latin1')
        st.download_button(
            label="Download as PDF (first 30 rows)",
            data=pdf_buffer,
            file_name="student_data.pdf",
            mime="application/pdf"
        )
    except ImportError:
        st.info("Install 'fpdf' package to enable PDF export: pip install fpdf")

# Place this function ONCE, before use
def send_sms_via_fast2sms(phone, message):
    url = "https://www.fast2sms.com/dev/bulkV2"
    headers = {
        "authorization": FAST2SMS_API_KEY
    }
    payload = {
        "route": "q",
        "message": message,
        "language": "english",
        "flash": 0,
        "numbers": phone
    }
    try:
        response = requests.post(url, headers=headers, data=payload)
        # Debug: print response for troubleshooting
        print("Fast2SMS response:", response.status_code, response.text)
        if response.status_code == 200 and response.json().get("return"):
            return "Success", ""
        else:
            return "Failed", response.text
    except Exception as e:
        return "Failed", str(e)


# ------------------- New Student Admission Data Collection -------------------
with st.expander("NEW ADMISSION", expanded=False):
    st.markdown(
        """
        <div style="background: linear-gradient(90deg, #232946 0%, #117A65 100%); border-radius: 18px; box-shadow: 0 2px 12px #117A6588; padding: 1.2em 1.5em; margin-bottom: 1.2em; color: #F7CA18;">
            <b>Register a new student for admission:</b> <br>
            <span style="color:#fff; font-size:1.05em;">All fields are required. Data is not saved until you click <b>Submit Admission</b>.</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    if "admission_list" not in st.session_state:
        st.session_state.admission_list = []
    if "admission_approval" not in st.session_state:
        st.session_state.admission_approval = []

    with st.form("admission_form"):
        col1, col2 = st.columns(2)
        with col1:
            admission_student_name = st.text_input("👦 Student Name", key="admission_student_name")
            admission_father_name = st.text_input("👨 Father's Name", key="admission_father_name")
            admission_mother_name = st.text_input("👩 Mother's Name", key="admission_mother_name")
            admission_class = st.text_input("🏫 Class", key="admission_class")
        with col2:
            admission_address = st.text_area("🏠 Address", key="admission_address")
            admission_parent_number = st.text_input("📱 Parent's Mobile Number", key="admission_parent_number")
            admission_reg_fee = st.number_input("💸 Registration Fee Payment (₹)", min_value=0, step=1, key="admission_reg_fee")
        admission_submitted = st.form_submit_button(
            label="✨ Submit Admission",
            help="Click to add this student to the admission dashboard."
        )
        if (
            admission_submitted
            and admission_student_name
            and admission_father_name
            and admission_mother_name
            and admission_address
            and admission_class
            and admission_parent_number
            and admission_reg_fee > 0
        ):
            # Add to pending approval list
            st.session_state.admission_approval.append({
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Student Name": admission_student_name,
                "Father's Name": admission_father_name,
                "Mother's Name": admission_mother_name,
                "Address": admission_address,
                "Class": admission_class,
                "Parent's Mobile Number": admission_parent_number,
                "Registration Fee Payment (₹)": admission_reg_fee,
                "Status": "Pending",
                "Admin Comment": ""
            })
            st.success("🎉 Admission submitted for approval! Waiting for admin action.")
        elif admission_submitted:
            st.error("❌ Please fill all fields and enter a valid registration fee.")

    # Admin Approval Workflow
    st.markdown("<div style='background: linear-gradient(90deg, #117A65 0%, #2E86C1 100%); border-radius: 14px; box-shadow: 0 2px 12px #2e86c13a; padding: 0.7em 1.2em; margin-bottom: 0.7em; color: #fff; font-weight:600; font-size:1.1em;'>🛡️ <b>Admission Approval Dashboard (Admin Only)</b></div>", unsafe_allow_html=True)
    if st.session_state.admission_approval:
        approval_df = pd.DataFrame(st.session_state.admission_approval)
        for idx, row in approval_df[approval_df["Status"]=="Pending"].iterrows():
            with st.expander(f"Pending: {row['Student Name']} ({row['Class']})", expanded=False):
                st.write(row)
                admin_action = st.radio(f"Approve or Reject {row['Student Name']}?", ["Approve", "Reject"], key=f"admin_action_{idx}")
                admin_comment = st.text_area("Admin Comment (optional)", key=f"admin_comment_{idx}")
                if st.button(f"Submit Decision for {row['Student Name']}", key=f"decision_{idx}"):
                    st.session_state.admission_approval[idx]["Status"] = "Approved" if admin_action=="Approve" else "Rejected"
                    st.session_state.admission_approval[idx]["Admin Comment"] = admin_comment
                    if admin_action=="Approve":
                        st.session_state.admission_list.append(st.session_state.admission_approval[idx])
                    st.success(f"{row['Student Name']} has been {admin_action.lower()}d.")

    # Show admission dashboard (approved only)
    if st.session_state.admission_list:
        st.markdown(
            """
            <div style="background: linear-gradient(90deg, #117A65 0%, #2E86C1 100%); border-radius: 14px; box-shadow: 0 2px 12px #2e86c13a; padding: 0.7em 1.2em; margin-bottom: 0.7em; color: #fff; font-weight:600; font-size:1.1em;">
                📋 <b>New Admission Dashboard (Approved)</b>
            </div>
            """,
            unsafe_allow_html=True
        )
        admission_df = pd.DataFrame(st.session_state.admission_list)
        st.dataframe(admission_df, use_container_width=True, hide_index=True)
        csv_admission = admission_df.to_csv(index=False)
        st.download_button(
            "⬇️ Download Admission Data as CSV",
            csv_admission,
            "new_admissions.csv",
            "text/csv",
            key="download-admission-csv"
        )

# --- Automated Fee Receipt Generation ---
def clean_text_for_pdf(text):
    if isinstance(text, str):
        # Replace rupee symbol and other non-latin1 chars
        text = text.replace("₹", "Rs.")
        return text.encode('latin1', 'replace').decode('latin1')
    return str(text)

def generate_fee_receipt_pdf(student_row):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=clean_text_for_pdf("Ambition Public School - Fee Receipt"), ln=True, align="C")
    pdf.ln(10)
    for k, v in student_row.items():
        pdf.cell(0, 10, txt=clean_text_for_pdf(f"{k}: {v}"), ln=True)
    pdf.ln(10)
    pdf.cell(0, 10, txt=clean_text_for_pdf("Thank you for your payment!"), ln=True)
    return pdf.output(dest='S').encode('latin1')

# Show/download receipts from dashboard
if df is not None and 'Payment Link' in df.columns and 'Email' in df.columns:
    with st.expander("Download Fee Receipts", expanded=False):
        st.header("Download Fee Receipts")
        for idx, row in df.iterrows():
            if row.get('Payment Link') and row.get('Email'):
                if st.button(f"Generate Receipt for {row['Student Name']}", key=f"receipt_{idx}"):
                    pdf_bytes = generate_fee_receipt_pdf(row)
                    st.download_button(
                        label=f"Download PDF Receipt for {row['Student Name']}",
                        data=pdf_bytes,
                        file_name=f"fee_receipt_{row['Student Name'].replace(' ','_')}.pdf",
                        mime="application/pdf",
                        key=f"download_receipt_{idx}"
                    )

# Email PDF receipt after payment (simulate after sending email)
def send_email_with_receipt(to, subject, body, pdf_bytes):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = st.secrets["email"]["user"]
    msg['To'] = to
    msg.set_content(body)
    msg.add_attachment(pdf_bytes, maintype='application', subtype='pdf', filename='fee_receipt.pdf')
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(st.secrets["email"]["user"], st.secrets["email"]["password"])
        smtp.send_message(msg)
