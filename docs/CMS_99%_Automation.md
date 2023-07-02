# FXTM Withdrawal Automation Improvement

#### Min Chen - Processing Officer - FXTM - Exinity

---

## Abstract
This paper introduces in detail how to maximize the automation of FXTM's withdrawal processing. The starting point is to find all the filters and constrains that cause transactions to come to Backoffice queue, screen these filters and constrains, remove useless filters and re-classify transactions. The direction of transaction automation is defined based on these categories.

## Table Of Contents

#### &nbsp; 1. Introduction

#### &nbsp; 2. Filters

#### &nbsp; 3. Classifications

#### &nbsp; 4. Status

#### &nbsp; 5. Methodology

#### &nbsp; 6. Results

#### &nbsp; 7. Actions

#### &nbsp; 8. Workflows

## 1. Introduction

## 2. Filters
 This chapter will explore the limitations of automatic withdrawal filters with a focus on their origin and usage, and evaluate the potential for their update, removal or closure.

### &nbsp; &nbsp; 2.1. Filter W/A/0
### &nbsp; &nbsp; 2.2. Filter W/A/0/2
### &nbsp; &nbsp; 2.3. Filter W/No act

## 3. Constrains
### &nbsp; &nbsp; 3.1. Daily withdrawal limit exceed
### &nbsp; &nbsp; 3.2. Transfer amount limit exceed
### &nbsp; &nbsp; 3.3. Initial withdrawal method is different to the initial deposit payment system
### &nbsp; &nbsp; 3.4.  Age documents
### &nbsp; &nbsp; 3.5.  BO Supervisor queue
### &nbsp; &nbsp; 3.6.  Sales queue
### &nbsp; &nbsp; 3.7.  Compliance queue
### &nbsp; &nbsp; 3.8.  Payment system not approved
### &nbsp; &nbsp; 3.9.  Detected attempt of withdrawal more funds than was deposited
### &nbsp; &nbsp; 3.10. Account has credit
### &nbsp; &nbsp; 3.11. Wallet is in use by others
### &nbsp; &nbsp; 3.12. No cryptocurrency deposit history  

## 4. Responses, errors and exceptions:
### &nbsp; &nbsp; 4.1 Curl error response
### &nbsp; &nbsp; 4.2 API error response
### &nbsp; &nbsp; 4.3 Callback is "Failed"
### &nbsp; &nbsp; 4.4 Payee and payer accounts has different types
### &nbsp; &nbsp; 4.5 Other errors
### &nbsp; &nbsp; 4.6 handleErrorRobot
### &nbsp; &nbsp; 4.7 Exception: Failed to load Account

## 4. Classifications

#### &nbsp; 3.1. No error found

#### &nbsp; &nbsp; &nbsp; &nbsp; 3.11 Online Banking

#### &nbsp; &nbsp; &nbsp; &nbsp; 3.12 E-Wallet

#### &nbsp; &nbsp; &nbsp; &nbsp; 3.13 Cryptocurrency

#### &nbsp; &nbsp; &nbsp; &nbsp; 3.14 Praxis Card

#### &nbsp; 3.2 Manual processed

#### &nbsp; 3.3 Payment system not approved, registered within 24 hours

#### &nbsp; 3.4 Payment system not approved, registered over 24 hours

#### &nbsp; 3.5 Payment system not approved, no documents requested emails sent

#### &nbsp; 3.6 Age documents requested

#### &nbsp; 3.7 Rejected from provider portal

#### &nbsp; 3.8 Other error

#### &nbsp; 3.9 API error

#### &nbsp; 3.10 CURL error

#### &nbsp; 3.11 Callback failed

#### &nbsp; 3.12 Blacklist

#### &nbsp; 3.13 Restricted country

#### &nbsp; 3.14 Insufficient funds

#### &nbsp; 3.15 B2binpay Summary Check

#### &nbsp; 3.16 Initial method is different than first withdrawal

## 4. Filters


## 5. Methodology

## 6. Results

## 7. References
