# Generated from: health.ipynb
# Converted at: 2026-06-09T12:25:49.965Z
# Next step (optional): refactor into modules & generate tests with RunCell
# Quick start: pip install runcell

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

import gradio as gr

from vllm import LLM
from vllm import SamplingParams

import torch

llm = None
sampling_params = None


def get_llm():

    global llm
    global sampling_params

    if llm is None:

        llm = LLM(
            model="Qwen/Qwen2.5-0.5B-Instruct",
            gpu_memory_utilization=0.05
        )

        sampling_params = SamplingParams(
            temperature=0.0,
            max_tokens=300
        )

    return llm, sampling_params


os.makedirs(
    "reports",
    exist_ok=True
)

os.makedirs(
    "exports",
    exist_ok=True
)

os.listdir()

patient = {

    "age": 58,

    "gender": "Male",

    "weight": 92,

    "height": 170,

    "symptoms": [
        "Chest Pain",
        "Shortness of Breath"
    ],

    "severity": 9,

    "medical_history": [
        "Diabetes",
        "Hypertension"
    ],

    "medications": [
        "Metformin"
    ],

    "heart_rate": 118,

    "temperature": 99.4,

    "spo2": 91
}

config = {

    "project":
        "AI Healthcare Intelligence Platform",

    "model":
        "Qwen/Qwen2.5-0.5B-Instruct",

    "acceleration":
        "AMD ROCm"
}

with open(
    "config.json",
    "w"
) as f:

    json.dump(
        config,
        f,
        indent=4
    )

def calculate_bmi(
    weight,
    height
):

    height_m = height / 100

    return round(
        weight / (
            height_m ** 2
        ),
        2
    )

bmi = calculate_bmi(
    patient["weight"],
    patient["height"]
)

print(bmi)

def bmi_category(
    bmi
):

    if bmi < 18.5:
        return "Underweight"

    elif bmi < 25:
        return "Normal"

    elif bmi < 30:
        return "Overweight"

    else:
        return "Obese"

print(
    bmi_category(bmi)
)

def vitals_risk(patient):

    risk = 0

    if patient["heart_rate"] > 110:
        risk += 20

    if patient["temperature"] > 100.4:
        risk += 10

    if patient["spo2"] < 92:
        risk += 40

    return risk

vitals_score = vitals_risk(
    patient
)

def history_risk(patient):

    risk = 0

    history = [
        x.lower()
        for x in
        patient["medical_history"]
    ]

    if "diabetes" in history:
        risk += 20

    if "hypertension" in history:
        risk += 20

    return risk

history_score = history_risk(
    patient
)

critical_symptoms = [

    "chest pain",

    "shortness of breath",

    "loss of consciousness",

    "severe bleeding"
]

high_risk_symptoms = [

    "fever",

    "dizziness",

    "palpitations"
]

def symptom_risk(patient):

    score = 0

    symptoms = [
        s.lower()
        for s in
        patient["symptoms"]
    ]

    for symptom in symptoms:

        if symptom in critical_symptoms:
            score += 50

        elif symptom in high_risk_symptoms:
            score += 20

    score += (
        patient["severity"] * 2
    )

    return score

symptom_score = symptom_risk(
    patient
)

def bmi_risk(bmi):

    if bmi >= 30:
        return 20

    elif bmi >= 25:
        return 10

    return 0

bmi_score = bmi_risk(
    bmi
)

def total_risk(patient):

    bmi = calculate_bmi(
        patient["weight"],
        patient["height"]
    )

    total = 0

    total += vitals_risk(patient)

    total += history_risk(patient)

    total += symptom_risk(patient)

    total += bmi_risk(bmi)

    return total

risk_score = total_risk(
    patient
)

def urgency_level(score):

    if score >= 150:
        return "CRITICAL"

    elif score >= 100:
        return "HIGH"

    elif score >= 50:
        return "MEDIUM"

    return "LOW"

urgency = urgency_level(
    risk_score
)

def patient_summary(
    patient
):

    return {

        "BMI":
            calculate_bmi(
                patient["weight"],
                patient["height"]
            ),

        "Risk Score":
            total_risk(
                patient
            ),

        "Urgency":
            urgency_level(
                total_risk(patient)
            )
    }

summary = patient_summary(
    patient
)

print(summary)

dashboard_df = pd.DataFrame(
    {
        "Metric": [
            "BMI",
            "Risk Score"
        ],

        "Value": [
            bmi,
            risk_score
        ]
    }
)

def build_healthcare_prompt(
    patient,
    bmi,
    risk_score,
    urgency
):

    return f"""
You are an AI Healthcare Intelligence Assistant.

Patient Information

Age: {patient['age']}
Gender: {patient['gender']}

BMI: {bmi}

Symptoms:
{', '.join(patient['symptoms'])}

Severity:
{patient['severity']}/10

Medical History:
{', '.join(patient['medical_history'])}

Current Medications:
{', '.join(patient['medications'])}

Heart Rate:
{patient['heart_rate']}

Temperature:
{patient['temperature']}

SpO2:
{patient['spo2']}

Calculated Risk Score:
{risk_score}

Urgency Level:
{urgency}

Generate:

1. Patient Summary
2. Risk Assessment
3. Contributing Risk Factors
4. Recommended Actions
5. Health Monitoring Advice
6. Disclaimer

Keep response under 250 words.

Do not provide a medical diagnosis.
"""

def generate_vllm_report(
    patient
):

    bmi = calculate_bmi(
        patient["weight"],
        patient["height"]
    )

    risk_score = total_risk(
        patient
    )

    urgency = urgency_level(
        risk_score
    )

    prompt = build_healthcare_prompt(
        patient,
        bmi,
        risk_score,
        urgency
    )

    llm, sampling_params = get_llm()

    outputs = llm.generate(
        [prompt],
        sampling_params
    )

    response = outputs[0].outputs[0].text

    return response


def healthcare_dashboard(

    age,
    gender,
    weight,
    height,

    symptoms,

    severity,

    medical_history,

    medications,

    heart_rate,

    temperature,

    spo2
):

    patient = {

        "age": age,

        "gender": gender,

        "weight": weight,

        "height": height,

        "symptoms": symptoms,

        "severity": severity,

        "medical_history": [

            s.strip()

            for s in medical_history.split(",")
        ],

        "medications": [

            s.strip()

            for s in medications.split(",")
        ],

        "heart_rate": heart_rate,

        "temperature": temperature,

        "spo2": spo2
    }

    bmi = calculate_bmi(
        weight,
        height
    )

    risk_score = total_risk(
        patient
    )

    urgency = urgency_level(
        risk_score
    )

    report = generate_vllm_report(
        patient
    )

    output = {

        "bmi": bmi,

        "risk_score": risk_score,

        "urgency": urgency,

        "report": report
    }

    with open(
        "healthcare_report.json",
        "w"
    ) as f:

        json.dump(
            output,
            f,
            indent=4
        )

    return (
        report,
        bmi,
        risk_score,
        urgency,
        "healthcare_report.json"
    )

import gradio as gr

with gr.Blocks(
    title="AI Healthcare Intelligence Platform"
) as app:

    gr.Markdown(
        """
# 🏥 AI Healthcare Intelligence Platform

AMD ROCm + vLLM Powered Healthcare Risk Assessment

⚠ Educational Use Only
"""
    )

    # -------------------------
    # Patient Information
    # -------------------------

    with gr.Row():

        age = gr.Number(
            label="Age",
            value=40
        )

        gender = gr.Dropdown(
            choices=[
                "Male",
                "Female",
                "Other"
            ],
            value="Male",
            label="Gender"
        )

    # -------------------------
    # Physical Metrics
    # -------------------------

    with gr.Row():

        weight = gr.Number(
            label="Weight (kg)"
        )

        height = gr.Number(
            label="Height (cm)"
        )

    # -------------------------
    # Symptoms
    # -------------------------

    symptoms = gr.Dropdown(

        choices=[

            "Chest Pain",
            "Shortness of Breath",
            "Fever",
            "Cough",
            "Headache",
            "Dizziness",
            "Fatigue",
            "Nausea",
            "Vomiting",
            "Diarrhea",
            "Abdominal Pain",
            "Back Pain",
            "Sore Throat",
            "Runny Nose",
            "Loss of Appetite",
            "Loss of Consciousness",
            "Palpitations",
            "High Blood Pressure",
            "Low Blood Pressure",
            "Severe Bleeding",
            "Blurred Vision",
            "Joint Pain",
            "Muscle Pain",
            "Skin Rash",
            "Anxiety",
            "Depression",
            "Insomnia"

        ],

        multiselect=True,
        filterable=True,
        allow_custom_value=True,
        label="Symptoms"
    )

    severity = gr.Slider(
        minimum=1,
        maximum=10,
        value=5,
        step=1,
        label="Severity"
    )

    # -------------------------
    # Medical History
    # -------------------------

    medical_history = gr.Textbox(
        lines=2,
        label="Medical History"
    )

    medications = gr.Textbox(
        lines=2,
        label="Current Medications"
    )

    # -------------------------
    # Vital Signs
    # -------------------------

    with gr.Row():

        heart_rate = gr.Number(
            label="Heart Rate"
        )

        temperature = gr.Number(
            label="Temperature (°F)"
        )

        spo2 = gr.Number(
            label="SpO₂ (%)"
        )

    # -------------------------
    # Analyze Button
    # -------------------------

    analyze_btn = gr.Button(
        "Analyze Patient",
        variant="primary"
    )

    # -------------------------
    # Outputs
    # -------------------------

    with gr.Row():

        bmi_output = gr.Number(
            label="BMI"
        )

        risk_output = gr.Number(
            label="Risk Score"
        )

        urgency_output = gr.Textbox(
            label="Urgency Level"
        )

    report_output = gr.Textbox(
        label="Healthcare Intelligence Report",
        lines=18
    )

    download_json = gr.File(
        label="Download JSON Report"
    )

    # -------------------------
    # Connect Backend
    # -------------------------

    analyze_btn.click(

        fn=healthcare_dashboard,

        inputs=[

            age,
            gender,
            weight,
            height,
            symptoms,
            severity,
            medical_history,
            medications,
            heart_rate,
            temperature,
            spo2
        ],

        outputs=[

            report_output,
            bmi_output,
            risk_output,
            urgency_output,
            download_json
        ]
    )

if __name__ == "__main__":
    app.launch(share=True)