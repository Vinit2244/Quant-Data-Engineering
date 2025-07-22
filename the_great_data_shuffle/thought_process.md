# Thought Process

Note: For detailed approach and though process please refer to the comments and markdown explanation in the `analysis.ipynb` file.

## Approach

**First we started with getting accurate understanding** of all the terms related to finance and trading used in the problem. Then to begin with we printed the descriptive statistics of the given datasets. Two things were directly apparent to us. First that the columns `deltaX`, `gamma`, `omega`, `flux` and `pulse` had negative min values and secondly that the column **`neutronCount` was drastically different in terms of order of magnitude of value** as compared to others. This got us suspicious about data being corrupt and that `neutronCount` presents a vastly different property than the other columns - for whom most of the statistical measures printed were almost equal. So based on our understanding of the terms we doubted `neutronCount` to be the volume of trade - the number of shares traded in a given time period. Then we made an assumption that stocks cannot be traded in fraction so we checked the data to calculate the percentage of integer values in the column and we found all the values to be integer which strongly supported our assumption of `neutronCount` being the `Volume`.

**Next, I handled data quality issues:** We checked for negative values across rows using systematic validation logic. We found that approximately 80K rows in each price column contained negative values, likely due to a constant systematic error in the data source. We corrected this by adding the absolute minimum value in the dataframe plus a small epsilon to ensure all values were positive (> 0) to avoid errors with value being 0. Alongside handling the negative values we also checked for `Null` and `0` values and handled them as well by dropping the rows and adding $\epsilon$ respectively to solve the issue.

**Then, we analyzed price relationships:** We inspected the remaining columns (`deltaX`, `flux`, `pulse`, `gamma`, `omega`) using correlation analysis and row-wise statistics. These showed nearly perfect correlation (≈1.0) among themselves, confirming they all represent price-related metrics for the same underlying asset. The row wise statistics were motivated by the assumption that since in a single day the price of stock cannot change by a lot (it is prevented by the circuit breaker applied in most of the stock exchanges) - so we moved ahead with the assumption that this particular stock exchange also has that safety.

**To identify High and Low:** We calculated row averages and created deviation plots by subtracting this baseline from each column. This revealed that `gamma` consistently occupied the uppermost band while `omega` remained in the lowermost band across all data points. Validation showed that `gamma` was the maximum value in most rows, while `omega` was the minimum, confirming `gamma = High` and `omega = Low`.

**For the Price field:** Based on financial principles, we assumed `Price` represents the average price for the day, which should logically fall between Open and Close values. Among the remaining columns (`deltaX`, `flux`, `pulse`), the deviation analysis showed that `pulse` consistently stayed in the middle band, making it the most likely candidate for `Price`.

**Finally, distinguishing Open vs Close:** We leveraged the financial principle that closing prices of a trading day should be relatively close to opening prices of the next day (overnight gaps). We tested both cases and found that `flux = Open, deltaX = Close` produced smaller overnight gaps compared to the alternative (ever so slightly), indicating better alignment with real market behavior.

## Challenges (and how we overcame them)

**Challenge 1: Negative Values in Price Data**
The dataset contained negative values across all price columns, which is impossible in real financial markets. We overcame this by identifying it as a systematic data source error and applying a global adjustment by adding the absolute minimum value plus epsilon to all entries.

**Challenge 2: High Correlation Between Price Fields**
All price-related columns showed near-perfect correlation, making direct differentiation difficult. We solved this by using row-wise deviation analysis - subtracting the row average from each value to amplify the subtle differences between fields.

**Challenge 3: Distinguishing Open from Close**
Without timestamps, it was challenging to determine which field represented opening vs closing prices. We addressed this by analyzing overnight gaps between consecutive trading periods for both the cases `flux = Open, deltaX = Close` and vice versa, using the financial principle that consecutive days' closing and opening prices should be relatively close. The differences were very minute and were visible only when looked at monthly scales or larger. It was very difficult to identify the open and close columns based on the given data and no information about the duration of the interval in which data was set.

**Challenge 4: Validating the Sequential Nature of Data**
Since it was not explicitely mentioned that the data was in-order in rows and was not jumbled up we needed to confirm that rows represented consecutive trading days. We validated this by plotting price[t] vs price[t+1] correlations, which showed a perfect linear relationship (correlation ≈ 1.0), confirming the sequential assumption since there are minute price changes in the value of a stock over consecutive days.

### Confidence Analysis

#### Volume (neutronCount): 100% confidence

- All 500,000 values are integers, which perfectly aligns with the nature of trading volumes

#### High (gamma): 86.5% confidence

- In 86.5% of rows, gamma has the maximum value among all price fields
- Consistent uppermost positioning in deviation plots

#### Low (omega): 86.6% confidence

- In 86.6% of rows, omega has the minimum value among all price fields  
- Consistent lowermost positioning in deviation plots

#### Price (pulse): 60.0% confidence

- Based on deviation from expected average of (Open+Close+High+Low)/4
- Scaled by daily trading range to account for varying volatility
- Consistent middle-band positioning in comparative analysis

#### Open (flux) & Close (deltaX): 67.0% confidence each

- Derived from Parkinson volatility model comparison between open-close and high-low based estimates
- Validated through overnight gap analysis showing smaller deviations
- Combined confidence incorporates reliability of High and Low predictions

### Summary

Overall, we combined **statistical analysis, financial domain knowledge, and data validation techniques** to derive the mapping. The approach leveraged multiple validation methods including correlation analysis, row-wise statistics, deviation plots, overnight gap analysis, and volatility model comparisons. I also wrote **comprehensive data preprocessing logic** to handle systematic errors and ensure data quality. The final mapping achieved high confidence scores through cross-validation using established financial principles like the relationship between consecutive trading periods and intraday price movements.

### Final Mapping

- `neutronCount` -> `Volume` (100% confidence)
- `gamma` -> `High` (86.5% confidence)  
- `omega` -> `Low` (86.6% confidence)
- `pulse` -> `Price` (60.0% confidence)
- `flux` -> `Open` (67.0% confidence)
- `deltaX` -> `Close` (67.0% confidence)
