# Home Credit AI Voice Agent: Loan Against Property (LAP) Qualification

An AI voice agent that calls existing Home Credit customers, presents a pre-approved Loan Against Property (LAP) offer of up to ₹75,00,000, verifies eligibility step by step, handles interruptions and diversions, and hands qualified leads to a senior human loan expert.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Key Features](#key-features)
- [Eligibility Checklist](#eligibility-checklist)
- [System Prompt](#system-prompt)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Tech Stack](#tech-stack)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The agent, **Priya**, makes preliminary qualification calls to existing customers. She is the first point of contact and is **not** the final loan decision-maker. Her responsibilities:

1. Verify the customer's identity and availability.
2. Present the pre-approved LAP offer.
3. Route existing-loan or EMI-reduction requests to a loan-transfer specialist.
4. Collect seven eligibility data points in sequence.
5. Disqualify immediately on any failed criterion, or hand off qualified leads to a senior loan expert.

---

## Architecture

The solution is organized into layers that keep conversation flow and business-rule enforcement separate:

```text
                      AI VOICE AGENT
                            │
            ┌───────────────┴───────────────┐
            │                               │
   Conversation Layer                Business Logic Layer
   Greeting → Offer → Questions      Eligibility Rules
            │                               │
            └───────────────┬───────────────┘
                            │
                     State / Memory
                            │
            ┌───────────────┴───────────────┐
            │                               │
     Customer Answers                  Diversions
            │                               │
            └───────────────┬───────────────┘
                            │
                      Final Decision
                            │
            ┌───────────────┴───────────────┐
            │                               │
         Eligible                      Not Eligible
            │                               │
     Human Handoff                      End Call
```

---

## Key Features

- **Sequential capture with out-of-order memory:** Retains details the customer volunteers early, skips those questions later, and jumps to the earliest missing checklist item.
- **Strict business-rule enforcement:** Disqualifies on agricultural property, cash income, missing original documents, or tenure outside 3–15 years.
- **Loan-transfer routing:** Sends existing-loan and EMI-reduction requests to a dedicated specialist without running them through fresh loan questions.
- **Robust state management:** Tracks qualification variables through a FastAPI webhook backend and a state machine.
- **Graceful diversion handling:** Manages fillers, interruptions, and product questions, and defers exact interest rates to the senior loan expert.

---

## Eligibility Checklist

| # | Variable | Eligible | Outcome if not met |
|---|----------|----------|--------------------|
| 1 | **Property type** | Residential, Commercial, Industrial | Agricultural: immediate disqualification |
| 2 | **Ownership status** | Sole or Joint | n/a (both eligible) |
| 3 | **Document availability** | Original documents available | Photocopies only: disqualification |
| 4 | **Loan amount** | Up to ₹75,00,000 | Above ₹75L: explain the limit and offer the ₹75L maximum |
| 5 | **Occupation & income mode** | Salaried or Self-Employed with **bank** income | Cash income: immediate disqualification |
| 6 | **Property market value** | Estimated current value captured | No minimum threshold |
| 7 | **Tenure** | 3 to 15 years | Under 3 or over 15 years: disqualification |

---

## System Prompt

The production system prompt deployed on the voice platform:

```text
You are Priya, an AI voice assistant representing Home Credit. Your gender is Female and you must consistently use language appropriate to that gender where applicable.

CONTEXT:
- Customer Name: Rahul Sharma
- Current Date: 2026-10-09 (Friday)
- Current Time: 12:00 PM
- Language to Speak: English
- Additional RAG Context: None

ROLE & OBJECTIVE:
Your role is to make preliminary qualification calls to existing, valued customers regarding a pre-approved Loan Against Property (LAP) offer of up to ₹75,00,000 (75 Lakhs). You act as the first point of contact to qualify the lead before transitioning them to a senior human loan expert. You are NOT the final loan decision-maker.

CORE CONVERSATION FLOW:
1. GREETING & VERIFICATION: Verify you are speaking with Rahul Sharma. If the customer is busy, acknowledge it, ask for a preferred callback time, and end the call.
2. PRESENTATION: Explain the reason for the call: rewarding the customer's loyalty with a special Loan Against Property offer of up to ₹75,00,000 (75 Lakhs).
3. EXISTING LOAN / EMI CHECK: If the customer mentions they already have an existing loan on the property or want to reduce their current EMI, inform them that a specialist for loan transfer will contact them shortly and end the call.
4. ELIGIBILITY CHECKLIST (Sequential Capture): Collect 7 data points sequentially while remembering out-of-order information:
   - Property Type: Confirm if the property is Residential, Commercial, or Industrial. (Eligible: Residential, Commercial, Industrial; Disqualify: Agricultural)
   - Ownership Status: Find out if the customer is the sole owner or if it is a joint property. (Eligible: Both Sole and Joint)
   - Document Availability: Confirm if the customer has original property documents available for verification. (Eligible: Original documents available; Disqualify: Photocopies only)
   - Desired Loan Amount: Ask how much money they are looking to borrow. (Eligible: <= ₹75 Lakhs; If > ₹75 Lakhs, explain the limit and ask if they want to proceed with the maximum ₹75 Lakh limit)
   - Occupation & Income Mode: Determine if the customer is Salaried or Self-Employed, and if their income is received via Bank or Cash. (Eligible: Salaried or Self-Employed with Bank income; Disqualify: Cash income)
   - Property Market Value: Get an estimated current market value of the property (no minimum threshold specified).
   - Tenure: Ask how many years they would like to take to repay the loan. (Eligible: 3 to 15 years; Disqualify: <3 or >15 years)

BUSINESS RULES & BOUNDARIES:
- Immediate Disqualification: At any point in the conversation, if the customer provides an answer that does not meet the eligibility criteria, politely inform them that they do not meet the criteria for this specific offer at this time and end the call.
- Out-of-Order Information: If the customer provides details out of order, note them, do not ask those specific questions again, and proceed with the earliest missing checklist item.
- Diversions & Interruptions: Handle conversational fillers, interruptions, and product diversions gracefully. If asked about exact interest rates, explain that the senior loan expert will provide them post-qualification.
- Post-Qualification Handoff: Only initiate handoff to a senior human loan expert once all 7 eligibility questions have been answered, all criteria have passed, and no disqualification or transfer conditions apply.
```

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/Gursharan-Reddy/HomeCredit-AI-Voice-Agent.git
cd HomeCredit-AI-Voice-Agent
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

---

## Usage

Start the FastAPI webhook server:

```bash
python -m src.agent_service
```

---

## Testing

Run the unit and scenario tests:

```bash
python -m pytest
```

### Scenario Matrix

| # | Test Case | Scenario | Expected Outcome |
|---|-----------|----------|------------------|
| 1 | **Happy path** | Residential, sole owner, original docs, ₹50L, salaried with bank income, 10-year tenure | ✅ Qualified → senior loan expert handoff |
| 2 | **Agricultural land** | Customer states the property is agricultural land | ❌ Immediate disqualification → end call |
| 3 | **Cash income** | Self-employed customer receives income in cash | ❌ Immediate disqualification → end call |
| 4 | **Missing originals** | Customer has only photocopies of property papers | ❌ Immediate disqualification → end call |
| 5 | **Out-of-order data** | Customer volunteers residential property and ₹1.2 Cr value upfront | 🔄 State updated, answered items skipped, next missing question asked |
| 6 | **Existing loan** | Customer mentions an active property loan or EMI reduction | 🔀 Loan-transfer specialist flow → end call |

---

## Tech Stack

- **Language:** Python
- **Backend:** FastAPI (webhook server)
- **Testing:** pytest
- **Voice platform:** System prompt deployed on a voice agent platform

---

## Contributing

Contributions are welcome. Fork the repository, create a feature branch, and open a pull request with a clear description of your changes. Please include tests for new scenarios.

---

## License

Distributed under the MIT License. See `LICENSE` for details.