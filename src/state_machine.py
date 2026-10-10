"""
State Machine & Eligibility Evaluator for Home Credit LAP Agent
Handles the 7 eligibility checklist items, out-of-order extraction, and disqualification logic.
"""

class QualificationState:
    def __init__(self):
        self.customer_verified = False
        self.property_type = None          
        self.ownership_status = None       
        self.documents_available = None    
        self.loan_amount = None            
        self.occupation = None             
        self.income_mode = None           
        self.market_value = None           
        self.tenure = None                 
        
        self.existing_property_loan = False
        self.emi_reduction_request = False
        self.disqualified = False
        self.transfer_required = False

    def update_from_utterance(self, extracted_data: dict):
        """Updates internal state with out-of-order data points."""
        for key, value in extracted_data.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        self._evaluate_rules()

    def _evaluate_rules(self):
        """Applies strict business eligibility rules."""

        if self.property_type and self.property_type.lower() == "agricultural":
            self.disqualified = True

        if self.documents_available is False:
            self.disqualified = True

        if self.income_mode and self.income_mode.lower() == "cash":
            self.disqualified = True

        if self.tenure is not None:
            if not (3 <= self.tenure <= 15):
                self.disqualified = True

    def get_first_missing_question(self):
        """Returns the earliest unanswered eligibility item in sequence[cite: 2]."""
        if not self.property_type:
            return "property_type"
        if not self.ownership_status:
            return "ownership_status"
        if not self.documents_available:
            return "documents_available"
        if not self.loan_amount:
            return "loan_amount"
        if not self.occupation or not self.income_mode:
            return "occupation_and_income"
        if not self.market_value:
            return "market_value"
        if not self.tenure:
            return "tenure"
        return None