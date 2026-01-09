from routes import app

if __name__ == "__main__":
    # 不在開發環境顯示 debug stacktrace
    app.run(host="0.0.0.0", port=5000, debug=False)
