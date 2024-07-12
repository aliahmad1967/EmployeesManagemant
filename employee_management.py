
# Not Complete
# For one record
#########################################################

import streamlit as st
import pandas as pd

def load_data():
    try:
        return pd.read_csv("employees1.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["ID", "Name", "Position", "Salary"])

def save_data(df):
    df.to_csv("employees1.csv", index=False)

def main():
    st.title("Employee Management System")

    # Load existing data
    df = load_data()

    # Sidebar for adding new employees
    st.sidebar.header("Add New Employee")
    new_id = st.sidebar.number_input("Employee ID", min_value=1, step=1)
    new_name = st.sidebar.text_input("Name")
    new_position = st.sidebar.text_input("Position")
    new_salary = st.sidebar.number_input("Salary", min_value=0.0, step=100.0)

    if st.sidebar.button("Add Employee"):
        new_employee = pd.DataFrame({
            "ID": [new_id],
            "Name": [new_name],
            "Position": [new_position],
            "Salary": [new_salary]
        })
        df = pd.concat([df, new_employee], ignore_index=True)
        save_data(df)
        st.sidebar.success("Employee added successfully!")

    # Main page
    st.header("Employee List")
    st.dataframe(df)

    # Delete employee
    st.header("Delete Employee")
    employee_to_delete = st.number_input("Enter Employee ID to delete", min_value=1, step=1)
    if st.button("Delete Employee"):
        df = df[df["ID"] != employee_to_delete]
        save_data(df)
        st.success(f"Employee with ID {employee_to_delete} has been deleted.")

if __name__ == "__main__":
    main()