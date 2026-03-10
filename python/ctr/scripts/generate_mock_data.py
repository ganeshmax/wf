import os
import random
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta

def generate_mock_data(num_customers=500, num_locations=50, num_transactions=5000):
    fake = Faker()
    
    # Ensure directories exist
    os.makedirs('data/raw', exist_ok=True)
    
    print("Generating Customers...")
    customers = []
    entity_types = ['Individual', 'Corporation', 'LLC', 'Partnership']
    for i in range(num_customers):
        # 70% chance of being an individual, 30% chance business
        e_type = random.choices(entity_types, weights=[0.7, 0.1, 0.15, 0.05])[0]
        
        if e_type == 'Individual':
            first = fake.first_name()
            last = fake.last_name()
            tin = fake.ssn()
            dob = fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat()
        else:
            first = fake.company()
            last = ""
            tin = fake.ein()
            dob = fake.date_this_century().isoformat() # Date of Incorporation
            
        customers.append({
            'customer_id': f"cust_{i+1:06d}",
            'entity_type': e_type,
            'first_name': first,
            'last_name': last,
            'tin': tin,
            'address': fake.street_address(),
            'city': fake.city(),
            'state': fake.state_abbr(),
            'zip': fake.zipcode(),
            'dob': dob
        })
    customers_df = pd.DataFrame(customers)
    customers_df.to_csv('data/raw/customers.csv', index=False)
    
    print("Generating Non-Customers (Shadow Profiles)...")
    non_customers = []
    num_non_customers = int(num_customers * 0.4) # Just arbitrary size for non-account holders
    for i in range(num_non_customers):
        non_customers.append({
            'customer_id': f"noncust_{i+1:06d}", # "customer_id" column name reused for schema consistency
            'entity_type': 'Individual',
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'tin': fake.ssn(),
            'address': fake.street_address(),
            'city': fake.city(),
            'state': fake.state_abbr(),
            'zip': fake.zipcode(),
            'dob': fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat()
        })
    non_customers_df = pd.DataFrame(non_customers)
    non_customers_df.to_csv('data/raw/non_customers.csv', index=False)
    
    print("Generating DOEP Exemptions...")
    exemptions = []
    # Arbitrarily exempt 5% of business customers (Phase II like)
    business_customers = customers_df[customers_df['entity_type'] != 'Individual']['customer_id'].tolist()
    num_exempt = max(1, int(len(business_customers) * 0.05))
    
    for cust_id in random.sample(business_customers, num_exempt):
        exemptions.append({
            'customer_id': cust_id,
            'phase_type': random.choice(['PHASE_I', 'PHASE_II']),
            'expiration_date': fake.date_between(start_date='+1y', end_date='+2y').isoformat()
        })
    exemptions_df = pd.DataFrame(exemptions)
    exemptions_df.to_csv('data/raw/exemptions.csv', index=False)
    
    print("Generating Locations...")
    locations = []
    for i in range(num_locations):
        locations.append({
            'location_id': f"loc_{i+1:05d}",
            'location_name': fake.company(),
            'address': fake.street_address(),
            'city': fake.city(),
            'state': fake.state_abbr(),
            'zip': fake.zipcode()
        })
    locations_df = pd.DataFrame(locations)
    locations_df.to_csv('data/raw/locations.csv', index=False)
    
    print("Generating Accounts and Ownership Profiles...")
    accounts = []
    account_owners = []
    num_accounts = int(num_customers * 1.2) # Some customers have multiple accounts
    
    customer_ids = customers_df['customer_id'].tolist()
    
    for i in range(num_accounts):
        account_id = f"acc_{i+1:06d}"
        accounts.append({
            'account_id': account_id,
            'account_type': random.choice(['CHECKING', 'SAVINGS', 'BUSINESS'])
        })
        
        # Guarantee every customer gets at least one account first
        if i < num_customers:
            primary_owner = customer_ids[i]
        else:
            primary_owner = random.choice(customer_ids)
            
        # 80% Single Owner, 20% Joint (2 owners)
        is_joint = random.random() < 0.2
        
        account_owners.append({
            'account_id': account_id,
            'customer_id': primary_owner,
            'ownership_type': 'PRIMARY'
        })
        
        if is_joint:
            secondary_owner = random.choice([c for c in customer_ids if c != primary_owner])
            account_owners.append({
                'account_id': account_id,
                'customer_id': secondary_owner,
                'ownership_type': 'JOINT'
            })
            
    accounts_df = pd.DataFrame(accounts)
    accounts_df.to_csv('data/raw/accounts.csv', index=False)
    
    accounts_owners_df = pd.DataFrame(account_owners)
    accounts_owners_df.to_csv('data/raw/account_owners.csv', index=False)
    
    print("Generating Transactions...")
    # Generate transactions over a simulated weekend (Thursday -> Tuesday)
    base_date = datetime.now()
    # Find the most recent Thursday
    days_to_subtract = (base_date.weekday() - 3) % 7
    start_date = base_date - timedelta(days=days_to_subtract)
    end_date = start_date + timedelta(days=5) # Up to Tuesday
    
    transactions = []
    transaction_types = ['DEPOSIT', 'WITHDRAWAL', 'WIRE_TRANSFER', 'CHECK_DEPOSIT', 'MONETARY_INSTRUMENT_PURCHASE']
    
    non_customer_ids = non_customers_df['customer_id'].tolist()
    location_ids = locations_df['location_id'].tolist()
    account_ids = accounts_df['account_id'].tolist()
    
    for i in range(num_transactions):
        # 5% chance of a high-value cash transaction to ensure realistic CTR distributions
        is_ctr_candidate = random.random() < 0.05
        is_mil_candidate = random.random() < 0.02
        
        if is_ctr_candidate:
            amount = round(random.uniform(9000.0, 15000.0), 2)
            t_type = random.choice(['DEPOSIT', 'WITHDRAWAL'])
            is_cash = True
        elif is_mil_candidate:
            amount = round(random.uniform(3000.0, 9999.0), 2)
            t_type = 'MONETARY_INSTRUMENT_PURCHASE'
            is_cash = True
        else:
            amount = round(random.uniform(10.0, 5000.0), 2)
            t_type = random.choice(transaction_types)
            is_cash = t_type in ['DEPOSIT', 'WITHDRAWAL', 'MONETARY_INSTRUMENT_PURCHASE'] and random.random() < 0.8
            
        timestamp = fake.date_time_between_dates(
            datetime_start=start_date.replace(hour=0, minute=0, second=0),
            datetime_end=end_date.replace(hour=23, minute=59, second=59)
        ).isoformat()
        
        target_account_id = random.choice(account_ids) 
        
        rand_cond = random.random()
        if rand_cond < 0.5:
            # Conductor is an owner of the account
            account_owners_subset = accounts_owners_df[accounts_owners_df['account_id'] == target_account_id]
            conductor_id = random.choice(account_owners_subset['customer_id'].tolist())
        elif rand_cond < 0.8:
            # Conductor is a non-customer
            conductor_id = random.choice(non_customer_ids)
        else:
            # Conductor is a random different customer
            conductor_id = random.choice(customer_ids)
            
        transactions.append({
            'transaction_id': f"tx_{i+1:07d}",
            'account_id': target_account_id,
            'conductor_id': conductor_id,
            'location_id': random.choice(location_ids),
            'timestamp': timestamp,
            'amount': amount,
            'transaction_type': t_type,
            'is_cash': is_cash,
            'currency': 'USD'
        })
        
    print("Injecting complex relational edge cases for FinCEN Phase 9 testing...")
    edge_loc = location_ids[0]
    
    # Edge Case 1: Joint Account Structured Split over the Weekend
    # Conductor 1 drops $4k on Saturday, $4k on Sunday, $3k on Monday into a JOINT ACCOUNT (Owners A & B)
    # This must roll forward into a single $11000 Monday report naming A & B as primary beneficiaries!
    saturday_time = (start_date + timedelta(days=2)).replace(hour=12, minute=0).isoformat()
    sunday_time = (start_date + timedelta(days=3)).replace(hour=14, minute=0).isoformat()
    monday_time = (start_date + timedelta(days=4)).replace(hour=10, minute=0).isoformat()
    
    # Find a guaranteed joint account
    joint_accs_counts = accounts_owners_df.groupby('account_id').size()
    joint_account_id = joint_accs_counts[joint_accs_counts > 1].index[0]
    cond_1 = customer_ids[1] # Unrelated conductor
    
    transactions.extend([
        {'transaction_id': f"tx_{num_transactions+1:07d}", 'account_id': joint_account_id, 'conductor_id': cond_1, 'location_id': edge_loc, 'timestamp': saturday_time, 'amount': 4000.0, 'transaction_type': 'DEPOSIT', 'is_cash': True, 'currency': 'USD'},
        {'transaction_id': f"tx_{num_transactions+2:07d}", 'account_id': joint_account_id, 'conductor_id': cond_1, 'location_id': edge_loc, 'timestamp': sunday_time, 'amount': 4000.0, 'transaction_type': 'DEPOSIT', 'is_cash': True, 'currency': 'USD'},
        {'transaction_id': f"tx_{num_transactions+3:07d}", 'account_id': joint_account_id, 'conductor_id': cond_1, 'location_id': edge_loc, 'timestamp': monday_time, 'amount': 3000.0, 'transaction_type': 'DEPOSIT', 'is_cash': True, 'currency': 'USD'}
    ])
    
    # Edge Case 2: One Conductor withdrawing Cash-Out for Multiple Accounts on the same Business Day
    # Conductor B withdraws $5000 from Account X, $6000 from Account Y on Friday
    conductor_b = customer_ids[4]
    acc_x = account_ids[5]; acc_y = account_ids[6]
    friday_time = (start_date + timedelta(days=1)).replace(hour=15, minute=0).isoformat()
    
    transactions.extend([
        {'transaction_id': f"tx_{num_transactions+4:07d}", 'account_id': acc_x, 'conductor_id': conductor_b, 'location_id': edge_loc, 'timestamp': friday_time, 'amount': 5000.0, 'transaction_type': 'WITHDRAWAL', 'is_cash': True, 'currency': 'USD'},
        {'transaction_id': f"tx_{num_transactions+5:07d}", 'account_id': acc_y, 'conductor_id': conductor_b, 'location_id': edge_loc, 'timestamp': friday_time, 'amount': 6000.0, 'transaction_type': 'WITHDRAWAL', 'is_cash': True, 'currency': 'USD'}
    ])
    
    # Edge Case 3: Structuring Detection (SAR Alert - $9,900 multiple times)
    acc_struct = account_ids[8]
    structurer_idx = accounts_owners_df[accounts_owners_df['account_id'] == acc_struct]['customer_id'].tolist()[0]
    struct_thursday = (start_date).replace(hour=11, minute=0).isoformat()
    struct_friday = (start_date + timedelta(days=1)).replace(hour=11, minute=0).isoformat()
    transactions.extend([
        {'transaction_id': f"tx_{num_transactions+6:07d}", 'account_id': acc_struct, 'conductor_id': structurer_idx, 'location_id': edge_loc, 'timestamp': struct_thursday, 'amount': 9500.0, 'transaction_type': 'DEPOSIT', 'is_cash': True, 'currency': 'USD'},
        {'transaction_id': f"tx_{num_transactions+7:07d}", 'account_id': acc_struct, 'conductor_id': structurer_idx, 'location_id': edge_loc, 'timestamp': struct_friday, 'amount': 9500.0, 'transaction_type': 'DEPOSIT', 'is_cash': True, 'currency': 'USD'}
    ])
    
    # Edge Case 4: Missing TINs for Maker/Checker
    # Inject 5 high-value transactions for customers, but forcefully blank out their TINs in the customers_df
    maker_checker_targets = random.sample(customer_ids[10:50], 5)
    maker_time = (start_date + timedelta(days=1)).replace(hour=10, minute=0).isoformat()
    
    for idx, c_id in enumerate(maker_checker_targets):
        accounts_for_c = accounts_owners_df[accounts_owners_df['customer_id'] == c_id]['account_id'].tolist()
        if not accounts_for_c:
            accounts_for_c = [account_ids[0]]
        acc = accounts_for_c[0]
        
        # Blank out the TIN in the customers dataframe
        customers_df.loc[customers_df['customer_id'] == c_id, 'tin'] = None
        
        transactions.append(
            {'transaction_id': f"tx_{num_transactions+8+idx:07d}", 'account_id': acc, 'conductor_id': c_id, 'location_id': edge_loc, 'timestamp': maker_time, 'amount': 12000.0, 'transaction_type': 'DEPOSIT', 'is_cash': True, 'currency': 'USD'}
        )
    
    # Re-save the customers dataframe with the blanked out TINs
    customers_df.to_csv('data/raw/customers.csv', index=False)
        
    transactions_df = pd.DataFrame(transactions)
    transactions_df.to_csv('data/raw/transactions.csv', index=False)
    
    print("Mock data generation complete!")
    print(f"Generated {num_customers} customers, {num_accounts} accounts, and {num_transactions} transactions.")

if __name__ == "__main__":
    generate_mock_data()
