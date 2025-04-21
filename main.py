# main.py
from react_agent import resolve_ticket_with_agent

# Example Case/Ticket input
case_description = """
Please onboard the UPI payment method for merchant 98765 starting from 20th April 2025.
"""

resolve_ticket_with_agent(case_description)


# Merchant ID: 98765
# Request Type: Add New Payment Method
# Payment Method: UPI
# Effective Date: 2025-04-20