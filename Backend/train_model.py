import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
import joblib

print("🧠 Booting up the Machine Learning pipeline...")

# 1. READ THE TEXTBOOK
df = pd.read_csv('hospital_appointments.csv')

# 2. SEPARATE CLUES AND ANSWERS
X = df[['Age', 'Distance_Miles', 'Lead_Time_Days', 'Previous_No_Shows']]
y = df['Show_Up']

# 3. SPLIT THE DATA
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ==========================================
# 🚀 NEW: FEATURE SCALING!
# ==========================================
print("📏 Scaling the features so the math doesn't overflow...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 4. TRAIN THE AI (Using the scaled data)
print("📚 Training the Logistic Regression model...")
model = LogisticRegression()
model.fit(X_train_scaled, y_train) 

# 5. GIVE THE FINAL EXAM
predictions = model.predict(X_test_scaled)
accuracy = accuracy_score(y_test, predictions)

print(f"🎯 Final Exam Score (Accuracy): {accuracy * 100:.2f}%")

# 6. SAVE BOTH THE BRAIN AND THE RULER
joblib.dump(model, 'noshow_model.pkl')
joblib.dump(scaler, 'scaler.pkl') # We must save the scaler so we can scale new patients later!
print("✅ Model and Scaler saved successfully!")