import joblib

print("🔍 Loading the AI Brain and Scaler...")

# 1. Load the saved model and ruler (scaler)
model = joblib.load('noshow_model.pkl')
scaler = joblib.load('scaler.pkl')

# 2. Create our test patients
# Format: [Age, Distance_Miles, Lead_Time_Days, Previous_No_Shows]
perfect_patient = [[30, 5, 2, 0]]   # 30 yrs old, 5 miles away, booked 2 days ago, 0 no-shows
risky_patient = [[25, 45, 60, 3]]   # 25 yrs old, 45 miles away, booked 60 days ago, 3 no-shows

# 3. Scale the data (CRITICAL: The AI only understands scaled numbers now!)
perfect_scaled = scaler.transform(perfect_patient)
risky_scaled = scaler.transform(risky_patient)

# 4. Ask the AI for its predictions
perfect_pred = model.predict(perfect_scaled)[0]
risky_pred = model.predict(risky_scaled)[0]

# Ask for the exact probability (confidence level) of a No-Show
perfect_risk = model.predict_proba(perfect_scaled)[0][0] * 100
risky_risk = model.predict_proba(risky_scaled)[0][0] * 100

print("\n=== 🩺 AI PREDICTION RESULTS ===")
print(f"Perfect Patient -> Prediction: {'Show' if perfect_pred == 1 else 'No-Show'} (Risk: {perfect_risk:.1f}%)")
print(f"Risky Patient   -> Prediction: {'Show' if risky_pred == 1 else 'No-Show'} (Risk: {risky_risk:.1f}%)")
print("================================")