import streamlit as st
import calendar
import random
import pandas as pd
from datetime import datetime
import backend  # Import the backend script

# Set Streamlit page configuration
st.set_page_config(page_title="Mari's Little Lambs", layout="wide")

# Inject JavaScript to detect the color scheme and apply the appropriate stylesheet
st.markdown("""
    <script>
    function detectColorScheme() {
        var theme = "light";    //default to light

        //local storage is used to override OS theme settings
        if(localStorage.getItem("theme")) {
            if(localStorage.getItem("theme") == "dark") {
                theme = "dark";
            }
        } else if(!window.matchMedia) {
            //matchMedia method not supported
            return false;
        } else if(window.matchMedia("(prefers-color-scheme: dark)").matches) {
            //OS theme setting detected as dark
            theme = "dark";
        }

        if (theme == "dark") {
            document.getElementById("dark-mode-styles").disabled = false;
            document.getElementById("light-mode-styles").disabled = true;
        } else {
            document.getElementById("dark-mode-styles").disabled = true;
            document.getElementById("light-mode-styles").disabled = false;
        }
    }

    detectColorScheme();
    </script>
    """, unsafe_allow_html=True)

# Inject custom CSS for light mode styling
st.markdown("""
    <style id="light-mode-styles">
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@200&display=swap');

    html, body, h1, h2, h3, h4, h5, h6, div, span, p, .stButton>button, .stFileUploader, .stTextInput>div>div>input {
        font-family: 'Nunito', sans-serif;
        font-weight: 200;
    }

    body {
        background-color: #fff; /* Light background */
        color: #000; /* Dark text */
    }

    .title {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        margin: 20px;
    }

    .subtitle {
        font-size: 24px;
        text-align: center;
        margin: 10px;
    }

    .upload-box {
        border: 2px dashed #aaa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
    }

    .stFileUploader {
        margin: 15px;
    }

    .stButton>button {
        width: 100%;
        border-radius: 20px;
        border: none;
        background-color: #4CAF50;
        color: white;
        padding: 14px 20px;
        margin: 8px 0;
        cursor: pointer;
    }

    .stButton>button:hover {
        background-color: #45a049;
    }

    .metric-box {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        padding: 15px;
        margin: 15px;
        background-color: transparent;
        border-radius: 10px;
        border: 2px solid #000;  /* Dark border for light mode */
        box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        flex: 1 1 22%; /* Adjusting flex to increase width by 20% */
        min-height: 150px; /* Minimum height for uniformity */
    }

    .metric-box h4 {
        margin: 0;
        font-size: 1em;
        color: #000;
    }

    .metric-box p {
        font-size: 1.5em;
        font-weight: bold;
        color: #4CAF50;
        margin: 5px 0 0 0;
        align-self: center;
    }

    .schedule-table {
        margin: 15px;
        border: 2px solid #000;  /* Dark border for light mode */
        border-radius: 10px;
        background-color: transparent;
        text-align: center;
        color: #4CAF50;
        padding: 10px;
        width: 100%;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
    }

    .schedule-table th, .schedule-table td {
        padding: 10px;
        border: 1px solid #000;  /* Dark border for light mode */
        color: #000; /* Ensuring text color is set */
    }

    .schedule-table table {
        width: 100%;
        border-collapse: collapse;
    }

    </style>
    """, unsafe_allow_html=True)

# Inject custom CSS for dark mode styling
st.markdown("""
    <style id="dark-mode-styles" disabled>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@200&display=swap');

    html, body, h1, h2, h3, h4, h5, h6, div, span, p, .stButton>button, .stFileUploader, .stTextInput>div>div>input {
        font-family: 'Nunito', sans-serif;
        font-weight: 200;
    }

    body {
        background-color: #333; /* Dark background */
        color: #fff; /* Light text */
    }

    .title {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        margin: 20px;
    }

    .subtitle {
        font-size: 24px;
        text-align: center;
        margin: 10px;
    }

    .upload-box {
        border: 2px dashed #aaa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        text-align: center;
    }

    .stFileUploader {
        margin: 15px;
    }

    .stButton>button {
        width: 100%;
        border-radius: 20px;
        border: none;
        background-color: #4CAF50;
        color: white;
        padding: 14px 20px;
        margin: 8px 0;
        cursor: pointer;
    }

    .stButton>button:hover {
        background-color: #45a049;
    }

    .metric-box {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        padding: 15px;
        margin: 15px;
        background-color: transparent;
        border-radius: 10px;
        border: 2px solid #fff;  /* Light border for dark mode */
        box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        flex: 1 1 22%; /* Adjusting flex to increase width by 20% */
        min-height: 150px; /* Minimum height for uniformity */
    }

    .metric-box h4 {
        margin: 0;
        font-size: 1em;
        color: #fff;
    }

    .metric-box p {
        font-size: 1.5em;
        font-weight: bold;
        color: #4CAF50;
        margin: 5px 0 0 0;
        align-self: center;
    }

    .schedule-table {
        margin: 15px;
        border: 2px solid #fff;  /* Light border for dark mode */
        border-radius: 10px;
        background-color: transparent;
        text-align: center;
        color: #4CAF50;
        padding: 10px;
        width: 100%;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
    }

    .schedule-table th, .schedule-table td {
        padding: 10px;
        border: 1px solid #fff;  /* Light border for dark mode */
        color: #fff; /* Ensuring text color is set */
    }

    .schedule-table table {
        width: 100%;
        border-collapse: collapse;
    }

    </style>
    """, unsafe_allow_html=True)

# Function to generate a calendar month with randomly colored days
def generate_colored_month(year, month):
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    cal_html = f"<div style='display: inline-block; width: 100%; text-align: center;'><h3>{month_name}</h3><table border='0' cellpadding='3' cellspacing='3' class='calendar' style='margin-left: auto; margin-right: auto;'><tr><th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th><th>Sat</th><th>Sun</th></tr>"
    for week in cal:
        cal_html += "<tr>"
        for i, day in enumerate(week):
            if day == 0:
                cal_html += "<td></td>"
            else:
                is_weekend = i == 5 or i == 6
                if not is_weekend:
                    color = random.choice(["red", "green"])
                    cal_html += f"<td style='background-color:{color};' title='Capacity = '>{day}</td>"
                else:
                    cal_html += f"<td title='Capacity = '>{day}</td>"
        cal_html += "</tr>"
    cal_html += "</table></div>"

    return cal_html

# Placeholder function for the home page
def display_home():
    st.markdown('<div class="title">Mari\'s Little Lambs</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Availability Date Calculator</div>', unsafe_allow_html=True)

    left_spacer, container, right_spacer = st.columns([2, 6, 2])

    with container:
        name = st.text_input("Enter the name of the child")
        date_of_birth = st.date_input("Select the date of birth")
        child_class = st.selectbox("Select the class", ["Infants", "Wobblers", "Older Toddlers", "Preschool"])
        schedule_days = st.multiselect("Select preferred schedule days",
                                       ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        schedule_type = st.selectbox("Select Program type", ["Fixed", "Flexible"])
        preferred_joining_date = st.date_input("Select Preferred Joining Date")

        upload_col1, upload_col2, upload_col3 = st.columns(3)

        with upload_col1:
            st.markdown('<div class="upload-box">Upload Active List Here</div>', unsafe_allow_html=True)
            active_file = st.file_uploader("", type=['xlsx', 'xls'], key="active_3")

        with upload_col2:
            st.markdown('<div class="upload-box">Upload Hold List Here</div>', unsafe_allow_html=True)
            hold_file = st.file_uploader("", type=['xlsx', 'xls'], key="hold_3")

        with upload_col3:
            st.markdown('<div class="upload-box">Upload FTE List Here</div>', unsafe_allow_html=True)
            fte_file = st.file_uploader("", type=['xlsx', 'xls'], key="fte_3")

        button_spacer_left, button_col, button_spacer_right = st.columns([3, 2, 3])
        with button_col:
            if st.button('Check Availability'):
                if active_file and hold_file and fte_file:
                    metrics = backend.process_inputs(name, date_of_birth, child_class, schedule_days, schedule_type,
                                                     preferred_joining_date, active_file, hold_file, fte_file)
                    st.session_state['metrics'] = metrics
                    st.session_state['active_file'] = active_file
                    st.session_state['hold_file'] = hold_file
                    st.session_state['fte_file'] = fte_file
                else:
                    st.session_state['metrics'] = {}
                st.session_state.page = 'metrics'
                st.experimental_rerun()

# Function to display the metrics page, including Excel file display and calendars
def display_metrics_page():
    st.markdown('<div class="title">Mari\'s Little Lambs</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Schedule Availability as on the Requested Joining Date</div>', unsafe_allow_html=True)

    metrics = st.session_state.get('metrics', {})

    default_metrics = {
        'Total kids': "N/A",
        'Capacity': "N/A",
        'Number of kids on hold': "N/A",
        'Full-time eq.': "N/A",
        'Graduating in next 60 days': "N/A",
        'Recently joined (coming soon)': "N/A",
        'Kid to staff ratio (coming soon)': "N/A",
        'Wait time in days': "N/A",
        'Availability for the requested date': "N/A",
        'Earliest Available Date': "<span style='color: green;'>N/A</span>",
        'Preferred Schedule': "<span style='color: green;'>N/A</span>",
    }

    for key in default_metrics:
        if key not in metrics:
            metrics[key] = default_metrics[key]

    base_metrics = ['Availability for the requested date', 'Earliest Available Date', 'Preferred Schedule']
    non_base_metrics = [(metric_name, metric_value) for metric_name, metric_value in metrics.items() if
                        metric_name not in base_metrics + ['Schedule Available']]

    # Ensure uniform box sizes
    cols = st.columns(len(non_base_metrics))

    for col, (metric_name, metric_value) in zip(cols, non_base_metrics):
        with col:
            st.markdown(f"""
                                <div class="metric-box">
                                    <h4>{metric_name}</h4>
                                    <p>{metric_value}</p>
                                </div>
                            """, unsafe_allow_html=True)

    base_cols = st.columns(3)  # Three columns for "Availability", "Preferred Schedule", and "Earliest Available Date"
    for base_col, metric_name in zip(base_cols, base_metrics):
        metric_value = metrics[metric_name]
        if metric_name == 'Availability for the requested date':
            if metric_value.lower() == "yes":
                color = "green"
            else:
                color = "red"
            metric_value = f"<span style='color: {color};'>{metric_value}</span>"

        with base_col:
            st.markdown(f"""
                                <div class="metric-box">
                                    <h4>{metric_name}</h4>
                                    <p>{metric_value}</p>
                                </div>
                            """, unsafe_allow_html=True)

    # Convert schedule available data into a table format
    schedule_available_raw = metrics.get('Schedule Available', "N/A")
    classroom_capacities = {
        "Infants": 8,
        "Wobblers": 8,
        "Older Toddlers": 7,
        "Preschool": 20
    }

    if schedule_available_raw != "N/A":
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        classes = ["Infants", "Wobblers", "Older Toddlers", "Preschool"]
        schedule_data = schedule_available_raw.split()[5:]  # Adjusted to skip the first 5 non-numeric entries

        schedule_table_html = "<table class='schedule-table'><thead><tr><th>Class/Day</th><th>Classroom Capacities</th>"
        for day in days:
            schedule_table_html += f"<th>{day}</th>"
        schedule_table_html += "</tr></thead><tbody>"

        for class_idx, class_name in enumerate(classes):
            capacity = classroom_capacities[class_name]
            schedule_table_html += f"<tr><td>{class_name}</td><td>{capacity}</td>"
            for day_idx in range(len(days)):
                student_count = schedule_data[class_idx * len(days) + day_idx]
                schedule_table_html += f"<td>{student_count}</td>"
            schedule_table_html += "</tr>"
        schedule_table_html += "</tbody></table>"

        st.markdown(f"""
                    <div class="subtitle">Schedule Available</div>
                    {schedule_table_html}
                    """, unsafe_allow_html=True)

    st.markdown("""
                <div style="text-align: center; margin-top: 10px;">
                    <small>Note: This date is only available if a child of flexible schedule is moved.</small>
                </div>
                """, unsafe_allow_html=True)

    st.markdown('<div class="subtitle">Available Dates</div>', unsafe_allow_html=True)
    year = datetime.now().year
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(generate_colored_month(year, 4), unsafe_allow_html=True)
    with col2:
        st.markdown(generate_colored_month(year, 5), unsafe_allow_html=True)
    with col3:
        st.markdown(generate_colored_month(year, 6), unsafe_allow_html=True)

    st.markdown('<div class="subtitle">Uploaded Lists</div>', unsafe_allow_html=True)
    file_col1, file_col2, file_col3 = st.columns(3)

    with file_col1:
        st.markdown('**Active List**')
        if 'active_file' in st.session_state and st.session_state['active_file'] is not None:
            df_active = pd.read_excel(st.session_state['active_file'], header=4)
            st.dataframe(df_active)
        else:
            st.write("No active list uploaded.")

    with file_col2:
        st.markdown('**Hold List**')
        if 'hold_file' in st.session_state and st.session_state['hold_file'] is not None:
            df_hold = pd.read_excel(st.session_state['hold_file'], header=4)
            st.dataframe(df_hold)
        else:
            st.write("No hold list uploaded.")

    with file_col3:
        st.markdown('**FTE List**')
        if 'fte_file' in st.session_state and st.session_state['fte_file'] is not None:
            df_fte = pd.read_excel(st.session_state['fte_file'], header=3)  # Set 5th row as header
            st.dataframe(df_fte)
        else:
            st.write("No FTE list uploaded.")

def show_loading_animation():
    with st.spinner('Checking Availability...'):
        time.sleep(2)

# Page routing
if 'page' not in st.session_state:
    st.session_state.page = 'home'

if st.session_state.page == 'home':
    display_home()
elif st.session_state.page == 'metrics':
    display_metrics_page()
