import streamlit as st
from inference_sdk import InferenceHTTPClient
from PIL import Image, ImageDraw, ImageFont, ImageOps
import tempfile
import os
from datetime import datetime
import pandas as pd


# =========================================================
# ROADGUARD AI
# =========================================================

MODEL_ID = "pathole-iokdb-gklme/1"
API_URL = "https://serverless.roboflow.com"


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="RoadGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# SESSION STATE
# =========================================================

if "history" not in st.session_state:
    st.session_state.history = []

if "reports" not in st.session_state:
    st.session_state.reports = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "last_image" not in st.session_state:
    st.session_state.last_image = None


# =========================================================
# PROFESSIONAL UI
# =========================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at top left, #eaf4ff 0%, transparent 35%),
        radial-gradient(circle at bottom right, #eef2ff 0%, transparent 35%),
        #f8fafc;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #07152f 0%, #0b2348 100%);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Main title */

.main-title {
    font-size: 48px;
    font-weight: 800;
    text-align: center;
    margin-top: 10px;
    margin-bottom: 5px;
    letter-spacing: -1px;
}

.main-subtitle {
    text-align: center;
    font-size: 18px;
    color: #64748b;
    margin-bottom: 35px;
}

/* Hero */

.hero {
    padding: 45px 30px;
    border-radius: 25px;
    background: linear-gradient(135deg, #07152f, #164e9a);
    color: white;
    text-align: center;
    box-shadow: 0 15px 40px rgba(15, 23, 42, 0.18);
    margin-bottom: 30px;
}

.hero h1 {
    font-size: 52px;
    margin-bottom: 8px;
}

.hero p {
    font-size: 20px;
    opacity: 0.9;
}

/* Cards */

.feature-card {
    background: white;
    padding: 25px;
    border-radius: 20px;
    min-height: 170px;
    box-shadow: 0 8px 25px rgba(15, 23, 42, 0.08);
    border: 1px solid #e2e8f0;
    transition: 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(15, 23, 42, 0.14);
}

.feature-card h2 {
    margin-bottom: 12px;
}

.feature-card p {
    color: #64748b;
    line-height: 1.6;
}

/* Metric cards */

.metric-card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 6px 20px rgba(15,23,42,0.07);
    text-align: center;
}

.metric-number {
    font-size: 32px;
    font-weight: 800;
    color: #0f3d78;
}

.metric-label {
    color: #64748b;
    font-size: 14px;
}

/* Section titles */

.section-title {
    font-size: 30px;
    font-weight: 750;
    margin-bottom: 8px;
}

.section-subtitle {
    color: #64748b;
    margin-bottom: 25px;
}

/* Scan animation */

.scan-box {
    padding: 20px;
    border-radius: 15px;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    text-align: center;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0% { opacity: 0.65; }
    50% { opacity: 1; }
    100% { opacity: 0.65; }
}

/* Status */

.status-safe {
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    color: #047857;
    padding: 15px;
    border-radius: 15px;
    text-align: center;
    font-weight: 700;
}

.status-warning {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    color: #c2410c;
    padding: 15px;
    border-radius: 15px;
    text-align: center;
    font-weight: 700;
}

/* Footer */

.footer {
    text-align: center;
    color: #94a3b8;
    padding: 35px 0 10px 0;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center; padding:15px 0 25px 0;">
            <div style="font-size:55px;">🛡️</div>
            <h2 style="margin-bottom:0;">RoadGuard AI</h2>
            <p style="opacity:0.75;">Smarter Roads. Safer Journeys.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "🏠 Home",
            "🔍 Detect",
            "📊 Dashboard",
            "🕘 History",
            "📍 Report",
            "ℹ️ About"
        ]
    )

    st.markdown("---")

    st.caption("AI-Powered Road Monitoring")
    st.caption("YOLO26s • Computer Vision")


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_confidence(prediction):
    value = prediction.get("confidence", 0)

    try:
        return float(value)
    except:
        return 0.0


def draw_predictions(image, predictions):

    image = image.copy()

    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()

    for prediction in predictions:

        x = prediction.get("x", 0)
        y = prediction.get("y", 0)
        width = prediction.get("width", 0)
        height = prediction.get("height", 0)

        confidence = get_confidence(prediction)

        left = int(x - width / 2)
        top = int(y - height / 2)
        right = int(x + width / 2)
        bottom = int(y + height / 2)

        draw.rectangle(
            [left, top, right, bottom],
            outline="red",
            width=4
        )

        label = f"Pothole {confidence * 100:.1f}%"

        bbox = draw.textbbox((left, max(0, top - 28)), label, font=font)

        draw.rectangle(
            bbox,
            fill="red"
        )

        draw.text(
            (left, max(0, top - 28)),
            label,
            fill="white",
            font=font
        )

    return image


def save_uploaded_image(uploaded_file):

    suffix = os.path.splitext(uploaded_file.name)[1]

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp_file:

        temp_file.write(uploaded_file.getbuffer())

        return temp_file.name


# =========================================================
# HOME
# =========================================================

if page == "🏠 Home":

    st.markdown(
        """
        <div class="hero">
            <h1>🛡️ RoadGuard AI</h1>
            <p>AI-powered pothole and road damage detection</p>
            <p style="font-size:15px;">
                Smarter Roads. Safer Journeys.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="main-title">
            Welcome to RoadGuard AI 👋
        </div>

        <div class="main-subtitle">
            Make roads safer using Artificial Intelligence and Computer Vision.
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="feature-card">
                <h2>🔍 Detect</h2>
                <p>
                Upload a road image and let our AI model identify
                potholes automatically.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="feature-card">
                <h2>📊 Analyze</h2>
                <p>
                View detection counts, confidence scores,
                road status and system statistics.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="feature-card">
                <h2>📍 Report</h2>
                <p>
                Record road problems and maintain a simple
                history of reported issues.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="feature-card">
            <h2>🚗 How RoadGuard AI Works</h2>

            <p>
            📷 Upload a road image
            →
            🤖 AI analyzes the image
            →
            🎯 Potholes are detected
            →
            📊 Results are displayed
            →
            📍 Road problems can be reported
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# DETECT
# =========================================================

elif page == "🔍 Detect":

    st.markdown(
        '<div class="section-title">🔍 Pothole Detection</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="section-subtitle">
        Upload a road image and let RoadGuard AI analyze it.
        </div>
        """,
        unsafe_allow_html=True
    )

    # API KEY
st.markdown("### 🔒 AI Connection")

try:
    api_key = st.secrets["ROBOFLOW_API_KEY"]
except Exception:
    api_key = ""
    st.error("Roboflow API key is not configured. Add it in Streamlit Secrets.")
    
st.markdown("---")

    uploaded_file = st.file_uploader(
        "📷 Upload a road image",
        type=["jpg", "jpeg", "png", "webp"]
    )

    if uploaded_file:

        image = Image.open(uploaded_file)
        image = ImageOps.exif_transpose(image)

        st.markdown("### 🖼️ Selected Image")

        st.image(
            image,
            caption=uploaded_file.name,
            use_container_width=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        detect_button = st.button(
            "🚀 Detect Potholes",
            use_container_width=True,
            type="primary"
        )

        if detect_button:

            if not api_key:

                st.error(
                    "Please enter your Roboflow Private API Key first."
                )

            else:

                with st.spinner("🤖 AI is analyzing the road image..."):

                    temp_path = None

                    try:

                        temp_path = save_uploaded_image(uploaded_file)

                        client = InferenceHTTPClient(
                            api_url=API_URL,
                            api_key=api_key
                        )

                        result = client.infer(
                            temp_path,
                            model_id=MODEL_ID
                        )

                        predictions = result.get(
                            "predictions",
                            []
                        )

                        result_image = draw_predictions(
                            image,
                            predictions
                        )

                        st.session_state.last_result = result
                        st.session_state.last_image = result_image

                        confidences = [
                            get_confidence(p)
                            for p in predictions
                        ]

                        average_confidence = (
                            sum(confidences) / len(confidences)
                            if confidences
                            else 0
                        )

                        timestamp = datetime.now().strftime(
                            "%d %b %Y, %I:%M %p"
                        )

                        st.session_state.history.append(
                            {
                                "Image": uploaded_file.name,
                                "Time": timestamp,
                                "Potholes": len(predictions),
                                "Confidence": round(
                                    average_confidence * 100,
                                    1
                                )
                            }
                        )

                        st.success("✅ Analysis completed successfully!")

                        st.markdown("## 🎯 Detection Result")

                        st.image(
                            result_image,
                            caption="AI Detection Result",
                            use_container_width=True
                        )

                        st.markdown("<br>", unsafe_allow_html=True)

                        # RESULT METRICS

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.markdown(
                                f"""
                                <div class="metric-card">
                                    <div class="metric-number">
                                        {len(predictions)}
                                    </div>
                                    <div class="metric-label">
                                        Potholes Detected
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        with col2:
                            st.markdown(
                                f"""
                                <div class="metric-card">
                                    <div class="metric-number">
                                        {average_confidence * 100:.1f}%
                                    </div>
                                    <div class="metric-label">
                                        Average Confidence
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        with col3:

                            if len(predictions) == 0:
                                status = "SAFE"
                            elif len(predictions) <= 2:
                                status = "LOW RISK"
                            elif len(predictions) <= 5:
                                status = "MEDIUM"
                            else:
                                status = "HIGH RISK"

                            st.markdown(
                                f"""
                                <div class="metric-card">
                                    <div class="metric-number">
                                        {status}
                                    </div>
                                    <div class="metric-label">
                                        Road Status
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        st.markdown("<br>", unsafe_allow_html=True)

                        if len(predictions) == 0:

                            st.markdown(
                                """
                                <div class="status-safe">
                                ✅ No potholes detected in this image.
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        else:

                            st.markdown(
                                f"""
                                <div class="status-warning">
                                ⚠️ {len(predictions)}
                                pothole(s) detected.
                                Please inspect the road carefully.
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        st.markdown("<br>", unsafe_allow_html=True)

                        # INDIVIDUAL DETECTIONS

                        if predictions:

                            st.markdown("### 🎯 Individual Detections")

                            detection_rows = []

                            for i, prediction in enumerate(
                                predictions,
                                start=1
                            ):

                                detection_rows.append(
                                    {
                                        "Detection": i,
                                        "Object": prediction.get(
                                            "class",
                                            "pothole"
                                        ),
                                        "Confidence": f"{get_confidence(prediction) * 100:.1f}%"
                                    }
                                )

                            st.dataframe(
                                pd.DataFrame(detection_rows),
                                use_container_width=True,
                                hide_index=True
                            )

                        # TECHNICAL RESULT

                        with st.expander(
                            "🧠 View AI Technical Result"
                        ):

                            st.json(result)

                    except Exception as e:

                        st.error(
                            "❌ Something went wrong while connecting to the AI model."
                        )

                        st.warning(
                            "Please check your Roboflow Private API Key and model connection."
                        )

                        with st.expander("Technical information"):
                            st.code(str(e))

                    finally:

                        if temp_path and os.path.exists(temp_path):

                            try:
                                os.remove(temp_path)
                            except:
                                pass


# =========================================================
# DASHBOARD
# =========================================================

elif page == "📊 Dashboard":

    st.markdown(
        '<div class="section-title">📊 RoadGuard Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="section-subtitle">
        Overview of your pothole detection activity.
        </div>
        """,
        unsafe_allow_html=True
    )

    history = st.session_state.history

    total_scans = len(history)

    total_potholes = sum(
        item["Potholes"]
        for item in history
    )

    if total_scans > 0:

        avg_confidence = sum(
            item["Confidence"]
            for item in history
        ) / total_scans

    else:

        avg_confidence = 0

    if total_potholes == 0:
        road_status = "SAFE"
    elif total_potholes <= 5:
        road_status = "MEDIUM"
    else:
        road_status = "HIGH RISK"

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">{total_scans}</div>
                <div class="metric-label">Total Scans</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">{total_potholes}</div>
                <div class="metric-label">Potholes Found</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">
                    {avg_confidence:.1f}%
                </div>
                <div class="metric-label">
                    Avg. Confidence
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-number">
                    {road_status}
                </div>
                <div class="metric-label">
                    Road Status
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if history:

        df = pd.DataFrame(history)

        st.markdown("### 📈 Detection Activity")

        chart_data = df[["Potholes"]]

        st.bar_chart(
            chart_data,
            use_container_width=True
        )

        st.markdown("### 🤖 AI Confidence")

        confidence_data = df[["Confidence"]]

        st.line_chart(
            confidence_data,
            use_container_width=True
        )

    else:

        st.info(
            "📷 No detection history yet. Go to Detect and analyze a road image."
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="feature-card">

        <h3>🤖 AI System</h3>

        <p>
        <b>Model:</b> YOLO26 Small
        </p>

        <p>
        <b>Task:</b> Object Detection
        </p>

        <p>
        <b>Target:</b> Road Potholes
        </p>

        <p>
        <b>Platform:</b> Roboflow
        </p>

        <p>
        <b>Application:</b> Streamlit
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# HISTORY
# =========================================================

elif page == "🕘 History":

    st.markdown(
        '<div class="section-title">🕘 Detection History</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="section-subtitle">
        Previous road image analyses from this session.
        </div>
        """,
        unsafe_allow_html=True
    )

    history = st.session_state.history

    if history:

        df = pd.DataFrame(history)

        df.insert(
            0,
            "Scan",
            range(1, len(df) + 1)
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(
            "🗑️ Clear History"
        ):

            st.session_state.history = []

            st.success("History cleared.")

            st.rerun()

    else:

        st.info(
            "No scans yet. Your detection history will appear here."
        )


# =========================================================
# REPORT
# =========================================================

elif page == "📍 Report":

    st.markdown(
        '<div class="section-title">📍 Report Road Damage</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="section-subtitle">
        Record information about a pothole or damaged road.
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("road_report_form"):

        location = st.text_input(
            "📍 Location",
            placeholder="Example: Kumaraswamy Layout"
        )

        issue_type = st.selectbox(
            "⚠️ Issue Type",
            [
                "Pothole",
                "Road Crack",
                "Damaged Road",
                "Waterlogging",
                "Other"
            ]
        )

        severity = st.selectbox(
            "🚨 Severity",
            [
                "Low",
                "Medium",
                "High",
                "Critical"
            ]
        )

        description = st.text_area(
            "📝 Description",
            placeholder="Describe the road problem..."
        )

        submitted = st.form_submit_button(
            "📤 Submit Report",
            use_container_width=True
        )

        if submitted:

            if not location:

                st.error(
                    "Please enter the location."
                )

            else:

                report = {
                    "Location": location,
                    "Issue": issue_type,
                    "Severity": severity,
                    "Description": description,
                    "Time": datetime.now().strftime(
                        "%d %b %Y, %I:%M %p"
                    )
                }

                st.session_state.reports.append(
                    report
                )

                st.success(
                    "✅ Road damage report submitted successfully!"
                )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("### 📋 Submitted Reports")

    if st.session_state.reports:

        report_df = pd.DataFrame(
            st.session_state.reports
        )

        st.dataframe(
            report_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No road damage reports submitted yet."
        )


# =========================================================
# ABOUT
# =========================================================

elif page == "ℹ️ About":

    st.markdown(
        '<div class="section-title">ℹ️ About RoadGuard AI</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="section-subtitle">
        Understanding the technology behind the application.
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            """
            <div class="feature-card">

            <h2>🛡️ What is RoadGuard AI?</h2>

            <p>
            RoadGuard AI is an Artificial Intelligence based
            road monitoring application designed to detect
            potholes from road images.
            </p>

            <p>
            The system uses Computer Vision and an
            object-detection model to identify potholes
            and estimate the confidence of each detection.
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            """
            <div class="feature-card">

            <h2>🤖 How the AI Works</h2>

            <p>
            A road image is provided to the trained AI model.
            The model analyzes the image and predicts the
            location of potholes using bounding boxes.
            </p>

            <p>
            Each prediction also receives a confidence score
            representing how confident the model is.
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="feature-card">

        <h2>⚙️ Technology Stack</h2>

        <p>🐍 <b>Python</b> — Application programming</p>

        <p>🎨 <b>Streamlit</b> — Web application interface</p>

        <p>🤖 <b>YOLO26 Small</b> — Object detection model</p>

        <p>☁️ <b>Roboflow</b> — Dataset, training and model deployment</p>

        <p>👁️ <b>Computer Vision</b> — Road image analysis</p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.info(
        "🚧 RoadGuard AI is a student project designed to demonstrate "
        "how Artificial Intelligence can assist in identifying road damage."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        🛡️ RoadGuard AI &nbsp;•&nbsp;
        Smarter Roads. Safer Journeys.
        <br>
        AI-powered pothole detection using Computer Vision
    </div>
    """,
    unsafe_allow_html=True
)
