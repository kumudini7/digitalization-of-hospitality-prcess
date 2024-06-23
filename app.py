from flask import Flask, render_template, request, redirect, url_for, flash
import csv
import sys
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Function to parse CSV and return data as dictionaries
def parse_csv(file_path):
    data = []
    with open(file_path, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(dict(row))
    return data

# Function to load and parse both CSV files
def load_data():
    groups_data = parse_csv('data/groups.csv')
    hostels_data = parse_csv('data/hostels.csv')
    return groups_data, hostels_data
# Function to allocate rooms based on the specified criteria
def allocate_rooms(groups_data, hostels_data):
    allocation_results = []

    # Step 1: Sort groups by size (descending) to allocate larger groups first
    groups_data.sort(key=lambda x: int(x['Members']), reverse=True)

    # Step 2: Initialize dictionaries to track allocated capacities for each hostel
    boys_hostel_capacities = {hostel['Room Number']: int(hostel['Capacity']) for hostel in hostels_data if hostel['Gender'] == 'Boys'}
    girls_hostel_capacities = {hostel['Room Number']: int(hostel['Capacity']) for hostel in hostels_data if hostel['Gender'] == 'Girls'}

    # Step 3: Allocate rooms
    for group in groups_data:
        group_id = group['Group ID']
        group_size = int(group['Members'])
        group_gender = group['Gender']

        allocated = False

        # Determine which hostel capacities to use based on group gender
        if group_gender == 'Boys':
            hostel_capacities = boys_hostel_capacities
        elif group_gender == 'Girls':
            hostel_capacities = girls_hostel_capacities
        else:
            flash(f"Invalid gender '{group_gender}' for group ID {group_id}.", 'error')
            continue

        # Try to allocate the group to available rooms
        for room_number, capacity in hostel_capacities.items():
            if group_size <= capacity:
                # Allocate the group to this room
                allocation_results.append({
                    'Group ID': group_id,
                    'Hostel Name': next((hostel['Hostel Name'] for hostel in hostels_data if hostel['Room Number'] == room_number), ''),
                    'Room Number': room_number,
                    'Members Allocated': str(group_size)
                })
                # Update the allocated capacity for the room
                hostel_capacities[room_number] -= group_size
                allocated = True
                break
        
        if not allocated:
            flash(f"No suitable room found for group ID {group_id} with {group_size} members.", 'error')

    return allocation_results

# Route to process uploaded files and display allocation results
@app.route('/allocate_rooms', methods=['GET', 'POST'])
def allocate_rooms_route():
    if request.method == 'POST':
        groups_data, hostels_data = load_data()
        allocation_results = allocate_rooms(groups_data, hostels_data)
        return render_template('result.html', allocation_data=allocation_results)

    flash('Please upload both CSV files first.', 'error')
    return redirect(url_for('upload_csv'))

if __name__ == '__main__':
    app.run(host="127.0.0.9", port=8080, debug=True)
