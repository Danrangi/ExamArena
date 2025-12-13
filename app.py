from exam_app import create_app

# Create and run the application factory
app = create_app()

if __name__ == '__main__':
    # Run the app, accessible on the local network IP
    app.run(debug=True, host='0.0.0.0', port=5000)