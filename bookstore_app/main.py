from app import create_app

app = create_app()

if __name__ == '__main__':
    # Run the Flask application
    # with debug mode enabled for development.
    app.run(debug=True)
