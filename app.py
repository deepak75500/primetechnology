import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
st.set_page_config(page_title="Odisha RERA PROJECT DETAILS", layout="wide")
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@600&display=swap" rel="stylesheet">
<style>
.glow {
    font-size: 50px;
    color: #00ffff;
    text-align: center;
    animation: glow 2s ease-in-out infinite alternate;
    font-family: 'Orbitron', sans-serif;
    margin-bottom: 30px;
}
@keyframes glow {
    from { text-shadow: 0 0 5px #00ffff, 0 0 10px #00ffff; }
    to   { text-shadow: 0 0 20px #00ccff, 0 0 40px #00ccff; }
}
.card {
    background: rgba(0, 255, 255, 0.08);
    border-radius: 20px;
    padding: 20px;
    margin: 20px 0;
    backdrop-filter: blur(8px);
    box-shadow: 0 0 30px rgba(0, 255, 255, 0.3);
    border: 1px solid rgba(0, 255, 255, 0.2);
    color: #00ffff;
    font-family: 'Orbitron', sans-serif;
}
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="glow">🛸 Odisha RERA PROJECT DETAILS</div>', unsafe_allow_html=True)
st.sidebar.header("⚙️ Settings")
num_projects = st.sidebar.slider("Select number of projects to fetch", min_value=1, max_value=30, value=6)
view_mode = st.sidebar.radio("View Mode", ["Hologram Cards", "Colorful Table"])
def style_table(df):
    return df.style \
        .applymap(lambda _: 'color: black; background-color: #a3f7bf; font-weight: bold;', subset=["RERA Regd. No"]) \
        .applymap(lambda _: 'color: white; background-color: #00adb5; font-weight: bold;', subset=["Project Name"]) \
        .applymap(lambda _: 'color: black; background-color: #ffd369; font-style: italic;', subset=["Promoter Name"]) \
        .applymap(lambda _: 'color: white; background-color: #393e46;', subset=["Promoter Address"]) \
        .applymap(lambda _: 'color: white; background-color: #222831;', subset=["GST No."])
def scrape_rera_projects(num_projects):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    driver.get("https://rera.odisha.gov.in/projects/project-list")

    wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(text(),'View Details')]")))
    data = []

    for i in range(num_projects):
        try:
            buttons = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(text(),'View Details')]")))
            button = buttons[i]
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", button)
            time.sleep(8)

            rera_no = driver.find_element(By.XPATH, "//label[contains(text(), 'RERA Regd. No.')]/following-sibling::*[1]").text
            project_name = driver.find_element(By.XPATH, "//label[contains(text(), 'Project Name')]/following-sibling::*[1]").text

            promoter_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Promoter Details')]")))
            driver.execute_script("arguments[0].click();", promoter_tab)
            time.sleep(6)

            try:
                promoter_name = driver.find_element(By.XPATH, "//label[contains(text(), 'Company Name')]/following-sibling::*[1]").text
            except NoSuchElementException:
                promoter_name = driver.find_element(By.XPATH, "//label[contains(text(), 'Propietory Name')]/following-sibling::*[1]").text

            try:
                address = driver.find_element(By.XPATH, "//label[contains(text(), 'Registered Office Address')]/following-sibling::*[1]").text
            except NoSuchElementException:
                address = driver.find_element(By.XPATH, "//label[contains(text(), 'Current Residence Address')]/following-sibling::*[1]").text

            gst_no = driver.find_element(By.XPATH, "//label[contains(text(), 'GST No.')]/following-sibling::*[1]").text

            data.append({
                "RERA Regd. No": rera_no,
                "Project Name": project_name,
                "Promoter Name": promoter_name,
                "Promoter Address": address,
                "GST No.": gst_no
            })

            driver.back()
            wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(text(),'View Details')]")))
            time.sleep(5)

        except Exception as e:
            st.warning(f"⚠️ Error on project {i + 1}: {e}")
            driver.back()
            wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(text(),'View Details')]")))
            time.sleep(3)

    driver.quit()
    return pd.DataFrame(data)
if st.button("🚀 Scrape and Show Projects"):
    with st.spinner("Connecting to RERA Odisha..."):
        df = scrape_rera_projects(num_projects)
        st.success("✅ Data fetched successfully!")

        if view_mode == "Hologram Cards":
            for index, row in df.iterrows():
                st.markdown(f"""
                <div class="card">
                    <h4>🚧 {row['Project Name']}</h4>
                    <p><b>RERA Regd. No:</b> {row['RERA Regd. No']}<br>
                    <b>Promoter:</b> {row['Promoter Name']}<br>
                    <b>Address:</b> {row['Promoter Address']}<br>
                    <b>GST No.:</b> {row['GST No.']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.dataframe(style_table(df), use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", data=csv, file_name="odisha_rera_projects.csv", mime="text/csv")
