import random
import csv
import matplotlib.pyplot as plt

STEM_SCHOOLS = ["CCDS", "CCEB", "CoE", "EEE", "MAE", "SPMS", "SBS", "MSE", "CEE"]

def read_file(filename):
    students = []
    with open(filename, 'r', newline='') as file:
        reader = csv.DictReader(file, fieldnames=['tutorial', 'id', 'name', 'school', 'gender', 'cgpa'])
        next(reader)
        
        for row in reader:
            if not any(row.values()):
                continue
            try:
                row['cgpa'] = float(row['cgpa'])
                row['team'] = 0
                students.append(row)
            except ValueError:
                print(f"Warning: Invalid CGPA for ID {row['id']}")
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
    if len(team) >= team_size:
        return False
    temp_team = team + [student]
    male, female = count_gender(temp_team)
    stem, nonstem = count_stem(temp_team)
    return (male <= ratio['male_max'] and female <= ratio['female_max'] and
            stem <= ratio['stem_max'] and nonstem <= ratio['nonstem_max'])

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
    
    stem, nonstem, males, females = [], [], [], []
    for s in students:
        if s['school'] in STEM_SCHOOLS:
            stem.append(s)
        elif s['school']:
            nonstem.append(s)
        
        if s['gender'].upper() in ['M', 'MALE']:
            males.append(s)
        elif s['gender'].upper() in ['F', 'FEMALE']:
            females.append(s)
    
    stem = sort_by_cgpa(stem)
    nonstem = sort_by_cgpa(nonstem)
    males = sort_by_cgpa(males)
    females = sort_by_cgpa(females)
    
    stem_minority, stem_majority = (stem, nonstem) if len(stem) <= len(nonstem) else (nonstem, stem)
    gender_minority, gender_majority = (males, females) if len(males) <= len(females) else (females, males)
    
    random.shuffle(stem_majority)
    random.shuffle(gender_majority)
    
    for i in range(len(stem_minority)):
        student = stem_minority[i]
        if student['id'] not in placed_ids:
            teams[i % num_teams].append(student)
            placed_ids[student['id']] = True

    for i in range(len(gender_minority)):
        student = gender_minority[i]
        if student['id'] not in placed_ids:
            teams[i % num_teams].append(student)
            placed_ids[student['id']] = True
    
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
    
    for student in stem_majority:
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
        writer = csv.DictWriter(file, fieldnames=['tutorial', 'id', 'school', 'name', 'gender', 'cgpa', 'team'])
        writer.writeheader()
        for key in keys_list:
            writer.writerows(groups[key])
    print(f"Saved to {filename}")

def calculate_std(values):
    """Manually calculate standard deviation without numpy"""
    n = len(values)
    if n <= 1:
        return 0.0
    
    # Calculate mean
    total = 0.0
    for val in values:
        total += val
    mean = total / n
    
    # Calculate squared differences
    sq_diff_sum = 0.0
    for val in values:
        diff = val - mean
        sq_diff_sum += diff * diff
    
    variance = sq_diff_sum / (n - 1)  # Sample variance
    return variance ** 0.5

def count_unique_schools(team):
    """Count unique schools in a team"""
    schools = []
    for student in team:
        school = student['school']
        if school and school not in schools:
            schools.append(school)
    return len(schools)

def visualize_tutorial_group(tutGrp, tutGrpName):
    """Enhanced visualization with diversity metrics"""
    team_ids = [f"Team {i+1}" for i in range(len(tutGrp))]
    avg_cgpas = []
    male_counts = []
    female_counts = []
    
    # New metric lists
    cgpa_std = []
    unique_school_counts = []
    
    # School distribution data (existing)
    all_schools = []
    for team in tutGrp:
        for student in team:
            school = student["school"]
            if school and school not in all_schools:
                all_schools.append(school)
    
    # Manual sort
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
        avg_cgpas.append(cgpa_total / len(team))
        
        # Calculate new metrics
        cgpa_std.append(calculate_std(team_cgpas))
        unique_school_counts.append(count_unique_schools(team))

        # School counts
        team_school_counts = {}
        for school in all_schools:
            team_school_counts[school] = 0
        
        for student in team:
            school = student["school"]
            if school:
                team_school_counts[school] += 1
        
        for school in all_schools:
            school_counts[school].append(team_school_counts[school])
    
    # === 1️⃣ Gender Distribution (keep original) ===
    plt.figure(figsize=(10,5))
    plt.bar(team_ids, male_counts, label="Male", color='#3498db', edgecolor='white', linewidth=0.5)
    plt.bar(team_ids, female_counts, bottom=male_counts, label="Female", color='#e74c3c', edgecolor='white', linewidth=0.5)
    plt.title(f"Gender Distribution in {tutGrpName}", fontsize=14, fontweight='bold')
    plt.xlabel("Teams")
    plt.ylabel("Number of Students")
    plt.legend()
    plt.tight_layout()
    plt.show()
    
    # === 2️⃣ NEW: CGPA Diversity (Standard Deviation) ===
    plt.figure(figsize=(10,5))
    bars = plt.bar(team_ids, cgpa_std, color='#9b59b6', edgecolor='black', linewidth=1.2, alpha=0.8)
    plt.title(f"CGPA Diversity (Std Dev) in {tutGrpName}", fontsize=14, fontweight='bold')
    plt.xlabel("Teams")
    plt.ylabel("Standard Deviation of CGPA")
    plt.axhline(y=sum(cgpa_std)/len(cgpa_std), color='red', linestyle='--', 
                linewidth=2, label=f'Average Std Dev: {sum(cgpa_std)/len(cgpa_std):.2f}')
    plt.legend()
    plt.tight_layout()
    plt.show()
    
    # === 3️⃣ NEW: School Diversity Score ===
    plt.figure(figsize=(10,5))
    bars = plt.bar(team_ids, unique_school_counts, color='#2ecc71', edgecolor='black', linewidth=1.2)
    plt.title(f"Unique Schools per Team in {tutGrpName}", fontsize=14, fontweight='bold')
    plt.xlabel("Teams")
    plt.ylabel("Number of Unique Schools")
    plt.axhline(y=sum(unique_school_counts)/len(unique_school_counts), color='red', linestyle='--',
                linewidth=2, label=f'Average: {sum(unique_school_counts)/len(unique_school_counts):.1f}')
    plt.legend()
    plt.tight_layout()
    plt.show()
    
    # === 4️⃣ School Distribution (existing format) ===
    plt.figure(figsize=(12,6))
    bottom = [0] * len(tutGrp)
    
    base_colors = [
        '#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', 
        '#1abc9c', '#34495e', '#e67e22', '#95a5a6', '#f1c40f',
        '#27ae60', '#d35400', '#8e44ad', '#16a085', '#c0392b'
    ]
    
    for i, school in enumerate(all_schools):
        counts = school_counts[school]
        color = base_colors[i % len(base_colors)]
        plt.bar(team_ids, counts, bottom=bottom, 
                label=school, color=color, edgecolor='white', linewidth=0.5)
        for j in range(len(bottom)):
            bottom[j] += counts[j]
    
    plt.title(f"School Distribution in {tutGrpName}", fontsize=14, fontweight='bold')
    plt.xlabel("Teams")
    plt.ylabel("Number of Students")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    plt.tight_layout()
    plt.show()
    
    # === 5️⃣ Average CGPA per Team (existing) ===
    plt.figure(figsize=(10,5))
    bars = plt.bar(team_ids, avg_cgpas, color='#9b59b6', edgecolor='black', linewidth=1.2)
    plt.title(f"Average CGPA per Team in {tutGrpName}", fontsize=14, fontweight='bold')
    plt.xlabel("Teams")
    plt.ylabel("Average CGPA")
    plt.ylim(0, 5)
    
    total_sum = 0.0
    for avg in avg_cgpas:
        total_sum += avg
    overall_avg = total_sum / len(avg_cgpas) if avg_cgpas else 0
    
    plt.axhline(y=overall_avg, color='red', linestyle='--', 
                linewidth=2, label=f'Overall Avg: {overall_avg:.2f}')
    plt.legend()
    plt.tight_layout()
    plt.show()
def get_team_size():
    while True:
        try:
            team_size = int(input("Enter team size (4–10): "))
            if team_size < 4 or team_size > 10:
                print("Invalid team size. Please enter a number between 4 and 10.")
                continue
            return team_size
        except ValueError:
            print("Invalid input. Please enter a number.")
            
def main():
    print("Team Allocation (STEM/NON-STEM):")
    team_size = get_team_size()
    print(f"Team Size: {team_size}")
    
    all_students = read_file('records.csv')
    tutorials = group_by_tutorial(all_students)
    
    team_number = 1
    tutorial_teams = {}
    
    for tut_name, tut_students in tutorials.items():
        teams = form_teams(tut_students, team_size)
        tutorial_teams[tut_name] = teams
        
        for team in teams:
            for student in team:
                student['team'] = team_number
            team_number += 1
    
    write_csv(all_students, 'FCS1_Team2_Joshua.csv')
    print("DONE! Check the output CSV file.")
    
    # Generate visualizations for EACH tutorial group
    for tut_name, teams in tutorial_teams.items():
        print(f"\nGenerating comprehensive visualizations for {tut_name}...")
        visualize_tutorial_group(teams, tut_name)

if __name__ == "__main__":
    main()