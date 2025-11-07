import random
import csv

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
    male = female = 0
    for student in team:
        if student['gender'].upper() in ['M', 'MALE']:
            male += 1
        elif student['gender'].upper() in ['F', 'FEMALE']:
            female += 1
    return male, female

def count_stem(team):
    stem = nonstem = 0
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
    placed_ids = set()
    
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
    
    for i, student in enumerate(stem_minority):
        if student['id'] not in placed_ids:
            teams[i % num_teams].append(student)
            placed_ids.add(student['id'])
    
    for i, student in enumerate(gender_minority):
        if student['id'] not in placed_ids:
            teams[i % num_teams].append(student)
            placed_ids.add(student['id'])
    
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
                placed_ids.add(student['id'])
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
            placed_ids.add(student['id'])
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
                placed_ids.add(student['id'])
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
            placed_ids.add(student['id'])
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

def main():
    print("Team Allocation (STEM/NON-STEM):")
    team_size = int(input("Enter team size (4-10): "))  
    
    if team_size < 4 or team_size > 10:  
        print("Team size must be between 4 and 10")
        return
    
    print(f"Team Size: {team_size}")
    
    all_students = read_file('records.csv')
    tutorials = group_by_tutorial(all_students)
    
    team_number = 1
    for tut_students in tutorials.values():
        teams = form_teams(tut_students, team_size)
        for team in teams:
            for student in team:
                student['team'] = team_number
            team_number += 1
    
    write_csv(all_students, 'FCS1_Team2_Joshua.csv')
    print("DONE! Check the output CSV file.")

if __name__ == "__main__":
    main()