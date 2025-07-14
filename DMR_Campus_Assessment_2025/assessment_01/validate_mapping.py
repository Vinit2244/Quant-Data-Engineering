"""
    This script validates the mapping of financial data columns and checks the integrity of OHLC (Open, High, Low, Close) data.
    It loads a mapping JSON file and a CSV data file, modifies the headers of the DataFrame based on the mapping,
    and performs various integrity tests on the OHLC data and the results of the tests are printed to the console.
"""


# ================================ IMPORTS ===============================
import json
import argparse
import pandas as pd


# =============================== CONSTANTS ===============================
MAPPING_FILE = 'mapping.json'
DATA_FILE    = 'sample_data_with_fabricated_columns.csv'
CIRCUIT_BREAKER_THRESHOLD = 0.2 # 20%


# ================================ CLASSES ================================
class OHLCDataValidator:
    # Validates OHLC data integrity based on specified rules.
    # Note: Here we are just testing the integrity of the OHLC data and not including the price column in the tests as we are not sure about what it represents exactly.
    def __init__(self, data: pd.DataFrame=None) -> None:
        self.data = data

    def test_low_close_high(self) -> float:
        """
            Checks: Low ≤ Close ≤ High
            Returns the percentage of rows that satisfy this condition.
        """
        constraint_check = (self.data['Low'] <= self.data['Close']) & (self.data['Close'] <= self.data['High'])
        return constraint_check.sum() / len(self.data)
    
    def test_low_open_high(self) -> float:
        """
            Checks: Low ≤ Open ≤ High
            Returns the percentage of rows that satisfy this condition.
        """
        constraint_check = (self.data['Low'] <= self.data['Open']) & (self.data['Open'] <= self.data['High'])
        return constraint_check.sum() / len(self.data)

    def test_integer_volume(self) -> float:
        """
            Checks if the 'Volume' column contains only non-negative integers.
            Returns the percentage of rows that satisfy this condition.
        """
        integer_volume_check = self.data['Volume'].apply(lambda x: isinstance(x, int) and x >= 0)
        return integer_volume_check.sum() / len(self.data)
    
    def test_volume_largest_magnitude(self) -> float:
        """
            Checks if the 'Volume' is the largest value in each row compared to other columns.
            Returns the percentage of rows where 'Volume' is the largest.
        """
        volume_is_largest = self.data.apply(
            lambda row: row['Volume'] == row[self.data.columns.tolist()].max(), axis=1
        )
        return volume_is_largest.sum() / len(self.data)
    
    def test_high_is_maximum(self) -> float:
        """
            Checks if High is the maximum among Open, High, Low, Close.
            Returns the percentage of rows where High is the maximum price.
        """
        price_columns = ['Open', 'High', 'Low', 'Close']
        high_is_max = self.data.apply(
            lambda row: row['High'] == row[price_columns].max(), axis=1
        )
        return high_is_max.sum() / len(self.data)
    
    def test_low_is_minimum(self) -> float:
        """
            Checks if Low is the minimum among Open, High, Low, Close.
            Returns the percentage of rows where Low is the minimum price.
        """
        price_columns = ['Open', 'High', 'Low', 'Close']
        low_is_min = self.data.apply(
            lambda row: row['Low'] == row[price_columns].min(), axis=1
        )
        return low_is_min.sum() / len(self.data)

    def test_sequential_consistency(self) -> float:
        """
            Checks for sequential consistency in closing prices.
            Ensures no extreme jumps between consecutive closing prices.
            Returns the percentage of valid sequential transitions.
        """
        if len(self.data) < 2:
            return 1.0
        
        # Calculate percentage change between consecutive closing prices
        price_changes = self.data['Close'].pct_change().abs()
        reasonable_changes = price_changes <= CIRCUIT_BREAKER_THRESHOLD
        return reasonable_changes[1:].sum() / (len(self.data) - 1)

    def run_all_tests_and_print_results(self) -> None:
        """
            Runs all integrity tests and prints the results to the console.
        """
        print("Running OHLC Data Integrity Tests...\n")

        tests = [
            ("Low ≤ Close ≤ High", self.test_low_close_high),
            ("Low ≤ Open ≤ High", self.test_low_open_high),
            ("Integer Volume", self.test_integer_volume),
            ("Volume Largest Magnitude", self.test_volume_largest_magnitude),
            ("High is Maximum", self.test_high_is_maximum),
            ("Low is Minimum", self.test_low_is_minimum),
            ("Sequential Consistency", self.test_sequential_consistency)
            ]
        
        for idx, (test_name, test_func) in enumerate(tests):
            result = test_func()
            print(f"Test {idx + 1} - {test_name}: {round(result * 100, 2)}% valid rows")
        
        # low_close_high_result = self.test_low_close_high()
        # print(f"Low ≤ Close ≤ High: {round(low_close_high_result * 100, 2)}% valid rows")
        
        # low_open_high_result = self.test_low_open_high()
        # print(f"Low ≤ Open ≤ High: {round(low_open_high_result * 100, 2)}% valid rows")
        
        # integer_volume_result = self.test_integer_volume()
        # print(f"Integer Volume: {round(integer_volume_result * 100, 2)}% valid rows")
        
        # volume_largest_magnitude_result = self.test_volume_largest_magnitude()
        # print(f"Volume Largest Magnitude: {round(volume_largest_magnitude_result * 100, 2)}% valid rows")

        # high_is_max_result = self.test_high_is_maximum()
        # print(f"High is Maximum: {round(high_is_max_result * 100, 2)}% valid rows")

        # low_is_min_result = self.test_low_is_minimum()
        # print(f"Low is Minimum: {round(low_is_min_result * 100, 2)}% valid rows")

        # sequential_consistency_result = self.test_sequential_consistency()
        # print(f"Sequential Consistency: {round(sequential_consistency_result * 100, 2)}% valid transitions")


# ============================ HELPER FUNCTIONS ============================
def load_json(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as f:
            mapping = json.load(f)
        return mapping
    except Exception as e:
        print(f"Error loading JSON file {file_path}: {e}")
        exit(1)

def load_data(data_file: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(data_file)
        return df
    except Exception as e:
        print(f"Error loading data file {data_file}: {e}")
        exit(1)

def modify_headers(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    col_mapping: dict = {}
    for col, info in mapping.items():
        modified_col: str = info['mapping']
        col_mapping[col] = modified_col
    
    # Rename columns
    modified_header_df: pd.DataFrame = df.rename(columns=col_mapping)
    return modified_header_df

def validate_data_integrity(df: pd.DataFrame) -> list:
    validation_results = []
    total_rows = len(df)
    
    # Check if required columns exist
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Price']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        validation_results.append({
            'check': 'Required Columns',
            'status': 'FAIL',
            'message': f"Missing required columns: {missing_columns}"
        })
        return validation_results
    
    # 1. Check: Low ≤ Close ≤ High
    low_close_high_check = (df['Low'] <= df['Close']) & (df['Close'] <= df['High'])
    valid_low_close_high = low_close_high_check.sum()
    invalid_low_close_high = total_rows - valid_low_close_high
    
    validation_results.append({
        'check': 'Low ≤ Close ≤ High',
        'status': 'PASS' if invalid_low_close_high == 0 else 'FAIL',
        'valid_rows': valid_low_close_high,
        'invalid_rows': invalid_low_close_high,
        'percentage_valid': (valid_low_close_high / total_rows) * 100
    })
    
    # 2. Check: Low ≤ Open ≤ High
    low_open_high_check = (df['Low'] <= df['Open']) & (df['Open'] <= df['High'])
    valid_low_open_high = low_open_high_check.sum()
    invalid_low_open_high = total_rows - valid_low_open_high
    
    validation_results.append({
        'check': 'Low ≤ Open ≤ High',
        'status': 'PASS' if invalid_low_open_high == 0 else 'FAIL',
        'valid_rows': valid_low_open_high,
        'invalid_rows': invalid_low_open_high,
        'percentage_valid': (valid_low_open_high / total_rows) * 100
    })
    
    # 3. Check: Volume should be positive
    positive_volume_check = df['Volume'] > 0
    valid_volume = positive_volume_check.sum()
    invalid_volume = total_rows - valid_volume
    
    validation_results.append({
        'check': 'Volume > 0',
        'status': 'PASS' if invalid_volume == 0 else 'FAIL',
        'valid_rows': valid_volume,
        'invalid_rows': invalid_volume,
        'percentage_valid': (valid_volume / total_rows) * 100
    })
    
    # 4. Check: Volume should be largest magnitude (assuming it should be much larger than price values)
    # Compare volume with price columns to ensure it's in a different scale
    price_columns = ['Open', 'High', 'Low', 'Close', 'Price']
    max_price_value = df[price_columns].max().max()
    min_volume_value = df['Volume'].min()
    
    volume_magnitude_check = min_volume_value > max_price_value * 0.1  # Volume should be at least 10% of max price
    
    validation_results.append({
        'check': 'Volume Magnitude Check',
        'status': 'PASS' if volume_magnitude_check else 'FAIL',
        'message': f"Min Volume: {min_volume_value:.2f}, Max Price: {max_price_value:.2f}",
        'volume_appears_reasonable': volume_magnitude_check
    })
    
    # 5. Check: No negative values in price columns
    price_negative_check = (df[price_columns] >= 0).all().all()
    
    validation_results.append({
        'check': 'Non-negative Price Values',
        'status': 'PASS' if price_negative_check else 'FAIL',
        'all_prices_non_negative': price_negative_check
    })
    
    # 6. Check: Price column relationship with OHLC (assuming Price could be Close or average)
    # Check if Price is within OHLC range
    price_in_range_check = (df['Low'] <= df['Price']) & (df['Price'] <= df['High'])
    valid_price_range = price_in_range_check.sum()
    invalid_price_range = total_rows - valid_price_range
    
    validation_results.append({
        'check': 'Low ≤ Price ≤ High',
        'status': 'PASS' if invalid_price_range == 0 else 'FAIL',
        'valid_rows': valid_price_range,
        'invalid_rows': invalid_price_range,
        'percentage_valid': (valid_price_range / total_rows) * 100
    })
    
    return validation_results

def main():
    # Parsing the arguments
    argparser = argparse.ArgumentParser(description="Validate mapping and data integrity")
    argparser.add_argument('--mapping_file', type=str, default=MAPPING_FILE, help='Path to the mapping JSON file')
    argparser.add_argument('--data_file', type=str, default=DATA_FILE, help='Path to the data CSV file')
    args = argparser.parse_args()
    mapping_file = args.mapping_file
    data_file = args.data_file

    # Load mapping and data
    mapping_info = load_json(mapping_file)
    df = load_data(data_file)
    
    print(f"Mapping:")
    for col, info in mapping_info.items():
        print(f"\t{col} -> {info['mapping']} (Confidence: {info['confidence']})")
    print()
    
    # Change the headers of the DataFrame based on mapping
    df_mapped = modify_headers(df, mapping_info)
    
    # Perform tests
    validator = OHLCDataValidator(data=df_mapped)
    validator.run_all_tests_and_print_results()


if __name__ == "__main__":
    main()
