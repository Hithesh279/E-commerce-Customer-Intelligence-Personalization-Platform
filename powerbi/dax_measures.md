# Power BI DAX Measures Dictionary

This document defines the production-ready DAX measures implemented in the E-commerce Customer Intelligence Power BI Data Model.

---

## 1. Sales & Revenue Measures

### Total Gross Revenue
```dax
Total Gross Revenue = 
SUM(FactSales[total_amount])
```
*Description:* Sum of all transaction amounts including returned items.

---

### Total Net Revenue
```dax
Total Net Revenue = 
CALCULATE(
    SUM(FactSales[total_amount]),
    FactSales[is_returned] = 0
)
```
*Description:* Realized revenue strictly excluding returned orders. Used as the primary top-line sales KPI.

---

### Total Orders
```dax
Total Orders = 
DISTINCTCOUNT(FactSales[transaction_id])
```
*Description:* Count of unique transaction receipts.

---

### Total Customers
```dax
Total Customers = 
DISTINCTCOUNT(DimCustomer[customer_id])
```
*Description:* Total registered customer count in the customer dimension.

---

### Active Purchasing Customers
```dax
Active Purchasing Customers = 
CALCULATE(
    DISTINCTCOUNT(FactSales[customer_id]),
    FactSales[is_returned] = 0
)
```
*Description:* Distinct customers who completed at least one non-returned purchase in the selected filter context.

---

### Average Order Value (AOV)
```dax
Average Order Value = 
DIVIDE([Total Net Revenue], [Total Orders], 0)
```
*Description:* Average revenue generated per completed order. Uses `DIVIDE` to avoid zero-division errors.

---

### Average Items Per Order
```dax
Average Items Per Order = 
DIVIDE(SUM(FactSales[quantity]), [Total Orders], 0)
```
*Description:* Average unit quantity purchased per transaction.

---

### Overall Return Rate %
```dax
Overall Return Rate % = 
VAR TotalTxns = COUNTROWS(FactSales)
VAR ReturnedTxns = CALCULATE(COUNTROWS(FactSales), FactSales[is_returned] = 1)
RETURN
DIVIDE(ReturnedTxns, TotalTxns, 0) * 100
```
*Description:* Percentage of total orders resulting in a product return.

---

### Repeat Customer Rate %
```dax
Repeat Customer Rate % = 
VAR CustomerOrderCounts = 
    ADDCOLUMNS(
        VALUES(FactSales[customer_id]),
        "@Orders", CALCULATE(DISTINCTCOUNT(FactSales[transaction_id]))
    )
VAR RepeatCount = COUNTROWS(FILTER(CustomerOrderCounts, [@Orders] > 1))
VAR TotalBuyers = COUNTROWS(CustomerOrderCounts)
RETURN
DIVIDE(RepeatCount, TotalBuyers, 0) * 100
```
*Description:* Percentage of purchasing customers who placed more than one order.

---

### Revenue MoM Growth %
```dax
Previous Month Revenue = 
CALCULATE(
    [Total Net Revenue],
    DATEADD(DimDate[full_date], -1, MONTH)
)

Revenue MoM Growth % = 
VAR CurrentRev = [Total Net Revenue]
VAR PrevRev = [Previous Month Revenue]
RETURN
DIVIDE(CurrentRev - PrevRev, PrevRev, 0) * 100
```
*Description:* Month-over-month percentage growth in net revenue.

---

## 2. Customer Sentiment & Review Measures

### Total Reviews
```dax
Total Reviews = 
COUNTROWS(FactReviews)
```
*Description:* Total customer reviews submitted.

---

### Average Rating
```dax
Average Rating = 
AVERAGE(FactReviews[rating])
```
*Description:* Mean 1-5 star rating across all reviews in filter context.

---

### Positive Sentiment %
```dax
Positive Sentiment % = 
VAR PosReviews = CALCULATE(COUNTROWS(FactReviews), FactReviews[sentiment] = "Positive")
RETURN
DIVIDE(PosReviews, [Total Reviews], 0) * 100
```
*Description:* Percentage of reviews classified with positive sentiment (rating >= 4 or positive polarity).

---

### Negative Sentiment %
```dax
Negative Sentiment % = 
VAR NegReviews = CALCULATE(COUNTROWS(FactReviews), FactReviews[sentiment] = "Negative")
RETURN
DIVIDE(NegReviews, [Total Reviews], 0) * 100
```
*Description:* Percentage of reviews expressing customer dissatisfaction (rating <= 2).

---

### Net Sentiment Score (NSS)
```dax
Net Sentiment Score = 
[Positive Sentiment %] - [Negative Sentiment %]
```
*Description:* Net satisfaction index ranging from -100 to +100.

---

## 3. Recommendation & Interaction Measures

### Total Browsing Interactions
```dax
Total Browsing Interactions = 
COUNTROWS(FactInteractions)
```
*Description:* Total user behavioral events recorded (view, click, wishlist, cart, purchase).

---

### Simulated Recommendation CTR %
```dax
Simulated Recommendation CTR % = 
VAR Views = CALCULATE(COUNTROWS(FactInteractions), FactInteractions[interaction_type] = "view")
VAR Clicks = CALCULATE(COUNTROWS(FactInteractions), FactInteractions[interaction_type] = "click")
RETURN
DIVIDE(Clicks, Views, 0) * 100
```
*Description:* Offline simulated click-through rate on recommended items.

---

### Simulated Recommendation Conversion Rate %
```dax
Simulated Recommendation Conversion % = 
VAR Clicks = CALCULATE(COUNTROWS(FactInteractions), FactInteractions[interaction_type] = "click")
VAR Purchases = CALCULATE(COUNTROWS(FactInteractions), FactInteractions[interaction_type] = "purchase")
RETURN
DIVIDE(Purchases, Clicks, 0) * 100
```
*Description:* Offline simulated conversion rate from recommendation click to completed purchase.
