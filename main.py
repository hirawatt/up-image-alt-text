import streamlit as st
import time
from streamlit_image_select import image_select
import pandas as pd
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import os
from streamlit import runtime
from streamlit.web import cli as stcli
import sys
import requests

st.set_page_config(
    page_title="Image Alt Text Tool",
    page_icon="📒",
    layout="wide",
)

if 'initialised' not in st.session_state:
    st.session_state.initialised = False
if 'generate' not in st.session_state:
    st.session_state.generate = False
if 'code' not in st.session_state:
    st.session_state.code = None
if 'state' not in st.session_state:
    st.session_state.state = None
if 'credentials' not in st.session_state:
    st.session_state.credentials = None
if 'data' not in st.session_state:
    st.session_state.data = None

m1, m2, m3 = st.columns([3, 4, 3])
# TODO: add logout feature
def logout():
    return None

# FIXME: remove query_params if credentials are set
if st.session_state.credentials:
    st.experimental_set_query_params(
        login="success",
    )

    if m3.button("Logout", use_container_width=True):
        logout()

query_params = st.experimental_get_query_params()
#st.write(query_params)
#st.write(st.session_state)

# for localhost testing
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

client_id = st.secrets["client_id"]
client_secret = st.secrets["client_secret"]
redirect_uri = st.secrets["redirect_uri"]

# Define the scopes required for your app
scopes = ['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']
auth_url = "https://accounts.google.com/o/oauth2/auth"
scope = "openid https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile"

# Create the OAuth flow instance
flow = Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=scopes,
    redirect_uri=redirect_uri
)

def get_google_id_token(auth_code, client_id):
    try:
        token = flow.fetch_token(code=auth_code, client_id=client_id, client_secret=client_secret, state=query_params["state"][0])

        # Store the credentials in session state
        st.session_state.credentials = flow.credentials
        st.success('Successfully authenticated!')
        return token
    except ValueError as e:
        st.error(f"Error retrieving ID token: {e}")

if m2.button("Sign in with Google", use_container_width=True):
    # Redirect the user to the Google Sign-In page
    authorization_url, state = flow.authorization_url(prompt='consent')
    auth_endpoint = f"{auth_url}?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&state={state}"
    # FIXME: add official google login button design
    m2.markdown(f'<center><a href="{auth_endpoint}">Click here to sign in with Google</a></center>', unsafe_allow_html=True)

def main():
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
            st.session_state.initialised = True

    # FIXME: add generate alt text logic
    def generate_alt_text():
        st.session_state.generate = True

    @st.cache_data
    def convert_df(df):
        return df.to_csv().encode('utf-8')

    # Section 2 - Thumbnail of images without alt text
    c1, c2 = st.columns([9, 1])
    c1.subheader("Thumbnail of images without alt text")
    c2.button("Generate", disabled=not(st.session_state["initialised"]), use_container_width=True, on_click=generate_alt_text)
    if st.session_state.initialised:
        image_selected = image_select("Select any one", ["images/image1.jpg", "images/image2.jpg", "images/image3.jpg", "images/image4.jpg"])
        
        # show alt text options based on the image selected
        output = (image_selected.split("images/")[1].split(".jpg")[0])
        csv = pd.read_csv("sample-alt-text.csv")
        image_list = csv["Image"].tolist()
        st.subheader("Alt text options")
        
        if st.session_state.generate:
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

if runtime.exists():
    if query_params:
        # FIXME: find alternate logic
        try:
            auth_code = query_params["code"][0]
            response = get_google_id_token(auth_code, client_id)
            # FIXME: add below code inside function?
            #st.write(response)
            r = requests.get(f'https://oauth2.googleapis.com/tokeninfo?id_token={response["id_token"]}')
            st.session_state.data = r.json()
            st.experimental_rerun()
        except:
            m1.write(f"Welcome {st.session_state.data['name']},")
            main()
        #r1 = requests.get(f'https://oauth2.googleapis.com/tokeninfo?access_token={response["access_token"]}')
        #st.write(r1.json())
else:
    sys.argv = ["streamlit", "run", sys.argv[0]]
    sys.exit(stcli.main())