from src.state_machine import QualificationState

def test_perfect_eligible_customer():
    state = QualificationState()
    state.update_from_utterance({
        "property_type": "Residential",
        "ownership_status": "Sole",
        "documents_available": True,
        "loan_amount": 5000000,
        "occupation": "Salaried",
        "income_mode": "Bank",
        "market_value": "1 Crore",
        "tenure": 10
    })
    assert state.disqualified is False
    assert state.get_first_missing_question() is None

def test_agricultural_disqualification():
    state = QualificationState()
    state.update_from_utterance({"property_type": "Agricultural"})
    assert state.disqualified is True

def test_cash_income_disqualification():
    state = QualificationState()
    state.update_from_utterance({"occupation": "Self-Employed", "income_mode": "Cash"})
    assert state.disqualified is True

def test_out_of_order_extraction():
    state = QualificationState()
    state.update_from_utterance({"property_type": "Commercial", "market_value": "80 Lakhs"})
    
    assert state.get_first_missing_question() == "ownership_status"