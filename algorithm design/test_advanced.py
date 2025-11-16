import random
import csv
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output

STEM_SCHOOLS = ["CCDS", "CCEB", "CoE", "EEE", "MAE", "SPMS", "SBS", "MSE", "CEE"]

def read_file(filename):
    students = []
    with open(filename, 'r', newline='') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            if not any(row.values()):
                continue
            try:
                student = {
                    'tutorial': row['Tutorial Group'],
                    'id': int(row['Student ID']),
                    'school': row['School'],
                    'name': row['Name'],
                    'gender': row['Gender'],
                    'cgpa': float(row['CGPA']),
                    'team': 0
                }
                students.append(student)
            except (ValueError, KeyError) as e:
                print(f"Warning: Invalid data for row {row}: {e}")
                continue
    
    print(f"Loaded {len(students)} students")
    return students

def calculate_ratio(students, team_size):
    male, female = count_gender(students)
    stem, nonstem = count_stem(students)
    total = male + female
    
    if total == 0:
        default_max = max(1, (team_size + 1) // 2)
        return {'male_max': default_max, 'female_max': default_max,
                'stem_max': default_max, 'nonstem_max': default_max}
    
    tolerance = 0.15 + (team_size - 5) * 0.02
    male_max = int(team_size * min(male / total + tolerance, 1) + 0.5)
    female_max = int(team_size * min(female / total + tolerance, 1) + 0.5)
    stem_max = int(team_size * min(stem / total + tolerance, 1) + 0.5)
    nonstem_max = int(team_size * min(nonstem / total + tolerance, 1) + 0.5)
    
    return {'male_max': max(1, male_max), 'female_max': max(1, female_max),
            'stem_max': max(1, stem_max), 'nonstem_max': max(1, nonstem_max)}

def count_gender(team):
    male = 0
    female = 0

    for student in team:
        if student['gender'].upper() in ['M', 'MALE']:
            male += 1
        elif student['gender'].upper() in ['F', 'FEMALE']:
            female += 1
    return male, female

def count_stem(team):
    stem = 0
    nonstem = 0
    for student in team:
        if student['school'] in STEM_SCHOOLS:
            stem += 1
        elif student['school']:
            nonstem += 1
    return stem, nonstem

def check_balanced(team, student, team_size, ratio):
    # Enhanced balance checking with school concentration and CGPA variance prevention
    if len(team) >= team_size:
        return False

    temp_team = team + [student]

    # Check 1: Gender balance
    male, female = count_gender(temp_team)
    if male > ratio['male_max'] or female > ratio['female_max']:
        return False

    # Check 2: STEM/Non-STEM balance
    stem, nonstem = count_stem(temp_team)
    if stem > ratio['stem_max'] or nonstem > ratio['nonstem_max']:
        return False

    # Check 3: School concentration (NEW)
    # Prevent more than 2 students from same school
    school_counts = {}
    for s in temp_team:
        sch = s['school']
        if sch:
            if sch not in school_counts:
                school_counts[sch] = 0
            school_counts[sch] += 1

    # Reject if any school has 3+ students
    max_same_school = max(school_counts.values()) if school_counts else 0
    if max_same_school > 2:
        return False

    # Check 4: CGPA spread (NEW)
    # Prevent extreme CGPA variance
    if len(temp_team) > 1:
        cgpas = [s['cgpa'] for s in temp_team]
        mean = sum(cgpas) / len(cgpas)
        sq_diff = sum((c - mean) ** 2 for c in cgpas)
        std_dev = (sq_diff / (len(cgpas) - 1)) ** 0.5

        # Allow slightly higher std for smaller partial teams
        max_std = 0.40 if len(temp_team) < team_size else 0.35
        if std_dev > max_std:
            return False

    return True

def group_by_tutorial(students):
    tutorials = {}
    for student in students:
        tut = student['tutorial']
        if tut not in tutorials:
            tutorials[tut] = []
        tutorials[tut].append(student)
    print(f"Found {len(tutorials)} tutorial groups")
    return tutorials

def sort_by_cgpa(students):
    n = len(students)
    for i in range(n):
        max_idx = i
        for j in range(i + 1, n):
            if students[j]['cgpa'] > students[max_idx]['cgpa']:
                max_idx = j
        students[i], students[max_idx] = students[max_idx], students[i]
    return students
    

def form_teams(students, team_size):
    if len(students) == 0:
        return []
    
    ratio = calculate_ratio(students, team_size)
    total = len(students)
    num_teams = (total + team_size - 1) // team_size
    
    base_size = total // num_teams
    extra = total % num_teams
    team_sizes = [base_size + 1 if i < extra else base_size for i in range(num_teams)]
    
    teams = [[] for _ in range(num_teams)]
    placed_ids = {}
    
    # Only separate by gender
    males, females = [], []
    for s in students:
        if s['gender'].upper() in ['M', 'MALE']:
            males.append(s)
        elif s['gender'].upper() in ['F', 'FEMALE']:
            females.append(s)
    
    # Sort by CGPA
    males = sort_by_cgpa(males)
    females = sort_by_cgpa(females)
    
    # Determine minority and majority gender groups
    gender_minority, gender_majority = (males, females) if len(males) <= len(females) else (females, males)
    
    # Shuffle majority to add randomness
    random.shuffle(gender_majority)
    
    # Distribute minority gender first (round-robin)
    for i in range(len(gender_minority)):
        student = gender_minority[i]
        if student['id'] not in placed_ids:
            teams[i % num_teams].append(student)
            placed_ids[student['id']] = True
    
    # Distribute majority gender with balance checking
    current_team = 0
    for student in gender_majority:
        if student['id'] in placed_ids:
            continue
        
        placed = False
        for offset in range(num_teams):
            idx = (current_team + offset) % num_teams
            if len(teams[idx]) < team_sizes[idx] and \
               check_balanced(teams[idx], student, team_sizes[idx], ratio):
                teams[idx].append(student)
                placed_ids[student['id']] = True
                placed = True
                current_team = (idx + 1) % num_teams
                break
        
        if not placed:
            # If can't place with balance, find team with most space
            best_team = 0
            max_space = team_sizes[0] - len(teams[0])
            for t in range(1, num_teams):
                space = team_sizes[t] - len(teams[t])
                if space > max_space:
                    max_space = space
                    best_team = t
            teams[best_team].append(student)
            placed_ids[student['id']] = True
            current_team = (best_team + 1) % num_teams
    
    return teams

def write_csv(all_students, filename):
    groups = {}
    for student in all_students:
        key = (student['tutorial'], student['team'])
        if key not in groups:
            groups[key] = []
        groups[key].append(student)
    
    keys_list = list(groups.keys())
    n = len(keys_list)
    for i in range(n):
        for j in range(i + 1, n):
            if keys_list[i] > keys_list[j]:
                keys_list[i], keys_list[j] = keys_list[j], keys_list[i]
    
    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, 
                                fieldnames=['Tutorial Group', 'Student ID', 'School', 'Name', 'Gender', 'CGPA', 'Team'],
                                extrasaction='ignore')
        writer.writeheader()
        for key in keys_list:
            for student in groups[key]:
                row = {
                    'Tutorial Group': student['tutorial'],
                    'Student ID': student['id'],
                    'School': student['school'],
                    'Name': student['name'],
                    'Gender': student['gender'],
                    'CGPA': student['cgpa'],
                    'Team': student['team']
                }
                writer.writerow(row)
    print(f"Saved to {filename}")
    


def print_summary(tutorial_teams):
    """Simple team summary showing gender, schools, and CGPA stats"""
    print("\n" + "="*120)
    print(f"{'TEAM COMPOSITION SUMMARY':^120}")
    print("="*120)
    print(f"{'Tutorial':<10} {'Team':<6} {'Size':<5} {'Gender':<10} {'Schools':<40} {'Avg CGPA':<10} {'Std Dev':<10}")
    print("-"*120)

    # Manual sort of tutorial keys
    tut_keys = []
    for key in tutorial_teams:
        tut_keys.append(key)

    for i in range(len(tut_keys)):
        for j in range(i + 1, len(tut_keys)):
            if tut_keys[i] > tut_keys[j]:
                tut_keys[i], tut_keys[j] = tut_keys[j], tut_keys[i]

    # Track overall stats
    total_teams = 0
    total_students = 0
    total_cgpa_sum = 0.0

    for tut in tut_keys:
        for i in range(len(tutorial_teams[tut])):
            team = tutorial_teams[tut][i]
            total_teams += 1
            total_students += len(team)

            # Gender counts
            m, f = count_gender(team)
            gender_str = f"{m}M/{f}F"

            # School counts
            school_counts = {}
            for st in team:
                sch = st['school']
                if sch:
                    if sch not in school_counts:
                        school_counts[sch] = 0
                    school_counts[sch] += 1

            # Format schools string
            schools_list = []
            for sch in school_counts:
                schools_list.append(f"{sch}:{school_counts[sch]}")
            schools_str = ", ".join(schools_list)

            # CGPA calculations
            cgpa_list = []
            cgpa_sum = 0.0
            for st in team:
                cgpa_sum += st['cgpa']
                cgpa_list.append(st['cgpa'])

            mean_cgpa = cgpa_sum / len(team)
            total_cgpa_sum += cgpa_sum

            # Calculate std dev
            if len(team) > 1:
                sq_diff = 0.0
                for cgpa in cgpa_list:
                    diff = cgpa - mean_cgpa
                    sq_diff += diff * diff
                std_dev = (sq_diff / (len(team) - 1)) ** 0.5
            else:
                std_dev = 0.0

            # Print row
            print(f"{tut:<10} T{i+1:<5} {len(team):<5} {gender_str:<10} {schools_str:<40} {mean_cgpa:>8.2f}  {std_dev:>9.3f}")

    # Print overall summary
    print("="*120)
    print(f"{'OVERALL STATISTICS':^120}")
    print("="*120)

    avg_size = total_students / total_teams if total_teams > 0 else 0
    overall_avg_cgpa = total_cgpa_sum / total_students if total_students > 0 else 0

    print(f"Total Tutorials: {len(tut_keys)}")
    print(f"Total Teams: {total_teams}")
    print(f"Total Students: {total_students}")
    print(f"Average Team Size: {avg_size:.2f}")
    print(f"Overall Average CGPA: {overall_avg_cgpa:.3f}")
    print("="*120 + "\n")

def visualize_tutorial_group(tutGrp, tutGrpName):
    """Create visualizations: Gender, CGPA Diversity, School Diversity (Stacked), and Average CGPA"""
    team_ids = [f"Team {i+1}" for i in range(len(tutGrp))]
    avg_cgpas = []
    male_counts = []
    female_counts = []
    cgpa_std_list = []
    
    # Collect all unique schools
    all_schools = []
    for team in tutGrp:
        for student in team:
            school = student["school"]
            if school and school not in all_schools:
                all_schools.append(school)
    
    # Manual sort (selection sort)
    for i in range(len(all_schools)):
        min_idx = i
        for j in range(i + 1, len(all_schools)):
            if all_schools[j] < all_schools[min_idx]:
                min_idx = j
        all_schools[i], all_schools[min_idx] = all_schools[min_idx], all_schools[i]
        
    school_counts = {}
    for school in all_schools:
        school_counts[school] = []

    # Process each team
    for team in tutGrp:
        males = 0
        females = 0
        cgpa_total = 0.0
        team_cgpas = []
        
        for student in team:
            if student["gender"].upper() in ['M', 'MALE']:
                males += 1
            elif student["gender"].upper() in ['F', 'FEMALE']:
                females += 1
            
            cgpa = student["cgpa"]
            cgpa_total += cgpa
            team_cgpas.append(cgpa)
            
        male_counts.append(males)
        female_counts.append(females)
        
        # Calculate Average CGPA
        avg_cgpas.append(cgpa_total / len(team))

        # Manual std dev calculation
        if len(team_cgpas) > 1:
            mean = sum(team_cgpas) / len(team_cgpas)
            squared_diffs = 0.0
            for cgpa_val in team_cgpas:
                diff = cgpa_val - mean
                squared_diffs += diff * diff
            variance = squared_diffs / (len(team_cgpas) - 1)
            std_dev = variance ** 0.5
        else:
            std_dev = 0.0
        cgpa_std_list.append(std_dev)

        # School counts
        team_school_tally = {}
        for school in all_schools:
            team_school_tally[school] = 0
        
        for student in team:
            school = student["school"]
            if school:
                team_school_tally[school] += 1
        
        for school in all_schools:
            school_counts[school].append(team_school_tally[school])

    # --- VISUALIZATIONS ---

    # 1. Gender Distribution
    plt.figure(figsize=(10,5))
    plt.bar(team_ids, male_counts, label="Male", color='#3498db', edgecolor='white', linewidth=0.5)
    plt.bar(team_ids, female_counts, bottom=male_counts, label="Female", color='#e74c3c', edgecolor='white', linewidth=0.5)
    plt.title(f"Gender Distribution in {tutGrpName}", fontsize=14, fontweight='bold')
    plt.xlabel("Teams")
    plt.ylabel("Number of Students")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # ---

    # 2. CGPA Diversity (Std Dev)
    plt.figure(figsize=(10,5))
    plt.bar(team_ids, cgpa_std_list, color='#9b59b6', edgecolor='black', linewidth=1.2, alpha=0.8)
    plt.title(f"CGPA Diversity (Std Dev) in {tutGrpName}", fontsize=14, fontweight='bold')
    plt.xlabel("Teams")
    plt.ylabel("Standard Deviation")
    total_std = sum(cgpa_std_list)
    avg_std = total_std / len(cgpa_std_list) if cgpa_std_list else 0
    plt.axhline(y=avg_std, color='red', linestyle='--', linewidth=2, label=f'Average Std Dev: {avg_std:.2f}')
    plt.legend()
    plt.tight_layout()
    plt.show()

    # ---

    # 3. Individual School Distributions (REMOVED as requested, using stacked plot instead)
    # The original plot has been commented out and replaced by a single stacked bar chart (new section 5)
    
    # ---

    # 4. Average CGPA per Team
    plt.figure(figsize=(10,5))
    bars = plt.bar(team_ids, avg_cgpas, color='#9b59b6', edgecolor='black', linewidth=1.2)
    plt.title(f"Average CGPA per Team in {tutGrpName}", fontsize=14, fontweight='bold')
    plt.xlabel("Teams")
    plt.ylabel("Average CGPA")
    plt.ylim(0, 5)
    total_avg = sum(avg_cgpas)
    overall_avg = total_avg / len(avg_cgpas) if avg_cgpas else 0
    plt.axhline(y=overall_avg, color='red', linestyle='--', linewidth=2, label=f'Overall Avg: {overall_avg:.2f}')
    plt.legend()
    plt.tight_layout()
    plt.show()

    # ---

    # 5. School Diversity (Stacked Bar Chart - The plot you wanted)
    # Define colors
    colors = [ 
        "#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd", "#8c564b", 
        "#e377c2", "#7f7f7f", "#bcbd22", "#17becf", "#3498db",
        "#d62728", "#8dd3c7", "#fdb462", "#b3de69", "#fb8072"
    ]

    # Map each school to a color by index
    school_colors = {}
    for i, school in enumerate(all_schools):
        school_colors[school] = colors[i % len(colors)]

    plt.figure(figsize=(12, 6))

    # Stack raw counts instead of percentages
    bottom = [0] * len(team_ids)
    for school in all_schools:
        # Use actual student counts
        values = school_counts[school]
        plt.bar(team_ids, values, bottom=bottom, 
                color=school_colors[school], label=school)
        # Update bottom for stacking
        for j in range(len(bottom)):
            bottom[j] += values[j]

    plt.xlabel("Teams")
    plt.ylabel("Total Number of Students")
    plt.title(f"School Diversity (Team Size & Composition) - {tutGrpName}")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()

from IPython.display import display
import ipywidgets as widgets
team_size_widget = widgets.IntText(
    value=5,
    description='Team Size:',
    style={'description_width': 'initial'}
)

run_button = widgets.Button(
    description='Generate Teams',
    button_style='success',
    icon='users'
)

output = widgets.Output()

# --- Callback function ---
def run_allocation(b):
    with output:
        output.clear_output()
        team_size = team_size_widget.value
        print(f"Starting team allocation with team size {team_size}...\n")
        
        # Load students
        try:
            all_students = read_file('records.csv')
        except FileNotFoundError:
            print("Error: 'records.csv' not found.")
            return
        
        tutorials = group_by_tutorial(all_students)
        
        # Team formation
        team_number = 1
        tutorial_teams = {}
        
        for tut_name, tut_students in tutorials.items():
            teams = form_teams(tut_students, team_size)
            tutorial_teams[tut_name] = teams
            
            for team in teams:
                for student in team:
                    student['team'] = team_number
                team_number += 1
        
        # Summary + CSV
        print_summary(tutorial_teams)
        write_csv(all_students, 'FCS1_Team_Allocation.csv')
        print("\nDONE! Check CSV: 'FCS1_Team_Allocation.csv'\n")
        
        # Visualizations
        for tut_name, teams in tutorial_teams.items():
            print(f"Generating visualizations for {tut_name}...")
            visualize_tutorial_group(teams, tut_name)

# Link button to callback
run_button.on_click(run_allocation)

# Display widgets
display(widgets.VBox([
    widgets.HBox([team_size_widget, run_button]),
    output
]))

