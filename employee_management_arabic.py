import streamlit as st
import pandas as pd
import csv
import traceback
import logging
import chardet
from datetime import date

# Set up logging
logging.basicConfig(filename='app.log', level=logging.DEBUG)

# Set page configuration to support right-to-left text
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

csv_path = "employees.csv"

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    return chardet.detect(raw_data)['encoding']

@st.cache_data
def load_data():
    columns = ["الرقم", "الاسم", "المنصب", "الراتب", "الجنس", "تاريخ الميلاد", "سنة التوظيف", "القومية", "رقم الموبايل"]
    encodings_to_try = ['utf-8', 'utf-8-sig', 'cp1256', 'iso-8859-6', 'windows-1256']
    
    for encoding in encodings_to_try:
        try:
            df = pd.read_csv(csv_path, encoding=encoding)
            logging.info(f"Successfully loaded data with encoding: {encoding}")
            # Add any missing columns
            for col in columns:
                if col not in df.columns:
                    df[col] = ""
            return df[columns]  # Ensure columns are in the correct order
        except UnicodeDecodeError:
            continue
        except Exception as e:
            logging.error(f"Error loading data with encoding {encoding}: {str(e)}")
    
    # If all encodings fail, try to detect encoding
    try:
        detected_encoding = detect_encoding(csv_path)
        df = pd.read_csv(csv_path, encoding=detected_encoding)
        logging.info(f"Successfully loaded data with detected encoding: {detected_encoding}")
        # Add any missing columns
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        return df[columns]  # Ensure columns are in the correct order
    except Exception as e:
        logging.error(f"Error loading data with detected encoding: {str(e)}")
    
    # If all attempts fail, return an empty DataFrame
    st.error("Unable to load data. Creating a new empty dataset.")
    return pd.DataFrame(columns=columns)

def save_data(df):
    try:
        df.to_csv(csv_path, index=False, encoding='utf-8', quoting=csv.QUOTE_NONNUMERIC)
        logging.info("Data saved successfully")
    except Exception as e:
        logging.error(f"Error saving data: {str(e)}")
        st.error(f"Error saving data: {str(e)}")
        raise

def main():
    # Add logo and company name
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("logo.png", width=100)  # Replace "logo.png" with your actual logo file
    with col2:
        st.title("شركة النجاح للتكنولوجيا")  # Replace with your company name
    
    st.header("نظام إدارة الموظفين")

    # Load existing data
    if 'df' not in st.session_state:
        st.session_state.df = load_data()

    # Sidebar for adding new employees
    st.sidebar.header("إضافة موظف جديد")
    new_id = st.sidebar.number_input("رقم الموظف", min_value=1, step=1)
    new_name = st.sidebar.text_input("الاسم")
    new_position = st.sidebar.text_input("المنصب")
    new_salary = st.sidebar.number_input("الراتب", min_value=0.0, step=100.0)
    new_gender = st.sidebar.selectbox("الجنس", ["ذكر", "أنثى"])
    new_birth_date = st.sidebar.date_input("تاريخ الميلاد")
    new_hire_year = st.sidebar.number_input("سنة التوظيف", min_value=1900, max_value=date.today().year, step=1)
    new_nationality = st.sidebar.text_input("القومية")
    new_mobile = st.sidebar.text_input("رقم الموبايل")

    if st.sidebar.button("إضافة موظف"):
        try:
            new_employee = pd.DataFrame({
                "الرقم": [new_id],
                "الاسم": [new_name],
                "المنصب": [new_position],
                "الراتب": [new_salary],
                "الجنس": [new_gender],
                "تاريخ الميلاد": [new_birth_date],
                "سنة التوظيف": [new_hire_year],
                "القومية": [new_nationality],
                "رقم الموبايل": [new_mobile]
            })
            st.session_state.df = pd.concat([st.session_state.df, new_employee], ignore_index=True)
            st.sidebar.success("تمت إضافة الموظف بنجاح!")
            logging.info(f"Employee added: ID {new_id}")
        except Exception as e:
            logging.error(f"Error adding employee: {str(e)}")
            st.sidebar.error(f"Error adding employee: {str(e)}")

    # Main page
    st.header("قائمة الموظفين")
    st.dataframe(st.session_state.df)

    # Delete employee
    st.header("حذف موظف")
    employee_to_delete = st.number_input("أدخل رقم الموظف المراد حذفه", min_value=1, step=1)
    if st.button("حذف الموظف"):
        try:
            original_len = len(st.session_state.df)
            st.session_state.df = st.session_state.df[st.session_state.df["الرقم"] != employee_to_delete]
            if len(st.session_state.df) < original_len:
                st.success(f"تم حذف الموظف برقم {employee_to_delete} بنجاح.")
                logging.info(f"Employee deleted: ID {employee_to_delete}")
            else:
                st.warning(f"لم يتم العثور على موظف برقم {employee_to_delete}")
                logging.warning(f"Employee not found for deletion: ID {employee_to_delete}")
        except Exception as e:
            logging.error(f"Error deleting employee: {str(e)}")
            st.error(f"Error deleting employee: {str(e)}")

    # Save data button
    if st.button("حفظ البيانات"):
        try:
            save_data(st.session_state.df)
            st.success("تم حفظ البيانات بنجاح!")
        except Exception as e:
            st.error(f"Error saving data: {str(e)}")
            logging.error(f"Error saving data: {str(e)}\n{traceback.format_exc()}")

if __name__ == "__main__":
    main()