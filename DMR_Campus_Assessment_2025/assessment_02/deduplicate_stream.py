import argparse
import pandas as pd
import sys

# CLI argument parsing
def parse_args():
    parser = argparse.ArgumentParser(description='Deduplicate and clean a CSV stream.')
    parser.add_argument('--input', '-i', type=str, default='final_output.csv', help='Input CSV file path')
    parser.add_argument('--output', '-o', type=str, default='deduplicated_output.csv', help='Output deduplicated CSV file path')
    parser.add_argument('--method', '-m', type=str, choices=['latest', 'average'], default='latest', help='Deduplication method: latest (by timestamp) or average (price)')
    return parser.parse_args()

def deduplicate(df, method):
    # we find duplicates by matching on Symbol, if consecutive event id have minimal difference in timestamp and in price, we keep the latest one

    # Define minimal difference thresholds
    MIN_TIMESTAMP_DIFF = pd.Timedelta(seconds=0.01)  # 1 second
    MIN_PRICE_DIFF = 0.50  # price units

    deduped_rows = []
    prev_row = None

    for _, row in df.iterrows():
        if prev_row is not None and row['symbol'] == prev_row['symbol']:
            try:
                row['timestamp'] = pd.to_datetime(row['timestamp'], format='%Y-%m-%dT%H:%M:%S.%fZ')
            except ValueError:
                row['timestamp'] = pd.to_datetime(row['timestamp'], format='%Y-%m-%dT%H:%M:%SZ')
            try:
                prev_row['timestamp'] = pd.to_datetime(prev_row['timestamp'], format='%Y-%m-%dT%H:%M:%S.%fZ')
            except ValueError:
                prev_row['timestamp'] = pd.to_datetime(prev_row['timestamp'], format='%Y-%m-%dT%H:%M:%SZ')
            timestamp_diff = abs(row['timestamp'] - prev_row['timestamp'])
            price_diff = abs(row['price'] - prev_row['price'])
            if timestamp_diff <= MIN_TIMESTAMP_DIFF and price_diff <= MIN_PRICE_DIFF:
                # Keep the latest (current) row, discard previous
                # deduped_rows[-1] = row
                pass
            else:
                deduped_rows.append(row)
        else:
            deduped_rows.append(row)
        prev_row = row

    return pd.DataFrame(deduped_rows)

def main():
    args = parse_args()
    try:
        df = pd.read_csv(args.input)
    except Exception as e:
        print(f'Error reading input CSV: {e}')
        sys.exit(1)
    
    # Remove corrupted rows (e.g., missing key or timestamp)
    df = df.dropna()
    deduped = deduplicate(df, args.method)
    deduped.to_csv(args.output, index=False)
    print(f'Deduplicated output written to {args.output}')

if __name__ == '__main__':
    main()
