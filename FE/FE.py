import streamlit as st
import requests

def main():
    st.title("Delta Cognition Test")

    # Input: query
    query = st.text_input("Search:", "machine learning")

    # Sidebar r
    st.sidebar.header("Filter")
    year_filter = st.sidebar.text_input("Year", "")
    num_results = st.sidebar.text_input("Number Of Results","")
    sort_by_cites = st.sidebar.checkbox("Sort by cites")

    # Waiting for user to click search button
    if st.button("Search"):
        st.info("Searching...")

        # call API
        api_url = f"http://localhost:8000/search/{query}"
        params = {
            'year_filter': year_filter,
            'num_results': num_results,
            'sort_by_cites': sort_by_cites
        }
        response = requests.get(api_url, params=params)

        # show result
        st.markdown(response.text, unsafe_allow_html=True)

if __name__ == "__main__":
    main()