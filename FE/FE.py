import streamlit as st
import requests

def main():
    st.title("Google Scholar Crawler and Viewer")

    # Input: Tìm kiếm từ khóa
    query = st.text_input("Nhập từ khóa tìm kiếm:", "machine learning")

    # Sidebar để thêm các nút chọn filter
    st.sidebar.header("Filter")
    year_filter = st.sidebar.text_input("Năm", "")
    num_results = st.sidebar.number_input("Số lượng kết quả tìm kiếm", 1, 100, 10)
    sort_by_cites = st.sidebar.checkbox("Sắp xếp theo số lần trích dẫn")

    # Nút để thực hiện crawler và hiển thị kết quả
    if st.button("Tìm Kiếm"):
        st.info("Đang tìm kiếm...")

        # Gọi API từ FastAPI backend với các tham số filter
        api_url = f"http://localhost:8000/search/{query}"
        params = {
            'year_filter': year_filter,
            'num_results': num_results,
            'sort_by_cites': sort_by_cites
        }
        response = requests.get(api_url, params=params)

        # Hiển thị kết quả
        st.markdown(response.text, unsafe_allow_html=True)

if __name__ == "__main__":
    main()