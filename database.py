
# database.py
from pymongo import MongoClient
from config import MONGO_URI, DATABASE_NAME
import datetime

class Database:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DATABASE_NAME]
        
    def create_user(self, username, password_hash):
        return self.db.users.insert_one({
            'username': username,
            'password': password_hash,
            'created_at': datetime.datetime.utcnow()
        })
    
    def get_user(self, username):
        return self.db.users.find_one({'username': username})
    
    def add_expense(self, user_id, amount, category, description, date):
        # Convert date to datetime at midnight for consistent storage
        if isinstance(date, datetime.date):
            date = datetime.datetime.combine(date, datetime.datetime.min.time())
        
        return self.db.expenses.insert_one({
            'user_id': user_id,
            'amount': float(amount),
            'category': category,
            'description': description,
            'date': date,
            'created_at': datetime.datetime.utcnow()
        })
    
    def get_user_expenses(self, user_id, start_date=None, end_date=None):
        query = {'user_id': user_id}
        if start_date and end_date:
            # Convert dates to datetime for query
            start_datetime = datetime.datetime.combine(start_date, datetime.datetime.min.time())
            end_datetime = datetime.datetime.combine(end_date, datetime.datetime.max.time())
            query['date'] = {'$gte': start_datetime, '$lte': end_datetime}
        return list(self.db.expenses.find(query).sort('date', -1))
    
    def get_category_summary(self, user_id, start_date=None, end_date=None):
        query = [
            {'$match': {'user_id': user_id}},
            {'$group': {
                '_id': '$category',
                'total': {'$sum': '$amount'},
                'count': {'$sum': 1}
            }}
        ]
        if start_date and end_date:
            # Convert dates to datetime for query
            start_datetime = datetime.datetime.combine(start_date, datetime.datetime.min.time())
            end_datetime = datetime.datetime.combine(end_date, datetime.datetime.max.time())
            query[0]['$match']['date'] = {'$gte': start_datetime, '$lte': end_datetime}
        return list(self.db.expenses.aggregate(query))