# :robot: Update:

> CMS withdrawal robot

## 04.03.2023

- Added **decline function** particularly for transaction's action which is classified as "**Declined**".
- Added **reject comments configuration**.
- Added custom page configration.
- Added custom window size configration.
- Added **SLA violation** in the diagnose category.
- Added new report sheet: "**report**" for summary of the run.
- Fixed when enter transaction not able to find **Transaction Payment Status**.
- Fixed keyerror when diagnose does not contain certain keys.

---

## 05.03.2023

- Added transaction summary extraction.

---

## 06.03.2023

- Fixed a summary bug.
- Added summary rebuild and dataframe construction.

---

## 07.03.2023

- Fixed a comment visibility bug.

---

## 11.03.2023

- Added the **Blacklist** diagnose category.
- Added the **Restricted country** diagnose category.
- Added new IP checker when CMS transaction ip does not show the country name.
- Added processing transaction in **Processing** status(status 1).

---

## 12.03.2023

- Added multi-threading of two browser instances for processing two different status withdrawals.
- Added **Free Margin** diagnose category for status-1 processing.
- Added the handler for transaction page failed to load.

---

## 14.03.2023

- Fixed handler when transaction in status 1 without any comment.
- Added email reminder time when documents not provided (current reminder time: 12h).
- Merged two status reports into one report.

---

## 16.03.2023

- Fixed error detecting "Compliance PE request".

---

## 17.03.2023

- Fixed summary not able to fetch when PS name starting with number. (2C2P Thiland).

---

## 18.03.2023

- Added **send email** action.

## 21.04.2023
- Removed comments text, sender name text, checked by text from transfer list to avoid interference for comment diagnose.

## Plan

- Reject comments translation in Chinese, Arabic, Korean, Thailand.
- API bank details checker for kora pay
- API transaction checker for transaction diagnosed as "API error", "Curl error" 
- E-wallets processing flow.
- Cryptocurrency processing flow.
- Online banking processing flow(India, China, Nigeria...).
- UI