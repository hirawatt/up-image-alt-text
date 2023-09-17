import streamlit as st
import time
from streamlit_image_select import image_select

st.set_page_config(
    page_title="Image Alt Text Tool",
    page_icon="📒",
    layout="wide",
)

st.markdown("""# <center> :ledger: Image Alt Text Tool</center>""", unsafe_allow_html=True)
# Section 1 - Input website data
with st.form("form_1"):
    col1, col2, col3, col4 = st.columns([2, 4, 2, 2])
    website_link = col2.text_input(
                                    label="Enter website link",
                                    value="website link",
                                    label_visibility="collapsed"
                                )

    submitted = col3.form_submit_button("Analyze")
    no_of_images = 4
    if submitted:
        with col2.status("Analyzing website..."):
            st.write("Searching for images...")
            time.sleep(2)
            analysis_info = f"Found {no_of_images} images without thumbnail."
            st.write(analysis_info)
            time.sleep(1)
            st.write("Downloading data...")
            time.sleep(1)
        col2.success(analysis_info)

st.divider()
# Section 2 - Thumbnail of images without alt text
st.write("Thumbnail of images without alt text")
image_selected = image_select("Select any one", ["images/image1.jpg", "images/image2.jpg", "images/image3.jpg", "images/image4.jpg"])
st.write(image_selected)
#co1, co2, co3, co4 = st.columns(4)
#co1.image("images/image1.jpg")

st.divider()
# Section 3 - Show alt text options based on the image selected
