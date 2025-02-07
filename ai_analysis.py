import google.generativeai as genai
from config import GOOGLE_API_KEY
import pandas as pd

class AiAnalyzer:
    def __init__(self):
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def analyze_expenses(self, expenses_df):
        """
        Analyze expenses using Gemini AI and provide insights and suggestions
        """
        if expenses_df.empty:
            return "No expenses data available for analysis."
        
        # Prepare data summary for AI analysis
        total_spent = expenses_df['amount'].sum()
        category_summary = expenses_df.groupby('category')['amount'].agg(['sum', 'count'])
        top_categories = category_summary.nlargest(3, 'sum')
        
        # Create prompt for Gemini
        prompt = f"""
        As a financial advisor, analyze this expense data and provide insights and suggestions:

        Total Spent: ${total_spent:.2f}

        Top 3 Spending Categories:
        {top_categories.to_string()}

        Full Category Breakdown:
        {category_summary.to_string()}

        Please provide:
        1. Key observations about spending patterns
        2. Specific suggestions for potential savings
        3. Budget recommendations
        4. Any concerning patterns that should be addressed
        5. Positive financial habits observed

        Format the response in clear sections with bullet points where appropriate.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating AI analysis: {str(e)}"