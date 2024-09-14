# mm-shopping-cart/app.py

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)  # Ensure it's running on the default port or configure as needed
