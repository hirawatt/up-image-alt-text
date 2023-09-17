import streamlit as st
import time
from streamlit_image_select import image_select
import pandas as pd

st.set_page_config(
    page_title="Image Alt Text Tool",
    page_icon="📒",
    layout="wide",
)

if 'initialised' not in st.session_state:
    st.session_state['initialised'] = False
if 'generate' not in st.session_state:
    st.session_state['generate'] = False

st.markdown("""# <center> :ledger: Image Alt Text Tool</center>""", unsafe_allow_html=True)
# Section 1 - Input website data
with st.form("form_1"):
    col1, col2, col3, col4 = st.columns([2, 4, 1, 2])
    website_link = col2.text_input(
                                    label="Enter website link",
                                    value="website link",
                                    label_visibility="collapsed"
                                )

    submitted = col3.form_submit_button("Analyze", use_container_width=True)
    no_of_images = 4
    if submitted:
        with col2.status("Analyzing website..."):
            st.write("Searching for images...")
            time.sleep(1)
            analysis_info = f"Found {no_of_images} images without thumbnail."
            st.write(analysis_info)
            time.sleep(1)
            st.write("Downloading data...")
            time.sleep(1)
        col2.success(analysis_info)
        st.session_state['initialised'] = True

# FIXME: add generate alt text logic
def generate_alt_text():
    st.session_state['generate'] = True

# Section 2 - Thumbnail of images without alt text
c1, c2 = st.columns([9, 1])
c1.subheader("Thumbnail of images without alt text")
c2.button("Generate", disabled=not(st.session_state["initialised"]), use_container_width=True, on_click=generate_alt_text)
if st.session_state['initialised']:
    image_selected = image_select("Select any one", ["images/image1.jpg", "images/image2.jpg", "images/image3.jpg", "images/image4.jpg"])
    
    # show alt text options based on the image selected
    output = (image_selected.split("images/")[1].split(".jpg")[0])
    csv = pd.read_csv("sample-alt-text.csv")
    image_list = csv["Image"].tolist()
    st.subheader("Alt text options")
    
    if st.session_state['generate']:
        # add alt text display logic
        o1, o2 = st.columns([4, 6])
        o1.markdown(f"#### Selected Image : `{output}`")
        image_index = image_list.index(output)
        alt1 = csv["Alt1"][image_index]
        alt2 = csv["Alt2"][image_index]
        o2.write("Copy any of the below alt texts")
        o2.code(f"{alt1}", language='bash')
        o2.code(f"{alt2}", language='bash')
        
        # extract & display all data
        # FIXME: add extract data logic
        co1, co2, = st.columns([9, 1])
        if co2.button("Extract", use_container_width=True):
            with st.expander("Extracted Data Info", expanded=True):
                st.dataframe(csv, hide_index=True, use_container_width=True)
    else:
        st.info("Press Generate to get thumbnail alt text")
else:
    st.info("Enter any website & analyse to search for thumbnails")
