import requests
import json
from typing import Dict, Any

def print_response(title: str, response: requests.Response) -> None:
    print(f"\n{title}")
    print("=" * len(title))
    print(f"Status Code: {response.status_code}")
    try:
        formatted_json = json.dumps(response.json(), indent=2)
        print(f"Response:\n{formatted_json}")
    except json.JSONDecodeError:
        print(f"Raw Response: {response.text}")

def test_health():
    response = requests.get('http://localhost:8000/health')
    print_response("Health Check Response", response)

def test_diagnosis(case: str, symptoms: str) -> None:
    data = {'patient_symptoms': symptoms}
    response = requests.post('http://localhost:8000/diagnose', data=data)
    print_response(f"Diagnosis Response - {case}", response)

if __name__ == '__main__':
    print("Testing AutoMedAI API...")
    
    # Test health endpoint
    test_health()
    
    # Test cases for diagnosis
    test_cases = {
        "Cardiac Emergency": """
            Experiencing severe chest pain, shortness of breath, and dizziness for the past hour. 
            Pain radiates to left arm. Also feeling nauseous and sweating profusely.
        """,
        
        "Neurological Symptoms": """
            Sudden onset of severe headache with neck stiffness. Experiencing confusion, 
            sensitivity to light, and difficulty speaking clearly. Started 2 hours ago.
        """,
        
        "Respiratory Issue": """
            Persistent cough for 5 days with yellow-green phlegm. Having fever of 101°F, 
            chest congestion, and difficulty breathing deeply. Fatigue and body aches present.
        """,
        
        "Digestive Problem": """
            Severe abdominal pain in lower right quadrant, nausea, and loss of appetite. 
            Pain worsens with movement. Mild fever present. No bowel movement for 24 hours.
        """,
        
        "Complex Case": """
            Diabetic patient with history of hypertension presenting with blurred vision, 
            frequent urination, fatigue, and numbness in feet. Blood sugar reading 285 mg/dL. 
            Also experiencing mild chest discomfort and anxiety.
        """
    }
    
    # Run each test case
    for case_name, symptoms in test_cases.items():
        # Clean up the symptoms text
        clean_symptoms = " ".join(symptoms.split())
        test_diagnosis(case_name, clean_symptoms)
        print("\n" + "-"*80) 