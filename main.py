import streamlit as st
import time
from streamlit_image_select import image_select
import pandas as pd
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import os

st.set_page_config(
    page_title="Image Alt Text Tool",
    page_icon="📒",
    layout="wide",
)

if 'initialised' not in st.session_state:
    st.session_state['initialised'] = False
if 'generate' not in st.session_state:
    st.session_state['generate'] = False

query_params = st.experimental_get_query_params()
st.write(query_params)
st.write(st.session_state)

if 'code' not in st.session_state:
    st.session_state.code = None

try:
    # Set the client ID and client secret
    client_id = st.secrets["client_id"]
    client_secret = st.secrets["client_secret"]

    # Define the redirect URL after successful authentication
    redirect_uri = st.secrets["redirect_uri"]
except:
    client_id = os.getenv('client_id')
    client_secret = os.getenv('client_secret')
    redirect_uri = os.getenv('redirect_uri')

# Define the scopes required for your app
scopes = ['openid', 'email', 'profile']

# Create the OAuth flow instance
flow = Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=scopes,
    redirect_uri=redirect_uri
)


if 'credentials' not in st.session_state:
    st.session_state.credentials = None

if st.button('Login'):
    authorization_url, state = flow.authorization_url(prompt='consent')

    # Store the state in session state
    st.session_state.state = state
    st.session_state.state = query_params["state"][0]
    st.session_state.code = query_params["code"][0]

    # Redirect the user to the authorization URL
    #st.redirect(authorization_url)
    st.write(f'''
    <a target="_self" href="{authorization_url}">
        <button>
            Please login via Google
        </button>
    </a>
    ''',
    unsafe_allow_html=True
    )

if 'code' in st.session_state and 'state' in st.session_state:
    flow.fetch_token(authorization_response=st.session_state.code)

    # Verify the state to prevent CSRF attacks
    assert st.session_state.state == st.session_state.token_response.get('state')

    # Store the credentials in session state
    st.session_state.credentials = flow.credentials
    st.write('Successfully authenticated!')

if st.session_state.credentials:
    token = st.session_state.credentials.token
    # Use the token for API calls or other purposes
    st.write('Access Token:', token)

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
            st.toast("Searching for images...")
            time.sleep(.5)
            analysis_info = f"Found {no_of_images} images without thumbnail."
            st.toast(analysis_info)
            time.sleep(.5)
            st.toast("Downloading data...")
            time.sleep(.5)
            st.toast('Success!', icon='🎉')
        col2.success(analysis_info)
        st.session_state['initialised'] = True

# FIXME: add generate alt text logic
def generate_alt_text():
    st.session_state['generate'] = True
    
@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

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
        
        sample_data = convert_df(csv)
        # extract & display all data
        co1, co2, = st.columns([9, 1])
        if co2.download_button(
                label="Extract",
                data=sample_data,
                file_name='sample_data.csv',
                mime='text/csv',
                use_container_width=True,
            ):
            with st.expander("Extracted Data Info", expanded=True):
                st.dataframe(csv, hide_index=True, use_container_width=True)
    else:
        st.info("Press Generate to get thumbnail alt text")
else:
    st.info("Enter any website & analyse to search for thumbnails")
