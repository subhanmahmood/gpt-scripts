import csv
import sys

status_col = 'labels.httpStatus'
count_col = 'Count of records'
filter_val = '2'

if len(sys.argv) < 2:
    print("Usage: python main.py <filename>")
    exit()

filename = sys.argv[1]

# read the csv file and filter rows based on status_col == filter_val
data = []
with open(filename, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if row[status_col].startswith(filter_val):
            data.append(float(row[count_col]))

# calculate the average and print it to the console
if data:
    avg = sum(data) / len(data)
    print("Average:", avg)
else:
    print("No data found for status", filter_val)