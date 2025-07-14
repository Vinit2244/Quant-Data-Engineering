## Thought Process
--- 

### A. Reconstruct Event Timelines

**First**, we began by loading the `worker_logs.csv` file and converting the `start_time` and `end_time` columns into a standard datetime format. This allowed us to perform time-based analysis accurately.

**Secondly**, we visualized each worker's task activity over time using a Gantt chart. This helped us clearly see how tasks were distributed across workers and whether any of them were idle or overloaded.

We then analyzed the data to identify any irregularities. Specifically, we looked for overlapping task windows assigned to the same worker, which could indicate scheduling issues. We also checked for retried jobs by counting how often the same `event_id` appeared more than once. Additionally, we filtered out tasks that did not have a "success" status to detect failed events.

**Finally**, we enhanced our Gantt chart by highlighting failed tasks in red. This gave us a quick visual overview of which workers encountered problems and when those failures occurred. Overall, this process helped us reconstruct the event timelines, spot inefficiencies, and better understand how the system behaved during task execution.


---


### B. Detect and Quantify Dulicates

**First**, we merge multiple logs: the raw tick events, worker processing logs, and the final output results. During this merge, we try to ensure that proper timestamp formatting—handling both millisecond (`%fZ`) and second-only (`%SZ`) variations are handled to prevent data loss or misalignment.

**Once merged**, the code identifies duplicate rows that share the same `event_id` and `symbol_final`. These represent potential inconsistencies where the same event was processed more than once. For each of these duplicates, the script calculates how many times the event appeared (`occurrences`) and computes the **price shift**, i.e., the difference between two final prices if multiple versions exist. This is useful for diagnosing issues such as non-deterministic pricing or race conditions. 

> We can also compute the time_difference between the two occurances (`timestamp_diff`) which has been commented out to maintain the formatting requirements as was given in the sample_duplication_analysis file.

**Finally**, the results were cleaned to match a consistent reporting format and saved to a CSV file named `duplication_analysis.csv` for further use.

In essence, this pipeline ensures high-integrity validation of event processing by tracing duplication patterns and quantifying their impact on pricing—crucial in systems like high-frequency trading where correctness and consistency are paramount.

Thus, this process helps check if the same trading event was handled more than once, and whether that led to any difference in the final price. By merging logs from different parts of the system and fixing any timestamp issues, it finds duplicate entries, measures how their prices differ, and saves the results for review. This is especially important in fast-paced trading systems, where even small mistakes or repeated processing can lead to serious problems.


---

### C.  Write a De-duplication Script

**First**, the script reads the `final_output.csv` file and drops any corrupted or incomplete rows (like those missing timestamps or symbols).

**Next**, it goes through each row in the data and checks if the current row has the same symbol as the previous one. If the price difference is small and the timestamps are almost the same (within 1 second), it assumes it’s a duplicate. In that case, it keeps only the most recent entry.

**Then**, it collects all the clean, non-duplicate records and saves them into a new file called `deduplicated_output.csv`.

**Finally**, this cleaned file is ready for further use—giving you a reliable, de-duplicated version of the data stream that avoids confusion or errors from repeated records.

#### Logical Rules used:
1. **Same Symbol Rule**
    Two events are only compared for duplication if they belong to the **same stock symbol** (`row['symbol'] == prev_row['symbol']`).

2. **Minimal Timestamp Difference Rule**
    The two events are considered potentially duplicated only if the **time difference** between their timestamps is **less than or equal to 1 second**:
     `abs(current_time - previous_time) ≤ 1 second`

3. **Minimal Price Difference Rule**
    To prevent false positives due to market movement, the **absolute difference in price** must also be **less than or equal to 0.50** units:
     `abs(current_price - previous_price) ≤ 0.50`

4. **Latest Entry Retention Rule**
    Among the near-duplicate records that pass the above two rules, the script **keeps only the latest row** (i.e., the one with the more recent timestamp).


---
