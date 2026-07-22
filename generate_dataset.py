import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os

fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

NUM_CUSTOMERS = 500
NUM_INVOICES = 5000

print("Generating synthetic customers...")
# 1. Generate Customers
customers = []
for i in range(NUM_CUSTOMERS):
    cust_type = np.random.choice(['B2B', 'B2C'], p=[0.4, 0.6])
    if cust_type == 'B2B':
        name = fake.company()
        industry = np.random.choice(['Retail', 'Construction', 'Services', 'Manufacturing'])
    else:
        name = fake.name()
        industry = 'Residential'
        
    customers.append({
        'customer_id': f"CUST_{i:04d}",
        'name': name,
        'customer_type': cust_type,
        'industry': industry,
        'risk_category': np.random.choice(['Low', 'Medium', 'High'], p=[0.6, 0.3, 0.1])
    })

df_customers = pd.DataFrame(customers)

print("Generating synthetic invoices...")
# 2. Generate Invoices
invoices = []
start_date = datetime(2022, 1, 1).date()
end_date = datetime(2023, 12, 31).date()

for i in range(NUM_INVOICES):
    customer = random.choice(customers)
    
    # Amount based on customer type
    if customer['customer_type'] == 'B2B':
        amount = round(np.random.lognormal(mean=7.5, sigma=1.0), 2)
    else:
        amount = round(np.random.lognormal(mean=5.5, sigma=0.8), 2)
        
    amount = max(50.0, min(amount, 50000.0))
    
    issue_date = fake.date_between(start_date=start_date, end_date=end_date)
    terms = np.random.choice([15, 30, 45, 60], p=[0.2, 0.5, 0.2, 0.1])
    due_date = issue_date + timedelta(days=int(terms))
    
    risk = customer['risk_category']
    if risk == 'Low':
        late_prob = 0.15
    elif risk == 'Medium':
        late_prob = 0.40
    else:
        late_prob = 0.85
        
    is_late = random.random() < late_prob
    is_disputed = random.random() < 0.05
    
    if not is_late:
        days_late = random.randint(-10, 0)
    else:
        days_late = int(np.random.exponential(scale=15)) + 1
        
    if is_disputed:
        days_late += int(np.random.exponential(scale=30))
        
    settled_date = due_date + timedelta(days=days_late)
    
    status = 'Settled'
    if settled_date > datetime(2023, 12, 31).date():
        status = 'Open'
        settled_date = pd.NaT
        days_late = (datetime(2023, 12, 31).date() - due_date).days
        if days_late < 0:
            days_late = 0
            
    invoices.append({
        'invoice_id': f"INV_{i:06d}",
        'customer_id': customer['customer_id'],
        'amount': amount,
        'terms': terms,
        'issue_date': issue_date,
        'due_date': due_date,
        'settled_date': settled_date,
        'days_late': days_late if status == 'Settled' or days_late > 0 else 0,
        'is_late': 1 if (status == 'Settled' and days_late > 0) or (status == 'Open' and days_late > 0) else 0,
        'is_disputed': int(is_disputed),
        'status': status
    })

df_invoices = pd.DataFrame(invoices)

print("Generating synthetic communications (CRM log)...")
# 3. Generate Communications (CRM Log)
communications = []
comm_id_counter = 1

for _, inv in df_invoices.iterrows():
    # Pre-due reminder
    comm_date = inv['due_date'] - timedelta(days=3)
    communications.append({
        'comm_id': f"COMM_{comm_id_counter:06d}",
        'invoice_id': inv['invoice_id'],
        'customer_id': inv['customer_id'],
        'timestamp': comm_date,
        'type': 'Reminder',
        'channel': 'Email',
        'outcome': 'Ignored' if inv['days_late'] > 0 else 'Paid Promptly'
    })
    comm_id_counter += 1
    
    if inv['days_late'] > 0:
        current_date = inv['due_date'] + timedelta(days=1)
        attempt = 1
        
        while current_date <= (inv['settled_date'] if pd.notna(inv['settled_date']) else datetime(2023, 12, 31).date()):
            if attempt == 1:
                channel = 'Email'
            elif attempt == 2:
                channel = np.random.choice(['Email', 'SMS'], p=[0.4, 0.6])
            else:
                channel = np.random.choice(['SMS', 'Call'], p=[0.5, 0.5])
                
            if inv['is_disputed'] == 1 and channel == 'Call':
                outcome = 'Disputed'
            elif channel == 'Call':
                outcome = np.random.choice(['No Answer', 'Left Voicemail', 'Promised to Pay', 'Wrong Number'], p=[0.4, 0.3, 0.25, 0.05])
            elif channel == 'SMS':
                outcome = np.random.choice(['Ignored', 'Replied - Will Pay', 'Opt Out'], p=[0.7, 0.25, 0.05])
            else:
                outcome = np.random.choice(['Ignored', 'Opened', 'Bounced'], p=[0.6, 0.35, 0.05])
                
            if pd.notna(inv['settled_date']) and (inv['settled_date'] - current_date).days <= 3:
                if channel == 'Call':
                    outcome = 'Promised to Pay'
                elif channel == 'SMS':
                    outcome = 'Replied - Will Pay'
                    
            communications.append({
                'comm_id': f"COMM_{comm_id_counter:06d}",
                'invoice_id': inv['invoice_id'],
                'customer_id': inv['customer_id'],
                'timestamp': current_date,
                'type': 'Collection',
                'channel': channel,
                'outcome': outcome
            })
            comm_id_counter += 1
            
            current_date += timedelta(days=random.randint(3, 10))
            attempt += 1

df_comms = pd.DataFrame(communications)

# Make a 'data' dir if it doesn't exist
os.makedirs('data', exist_ok=True)

df_customers.to_csv('data/customers.csv', index=False)
df_invoices.to_csv('data/invoices.csv', index=False)
df_comms.to_csv('data/communications.csv', index=False)

print("Datasets generated successfully in the 'data' directory!")
print(f"- customers.csv: {len(df_customers)} records")
print(f"- invoices.csv: {len(df_invoices)} records")
print(f"- communications.csv: {len(df_comms)} records")
