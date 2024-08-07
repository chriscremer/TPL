import streamlit as st

def settings_page():
    st.write(f'Team: {st.session_state["team_name"]}')
    logout = st.button('Logout')
    if logout:
        st.session_state['login_status'] = False
        print (f"Logging out {st.session_state['team_name']}")
        # erase session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
