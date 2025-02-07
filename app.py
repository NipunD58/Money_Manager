import streamlit as st
import pandas as pd
import plotly.express as px
from database import Database
from auth import hash_password, verify_password
from datetime import datetime, timedelta
import plotly.graph_objects as go

from ai_analysis import AiAnalyzer

class MoneyManager:

    def initialize_session_state(self):
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
        if 'user_id' not in st.session_state:
            st.session_state.user_id = None

    def __init__(self):
        self.db = Database()
        self.ai_analyzer = AiAnalyzer()
        self.initialize_session_state()
    
    def main_page(self):
        st.title("Money Manager Dashboard")
        
        # Updated navigation with AI Analysis
        page = st.sidebar.selectbox(
            "Navigation", 
            ["Add Expense", "View Expenses", "Analytics", "AI Insights", "Logout"]
        )
        
        if page == "Add Expense":
            self.add_expense_page()
        elif page == "View Expenses":
            self.view_expenses_page()
        elif page == "Analytics":
            self.analytics_page()
        elif page == "AI Insights":
            self.ai_insights_page()

        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.rerun()
    
    def ai_insights_page(self):
        st.header("AI-Powered Financial Insights")
        
        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                datetime.now() - timedelta(days=30)
            )
        with col2:
            end_date = st.date_input("End Date", datetime.now())
        
        expenses = self.db.get_user_expenses(
            st.session_state.user_id,
            start_date,
            end_date
        )
        
        if expenses:
            df = pd.DataFrame(expenses)
            df['date'] = pd.to_datetime(df['date']).dt.date
            
            # Add a spinner while generating AI insights
            with st.spinner("Generating AI insights..."):
                ai_analysis = self.ai_analyzer.analyze_expenses(
                    df[['date', 'category', 'amount', 'description']]
                )
            
            # Display AI analysis in an expandable container
            with st.expander("💡 AI Analysis and Recommendations", expanded=True):
                st.markdown(ai_analysis)
            
            # Display supporting visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                # Daily spending trend
                daily_spending = df.groupby('date')['amount'].sum().reset_index()
                fig1 = px.line(daily_spending, x='date', y='amount',
                              title='Daily Spending Trend')
                st.plotly_chart(fig1)
            
            with col2:
                # Category distribution
                category_spending = df.groupby('category')['amount'].sum()
                fig2 = px.pie(values=category_spending.values,
                             names=category_spending.index,
                             title='Spending Distribution')
                st.plotly_chart(fig2)
            
        else:
            st.info("No expenses found for the selected date range.")
            st.warning("Add some expenses to get AI-powered insights!")

    
            
    def login_page(self):
        st.title("Money Manager - Login")
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login"):
                user = self.db.get_user(username)
                if user and verify_password(password, user['password']):
                    st.session_state.logged_in = True
                    st.session_state.user_id = str(user['_id'])
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        with tab2:
            new_username = st.text_input("Username", key="register_username")
            new_password = st.text_input("Password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            if st.button("Register"):
                if new_password != confirm_password:
                    st.error("Passwords don't match")
                    return
                
                if self.db.get_user(new_username):
                    st.error("Username already exists")
                    return
                
                hashed_password = hash_password(new_password)
                self.db.create_user(new_username, hashed_password)
                st.success("Registration successful! Please login.")
    
    
    
    def add_expense_page(self):
        st.header("Add New Expense")
        
        # Get predefined categories and allow custom input
        categories = ["Food", "Transportation", "Housing", "Utilities", "Entertainment", "Shopping", "Healthcare", "Other"]
        category = st.selectbox("Category", categories)
        
        amount = st.number_input("Amount", min_value=0.01, step=0.01)
        description = st.text_input("Description")
        date = st.date_input("Date", max_value=datetime.now())
        
        if st.button("Add Expense"):
            self.db.add_expense(
                st.session_state.user_id,
                amount,
                category,
                description,
                date
            )
            st.success("Expense added successfully!")
    
    def view_expenses_page(self):
        st.header("View Expenses")
        
        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", datetime.now())
        
        expenses = self.db.get_user_expenses(
            st.session_state.user_id,
            start_date,
            end_date
        )
        
        if expenses:
            df = pd.DataFrame(expenses)
            # Convert datetime to date for display
            df['date'] = pd.to_datetime(df['date']).dt.date
            
            st.dataframe(
                df[['date', 'category', 'amount', 'description']],
                column_config={
                    "amount": st.column_config.NumberColumn(
                        "Amount",
                        format="$%.2f"
                    )
                },
                hide_index=True
            )
            
            total_spent = df['amount'].sum()
            st.metric("Total Spent", f"${total_spent:.2f}")
        else:
            st.info("No expenses found for the selected date range.")
    
    def analytics_page(self):
        st.header("Expense Analytics")
        
        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", datetime.now())
        
        # Get category summary
        category_summary = self.db.get_category_summary(
            st.session_state.user_id,
            start_date,
            end_date
        )
        
        if category_summary:
            df = pd.DataFrame(category_summary)
            df.columns = ['Category', 'Total Amount', 'Count']
            
            # Pie chart for category distribution
            fig1 = px.pie(df, values='Total Amount', names='Category',
                         title='Expense Distribution by Category')
            st.plotly_chart(fig1)
            
            # Bar chart for category comparison
            fig2 = px.bar(df, x='Category', y='Total Amount',
                         title='Total Expenses by Category')
            st.plotly_chart(fig2)
            
            # Display summary table
            st.subheader("Category Summary")
            st.dataframe(
                df,
                column_config={
                    "Total Amount": st.column_config.NumberColumn(
                        "Total Amount",
                        format="$%.2f"
                    )
                },
                hide_index=True
            )
        else:
            st.info("No data available for the selected date range.")

def main():
    st.set_page_config(page_title="Money Manager", layout="wide")
    
    app = MoneyManager()
    
    if not st.session_state.logged_in:
        app.login_page()
    else:
        app.main_page()

if __name__ == "__main__":
    main()