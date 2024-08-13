import streamlit as st


import os
import base64


def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def get_img_with_href(local_img_path, target_url, caption):
    img_format = os.path.splitext(local_img_path)[-1].replace(".", "")
    bin_str = get_base64_of_bin_file(local_img_path)
    image_size = 150
    html_code = f"""
    <p style="text-align: center;">
        <a href="{target_url}">
            <img src="data:image/{img_format};base64,{bin_str}"
            width="{image_size}"
            height="{image_size}"
            style="border-radius:50%">
        </a>
        <br>
        {caption}
    </p>"""

    return html_code



def settings_page():
    st.write(f'Team: {st.session_state["team_name"]}')
    logout = st.button('Logout')


    st.markdown("<br>", unsafe_allow_html=True) 
    st.markdown("## Links")

    games_url = "https://chriscremer.ca/TPL/index.html"
    frisbee_img = "images/frisbee.png"

    tuc_url = "https://www.tuc.org/zuluru/divisions/standings?division=1041&team=9772"
    tuc_img = "images/tuc.jpeg"

    public_sheet_url = "https://docs.google.com/spreadsheets/d/1GovSEPKC2ayC7YvGvKvZIXlOUi1eGjdr7yF9Aw_q964/edit?gid=1238198717#gid=1238198717"
    public_sheet_img = "images/gsheet.png"

    gm_sheet_url = "https://docs.google.com/spreadsheets/d/1U4T-r7DsfWZI9VXsa7Ul38XDDLpE-7Sz1TFzd29EEVw/edit?gid=9#gid=9"
    gm_sheet_img = "images/gsheet.png"

    stat_keeping_url = "https://tplstats.netlify.app/home"
    stat_keeping_img = "images/stat_keeping.png"


    cols = st.columns(7)
    with cols[1]:
        st.markdown(get_img_with_href(frisbee_img, games_url, "Games Page"), unsafe_allow_html=True)
    with cols[2]:
        st.markdown(get_img_with_href(tuc_img, tuc_url, "TUC Site"), unsafe_allow_html=True)
    with cols[3]:
        st.markdown(get_img_with_href(public_sheet_img, public_sheet_url, "Public Stats Sheet"), unsafe_allow_html=True)
    with cols[4]:
        st.markdown(get_img_with_href(gm_sheet_img, gm_sheet_url, "GM Sheet"), unsafe_allow_html=True)
    with cols[5]:
        st.markdown(get_img_with_href(stat_keeping_img, stat_keeping_url, "Stat Keeping"), unsafe_allow_html=True)



    if logout:
        st.session_state['login_status'] = False
        print (f"Logging out {st.session_state['team_name']}")
        # erase session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
