import sys
import os

# Add 'src' to the python path so imports work correctly
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.app import create_app

app = create_app()

if __name__ == '__main__':
    # Use 0.0.0.0 so it works on LAN (other computers can connect)
    app.run(debug=True, host='0.0.0.0', port=5000)
