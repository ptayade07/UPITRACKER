import re
from datetime import datetime

def parse_upi_sms(sms_text):
    result = {}

    # Amount
    amount_match = re.search(r'(?:Rs\.?|INR)\s*([\d,]+(?:\.\d{1,2})?)', sms_text, re.IGNORECASE)
    if amount_match:
        result['amount'] = float(amount_match.group(1).replace(',', ''))

    # Debit or Credit
    if re.search(r'\b(debited|paid|sent|payment of)\b', sms_text, re.IGNORECASE):
        result['transaction_type'] = 'debit'
    elif re.search(r'\b(credited|received)\b', sms_text, re.IGNORECASE):
        result['transaction_type'] = 'credit'

    # Payment app
    sms_lower = sms_text.lower()
    if 'gpay' in sms_lower or 'google pay' in sms_lower:
        result['payment_app'] = 'gpay'
    elif 'phonepe' in sms_lower or 'phone pe' in sms_lower:
        result['payment_app'] = 'phonepe'
    elif 'paytm' in sms_lower:
        result['payment_app'] = 'paytm'
    else:
        result['payment_app'] = 'bank'

    # UPI reference number
    ref_match = re.search(r'(?:UPI Ref|Ref No|Ref|UPI Ref No)[\s.:]*(\d+)', sms_text, re.IGNORECASE)
    if ref_match:
        result['upi_ref'] = ref_match.group(1)

    # Merchant name — "to <merchant>" or "at <merchant>"
    merchant_match = re.search(r'(?:to|at)\s+([A-Za-z0-9 _&.\'-]{3,40}?)(?:\s+on|\s+via|\s+using|\s+UPI|\.|\Z)', sms_text, re.IGNORECASE)
    if merchant_match:
        result['merchant'] = merchant_match.group(1).strip()

    # Date
    date_match = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', sms_text)
    if date_match:
        raw_date = date_match.group(1)
        for fmt in ('%d-%m-%Y', '%d/%m/%Y', '%d-%m-%y', '%d/%m/%y'):
            try:
                result['date'] = datetime.strptime(raw_date, fmt)
                break
            except ValueError:
                continue

    result['raw_sms'] = sms_text

    result['category'] = detect_category(
        result.get('merchant', ''), 
        sms_text
    )

    return result

CATEGORY_RULES = {
    'Food': ['swiggy', 'zomato', 'blinkit', 'zepto', 'dominos', 'mcdonalds', 'kfc', 'subway', 'dunzo', 'bigbasket', 'grofers'],
    'Transport': ['uber', 'ola', 'rapido', 'irctc', 'redbus', 'metro', 'petrol', 'fuel'],
    'Entertainment': ['netflix', 'spotify', 'prime', 'hotstar', 'youtube', 'bookmyshow', 'pvr', 'inox'],
    'Shopping': ['amazon', 'flipkart', 'myntra', 'nykaa', 'ajio', 'meesho', 'snapdeal'],
    'Bills': ['airtel', 'jio', 'vodafone', 'bsnl', 'electricity', 'bescom', 'mahadiscom', 'tata'],
    'Health': ['pharmacy', 'medplus', 'apollo', 'practo', 'netmeds', '1mg', 'hospital'],
    'Education': ['udemy', 'coursera', 'byju', 'unacademy', 'college', 'school', 'fees'],
}

def detect_category(merchant, raw_sms=''):
    text = (merchant + ' ' + raw_sms).lower()
    for category, keywords in CATEGORY_RULES.items():
        if any(keyword in text for keyword in keywords):
            return category
    return ''