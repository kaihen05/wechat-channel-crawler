from sqlalchemy import create_engine, inspect

engine = create_engine('sqlite:///./data/channels.db')
inspector = inspect(engine)
columns = inspector.get_columns('channels')
print('Current table columns:')
for col in columns:
    print(f'  {col["name"]}: {col["type"]}')

# Check if category column exists
category_exists = any(col['name'] == 'category' for col in columns)
print(f'\nCategory column exists: {category_exists}')

if not category_exists:
    print('\n!!! Category column is missing!')
    print('Need to delete old database and recreate...')
    import os
    if os.path.exists('./data/channels.db'):
        os.remove('./data/channels.db')
        print('Old database deleted')
        print('Please restart the server to create new database with category column')
