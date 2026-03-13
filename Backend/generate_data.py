import pandas as pd
import random

print("Generating 1,000 past hospital appointments...")

data = []
for _ in range(1000):
    age = random.randint(18, 90)
    distance = random.randint(1, 50) # Miles away from hospital
    lead_time = random.randint(1, 90) # Days between booking and the appointment
    prev_no_shows = random.randint(0, 4) # How many times they ghosted the doctor before
    
    # We are planting a secret pattern for the AI to discover:
    # If they live far away, booked a long time ago, or have a history of ghosting, they are high risk!
    risk_score = (distance * 0.2) + (lead_time * 0.3) + (prev_no_shows * 15)
    
    if risk_score > 35:
        show_up = 0 # 0 means No-Show (Bad)
    else:
        show_up = 1 # 1 means They Showed Up (Good)
        
    # Add 10% randomness to simulate real human unpredictability
    if random.random() < 0.1: 
        show_up = 1 if show_up == 0 else 0
        
    data.append([age, distance, lead_time, prev_no_shows, show_up])

# Create the spreadsheet and save it
df = pd.DataFrame(data, columns=['Age', 'Distance_Miles', 'Lead_Time_Days', 'Previous_No_Shows', 'Show_Up'])
df.to_csv('hospital_appointments.csv', index=False)

print("Success! 'hospital_appointments.csv' has been created.")