import sys

import openpyxl
import pandas as pd

from backend import mark_flag
from make_log import log_exceptions
from movemaster import move_master_to_master_insurer
try:
    _, file_path, mid = sys.argv

    df = pd.read_html(file_path)[0]
    data = []

    for index, row in df.iterrows():
        temp = [cell for cell in row]
        data.append(temp)

    wbName = 'master.xlsx'
    wb = openpyxl.Workbook()
    wb.create_sheet('Sheet1')
    wb.create_sheet('count')
    wb.create_sheet('count_star')
    wb.create_sheet('error_sheet')
    main_s1 = wb.worksheets[0]
    main_s2 = wb.worksheets[1]

    sh1 = ['Sno', 'HospitalID', 'InsurerID', 'ALNO', 'ClaimNo', 'MemberID', 'PolicyNo', 'PatientName', 'InsuranceCompany',
           'AccountNo', 'BeneficiaryBank Name', 'Diagnosis', 'UTRNo', 'BilledAmount', 'SettledAmount', 'TDS', 'NetPayable',
           'DiscountAmt', 'COPay', 'PolicyHolder', 'IPNo', 'PrimaryBeneficiary', 'EmployeeID', 'InsurerClaimNo',
           'InsurerMemberID', 'TaxDeductedatSource', 'Netamount payment', 'PaidbythePatient', 'ProrataBasis',
           'PolicyExcessDeductible', 'BeneficiaryName', 'BalanceSumInsuredBeforeClaim', 'NetPayable',
           'BalanceSumInsuredAfterClaim', 'TDS%', 'Remarks', 'PaymentTo', 'DateofAdmission', 'DateofDischarge',
           'AmtPaidtoHospital', 'BillAmt', 'PayableAmt', 'SettledAmt', 'SumInsured', 'ALAmount	Approved', 'Amount',
           'HospitalAmount', 'AmountUtilised', 'FinalAmountSettled', 'DateOfPayment', 'ServiceTax', 'TotalwithServiceTax',
           'InsuredPerson', 'CorporateName', 'DeductibleAmt', 'Transactiondate', 'LOCALAmount', 'ChequeDate',
           'UHCApprovedHospitalAmt', 'InsurerApprovedHospitalAmt', 'InsurerApprovedEmployeeAmt', 'PayableAmount',
           'NEFTTransactionNumber', 'TransactionDate', 'CorporateName', 'Claimed', 'PreHospitalisationPayableAmount',
           'PostHospitalisationPayableAmount', 'AddonBenefit', 'Claimed', 'Paid', 'BillAmount', 'PayableAmount(INR)',
           'BillDate', 'BillNo', 'AmountSettled', 'ApprovedAmount', 'less', 'Excess of Defined / Ailment Limit',
           'policy deduction', 'Limit exceed deduction', 'non payable deduction', 'Bill deduction', 'Other deduction']
    sh2 = ['Sr. No.', 'HospitalID', 'InsurerID', 'Claim ID', 'Details', 'Bill amount', 'Payable Amount', 'Deducted Amt',
           'Reason for Deduction', 'Discount']

    sh1_fields = [('ALNO', 'Remarks'), ('ClaimNo', 'Settlement No'), ('PolicyNo', 'Policy No'),
                  ('PatientName', 'Claimant Name'), ('InsuranceCompany', 'Tpa Branch Name'),
                  ('AccountNo', 'Payee Bank Acc No'), ('UTRNo', 'Utr No'), ('SettledAmount', 'GrossPaidAmount'),
                  ('TDS', 'TDS'), ('NetPayable', 'Net Paid Amount'), ('PolicyHolder', 'Insured Name'),
                  ('InsurerClaimNo', 'Sub Claim No'), ('NEFTTransactionNumber', 'Utr No'),
                  ('TransactionDate', 'Payment Date')]

    temp = {}
    for j, i in enumerate(data[0]):
        for field in sh1_fields:
            if field[1] in i:
                t_list = []
                for k in range(1, len(data)):
                    t_list.append(data[k][j])
                temp[field[0]] = t_list

    for i in range(len(temp['ALNO'])):
        tmp = temp['ALNO'][i]
        temp['ALNO'][i] = tmp.replace('-', '')

    tmp_l = [(mid, 'Sno'), ('inamdar', 'HospitalID'), ('NIC', 'InsurerID')]
    for field in tmp_l:
        temp[field[1]] = []
        for i in data[1:]:
            temp[field[1]].append(field[0])

    for i in range(0, len(sh1)):
        # main_s1.cell(row=1, column=i+1).value=i+1
        main_s1.cell(row=1, column=i + 1).value = sh1[i]
        if sh1[i] in temp:
            for j, k in enumerate(temp[sh1[i]]):
                main_s1.cell(row=j + 2, column=i + 1).value = k

    for i in range(0, len(sh2)):
        main_s2.cell(row=1, column=i + 1).value = sh2[i]


    wb.save(wbName)
    move_master_to_master_insurer(sys.argv[2], pdfpath=file_path)
    mark_flag('X', sys.argv[2])
    print(f'processed')
except:
    log_exceptions()
    pass