from website import create_app

app = create_app()

@app.route("/")
def home():
    return "Hello from main.py + website package!"

if __name__ == "__main__":
    print("Starting Flask dev server on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", debug=True)


