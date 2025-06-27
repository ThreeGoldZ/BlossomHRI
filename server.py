from flask import Flask, request, jsonify

app = Flask(__name__)

def run_happiness():
    print("Happiness triggered")
    return "Happiness OK"

@app.route('/run', methods=['GET'])
def run_function():
    func_name = request.args.get('emotion')
    print(f"Received emotion: {func_name}")

    if func_name == "happiness":
        result = run_happiness()
    else:
        return jsonify({"error": "Unknown emotion"}), 400

    return jsonify({"status": "success", "result": result})

if __name__ == "__main__":
    app.run(host="localhost", port=5001, debug=True)
