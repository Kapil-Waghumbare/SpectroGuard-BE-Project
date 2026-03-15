import argparse
import pickle
from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)

model_data = None


@app.route("/check_phishing", methods=["POST"])
def check_phishing():
    global model_data

    try:
        data = request.json
        url_features = data.get("features")

        if not url_features:
            return jsonify({"error": "No features received"}), 400

        features = np.array([url_features])
        features_scaled = model_data["scaler"].transform(features)

        prob = model_data["model"].predict_proba(features_scaled)[0][1]
        label = "Phishing" if prob > 0.5 else "Legit"

        return jsonify({
            "label": label,
            "score": round(float(prob) * 100, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def start_server(model_path):
    global model_data
    with open(model_path, "rb") as f:
        model_data = pickle.load(f)

    print("Model loaded. Server running at http://127.0.0.1:5000")
    app.run(debug=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--model", type=str, required=True)

    args = parser.parse_args()

    if args.serve:
        start_server(args.model)
