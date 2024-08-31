import os
port=os.environ.get('PORT', '8000')
bind = f'0.0.0.0:{port}'
workers=3
