import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. Define project paths
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATASET_DIR = PROJECT_DIR / "dataset" / "raw"
PROCESSED_DIR = PROJECT_DIR / "dataset" / "processed"
DOCUMENTATION_DIR = PROJECT_DIR / "documentation"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
DOCUMENTATION_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# 2. Find all CSV files
# --------------------------------------------------

csv_files = sorted(DATASET_DIR.glob("*.csv"))

if not csv_files:
    print("ERROR: No CSV files found in dataset/raw/")
    raise SystemExit(1)

print("=" * 70)
print("       E-COMMERCE DATASET EXPLORATION")
print("=" * 70)

print(f"\nTotal CSV files found: {len(csv_files)}")

report_lines = []

summary_data = []

# --------------------------------------------------
# 3. Inspect each CSV file
# --------------------------------------------------

for file_path in csv_files:

    print("\n" + "=" * 70)
    print(f"FILE: {file_path.name}")
    print("=" * 70)

    report_lines.append("\n" + "=" * 70)
    report_lines.append(f"FILE: {file_path.name}")
    report_lines.append("=" * 70)

    total_rows = 0
    total_missing = 0
    chunk_duplicate_count = 0

    missing_counts = {}
    column_types = {}

    sample_records = None
    total_memory = 0

    # Read data in chunks to reduce memory consumption
    try:

        for chunk in pd.read_csv(
            file_path,
            chunksize=100_000,
            encoding="utf-8",
            encoding_errors="replace"
        ):

            total_rows += len(chunk)

            if sample_records is None:
                sample_records = chunk.head(5)

                column_types = {
                    col: str(dtype)
                    for col, dtype in chunk.dtypes.items()
                }

            # Count missing values
            missing = chunk.isnull().sum()

            for column, count in missing.items():
                missing_counts[column] = (
                    missing_counts.get(column, 0) + int(count)
                )

            total_missing += int(missing.sum())

            # Count duplicate rows within each chunk
            chunk_duplicate_count += int(chunk.duplicated().sum())

            total_memory += chunk.memory_usage(
                index=True,
                deep=True
            ).sum()

        if sample_records is None:
            print("Empty CSV file.")
            continue

        # --------------------------------------------------
        # 4. Display results
        # --------------------------------------------------

        total_columns = len(column_types)

        print(f"\nTotal Rows       : {total_rows:,}")
        print(f"Total Columns    : {total_columns}")
        print(f"Missing Values   : {total_missing:,}")
        print(f"Duplicates       : {chunk_duplicate_count:,}")
        print(f"Approx. Memory   : {total_memory / (1024 ** 2):.2f} MB")

        print("\nCOLUMN INFORMATION")

        for column, dtype in column_types.items():

            missing = missing_counts.get(column, 0)

            print(
                f"{column:<40} "
                f"{dtype:<15} "
                f"Missing: {missing:,}"
            )

        print("\nSAMPLE RECORDS")

        print(sample_records.to_string(index=False))

        # --------------------------------------------------
        # 5. Save report information
        # --------------------------------------------------

        report_lines.append(f"Rows: {total_rows:,}")
        report_lines.append(f"Columns: {total_columns}")
        report_lines.append(f"Missing Values: {total_missing:,}")
        report_lines.append(
            f"Duplicates within chunks: {chunk_duplicate_count:,}"
        )
        report_lines.append(
            f"Approx. Memory: {total_memory / (1024 ** 2):.2f} MB"
        )

        report_lines.append("\nColumn Information:")

        for column, dtype in column_types.items():

            missing = missing_counts.get(column, 0)

            report_lines.append(
                f"{column} | {dtype} | Missing: {missing:,}"
            )

        report_lines.append("\nSample Records:")
        report_lines.append(sample_records.to_string(index=False))

        summary_data.append({
            "file_name": file_path.name,
            "total_rows": total_rows,
            "total_columns": total_columns,
            "missing_values": total_missing,
            "duplicate_rows_within_chunks": chunk_duplicate_count,
            "approx_memory_mb": round(
                total_memory / (1024 ** 2), 2
            )
        })

    except Exception as error:

        print(f"ERROR processing {file_path.name}: {error}")

        report_lines.append(
            f"ERROR processing file: {error}"
        )

# --------------------------------------------------
# 6. Save exploration reports
# --------------------------------------------------

summary_df = pd.DataFrame(summary_data)

summary_path = PROCESSED_DIR / "exploration_summary.csv"

summary_df.to_csv(summary_path, index=False)

report_path = (
    DOCUMENTATION_DIR / "dataset_exploration_report.txt"
)

with open(report_path, "w", encoding="utf-8") as report_file:

    report_file.write(
        "E-COMMERCE DATASET EXPLORATION REPORT\n"
    )

    report_file.write("\n".join(report_lines))

# --------------------------------------------------
# 7. Final summary
# --------------------------------------------------

print("\n" + "=" * 70)
print("                 FINAL SUMMARY")
print("=" * 70)

print(summary_df.to_string(index=False))

print("\nReports generated successfully!")

print(f"\nSummary CSV: {summary_path}")
print(f"Text Report: {report_path}")
