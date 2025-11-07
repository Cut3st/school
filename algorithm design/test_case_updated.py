"""
Team Allocation Validator - ULTRA STRICT EDITION
Checks EVERYTHING with extreme prejudice. No mercy.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import math

class TeamValidatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Team Allocation Validator")
        self.root.geometry("1200x800")
        
        self.all_teams = {}
        self.students_data = []
        self.tutorial_demographics = {}
        self.all_issues = []  # Track ALL issues found
        
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(top_frame, text="CSV File:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.file_path = tk.StringVar()
        tk.Entry(top_frame, textvariable=self.file_path, width=60).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(top_frame, text="Browse...", command=self.browse_file, bg="#4CAF50", fg="white").grid(row=0, column=2, padx=5, pady=5)
        
        tk.Label(top_frame, text="Team Size:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.team_size = tk.StringVar(value="5")
        tk.Entry(top_frame, textvariable=self.team_size, width=10).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Strictness selector
        tk.Label(top_frame, text="Strictness:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.strictness = tk.StringVar(value="ULTRA")
        strictness_combo = ttk.Combobox(top_frame, textvariable=self.strictness, 
                                        values=["NORMAL", "STRICT", "ULTRA", "NIGHTMARE"], 
                                        state="readonly", width=10)
        strictness_combo.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        tk.Button(top_frame, text="▶ Run Validation", command=self.run_validation, 
                 bg="#2196F3", fg="white", font=("Arial", 11, "bold"), 
                 padx=20, pady=5).grid(row=1, column=2, padx=5, pady=5)
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.summary_tab = scrolledtext.ScrolledText(notebook, wrap=tk.WORD, font=("Courier", 9))
        notebook.add(self.summary_tab, text="📊 Summary")
        
        self.gender_tab = scrolledtext.ScrolledText(notebook, wrap=tk.WORD, font=("Courier", 9))
        notebook.add(self.gender_tab, text="👥 Gender")
        
        self.school_tab = scrolledtext.ScrolledText(notebook, wrap=tk.WORD, font=("Courier", 9))
        notebook.add(self.school_tab, text="🏫 School")
        
        self.cgpa_tab = scrolledtext.ScrolledText(notebook, wrap=tk.WORD, font=("Courier", 9))
        notebook.add(self.cgpa_tab, text="📈 CGPA")
        
        # NEW: Critical Issues Tab
        self.critical_tab = scrolledtext.ScrolledText(notebook, wrap=tk.WORD, font=("Courier", 9))
        notebook.add(self.critical_tab, text="🚨 Critical Issues")
        
        # NEW: Data Quality Tab
        self.quality_tab = scrolledtext.ScrolledText(notebook, wrap=tk.WORD, font=("Courier", 9))
        notebook.add(self.quality_tab, text="🔬 Data Quality")
        
        inspector_frame = tk.Frame(notebook)
        notebook.add(inspector_frame, text="🔍 Team Inspector")
        
        search_frame = tk.Frame(inspector_frame, pady=10)
        search_frame.pack(fill=tk.X)
        
        tk.Label(search_frame, text="Search Team:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Label(search_frame, text="Tutorial:").pack(side=tk.LEFT, padx=5)
        self.search_tutorial = tk.Entry(search_frame, width=10)
        self.search_tutorial.pack(side=tk.LEFT, padx=5)
        
        tk.Label(search_frame, text="Team #:").pack(side=tk.LEFT, padx=5)
        self.search_team = tk.Entry(search_frame, width=10)
        self.search_team.pack(side=tk.LEFT, padx=5)
        
        tk.Button(search_frame, text="🔍 Find Team", command=self.find_team,
                 bg="#FF9800", fg="white").pack(side=tk.LEFT, padx=10)
        
        tk.Button(search_frame, text="📋 List All Teams", command=self.list_all_teams,
                 bg="#9C27B0", fg="white").pack(side=tk.LEFT, padx=5)
        
        self.inspector_display = scrolledtext.ScrolledText(inspector_frame, wrap=tk.WORD, font=("Courier", 9))
        self.inspector_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.status_bar = tk.Label(main_frame, text="Ready. Select a CSV file to begin.", 
                                   relief=tk.SUNKEN, anchor=tk.W, bg="#f0f0f0")
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Team Allocation CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
            self.status_bar.config(text=f"Selected: {filename}")
    
    def clear_all_tabs(self):
        self.summary_tab.delete('1.0', tk.END)
        self.gender_tab.delete('1.0', tk.END)
        self.school_tab.delete('1.0', tk.END)
        self.cgpa_tab.delete('1.0', tk.END)
        self.critical_tab.delete('1.0', tk.END)
        self.quality_tab.delete('1.0', tk.END)
        self.inspector_display.delete('1.0', tk.END)
        self.all_issues = []
    
    def add_issue(self, severity, category, message):
        """Track all issues found during validation."""
        self.all_issues.append({
            'severity': severity,
            'category': category,
            'message': message
        })
    
    def detect_column_mapping(self, header):
        header_lower = [h.strip().lower() for h in header]
        mapping = {}
        
        for i, col in enumerate(header_lower):
            if 'tutorial' in col:
                mapping['tutorial'] = i
                break
        
        for i, col in enumerate(header_lower):
            if 'student' in col and 'id' in col:
                mapping['id'] = i
                break
            elif col in ['id', 'student_id', 'studentid']:
                mapping['id'] = i
                break
        
        for i, col in enumerate(header_lower):
            if col == 'name' or col == 'student name':
                mapping['name'] = i
                break
        
        for i, col in enumerate(header_lower):
            if col == 'school' or col == 'school affiliation':
                mapping['school'] = i
                break
        
        for i, col in enumerate(header_lower):
            if col == 'gender' or col == 'sex':
                mapping['gender'] = i
                break
        
        for i, col in enumerate(header_lower):
            if col == 'cgpa' or col == 'gpa' or 'cgpa' in col:
                mapping['cgpa'] = i
                break
        
        for i, col in enumerate(header_lower):
            if 'team' in col:
                mapping['team'] = i
        
        if 'team' not in mapping:
            mapping['team'] = len(header) - 1
        
        return mapping
    
    def calculate_tutorial_thresholds(self, tutorial_students, team_size):
        male_count = sum(1 for s in tutorial_students if s['gender'].upper() in ['M', 'MALE'])
        female_count = len(tutorial_students) - male_count
        total = len(tutorial_students)
        
        if total == 0:
            return {'male_max': 3, 'female_max': 3, 'male_ratio': 0.5, 'female_ratio': 0.5}
        
        male_ratio = male_count / total
        female_ratio = female_count / total
        
        # Adjust tolerance based on strictness
        strictness = self.strictness.get()
        if strictness == "NIGHTMARE":
            tolerance = 0.10  # Only 10% deviation
        elif strictness == "ULTRA":
            tolerance = 0.15  # 15% deviation
        elif strictness == "STRICT":
            tolerance = 0.20  # 20% deviation
        else:
            tolerance = 0.25  # 25% deviation
        
        male_max_ratio = min(male_ratio + tolerance, 1.0)
        female_max_ratio = min(female_ratio + tolerance, 1.0)
        
        male_max = int(team_size * male_max_ratio + 0.5)
        female_max = int(team_size * female_max_ratio + 0.5)
        
        min_minority = 1 if min(male_count, female_count) >= 1 else 0
        
        return {
            'male_max': max(male_max, min_minority),
            'female_max': max(female_max, min_minority),
            'male_ratio': male_ratio,
            'female_ratio': female_ratio,
            'tolerance': tolerance
        }
    
    def check_stem_sorting(self):
        """Check if the CSV data is sorted by STEM school status."""
        STEM_SCHOOLS = [
            "CCDS",
            "CCEB",
            "CoE",
            "EEE",
            "MAE",
            "SPMS",
            "SBS",
            "MSE",
            "CEE"
        ]

        if not self.students_data:
            return True, "No data to check"

        # Check if data is sorted by STEM status (STEM schools first, then non-STEM)
        is_sorted = True
        first_non_stem_index = None
        sorting_violations = []

        for i, student in enumerate(self.students_data):
            school = student['school'].strip()
            is_stem = school in STEM_SCHOOLS

            # Track when we first see a non-STEM school
            if not is_stem and first_non_stem_index is None:
                first_non_stem_index = i

            # If we've seen a non-STEM school and now see a STEM school, it's not sorted
            if first_non_stem_index is not None and is_stem:
                is_sorted = False
                sorting_violations.append({
                    'index': i,
                    'student_id': student['id'],
                    'school': school,
                    'issue': f"STEM school '{school}' found at row {i+2} after non-STEM school at row {first_non_stem_index+2}"
                })

        return is_sorted, sorting_violations

    def run_validation(self):
        filename = self.file_path.get()
        
        if not filename:
            messagebox.showerror("Error", "Please select a CSV file first!")
            return
        
        try:
            team_size = int(self.team_size.get())
            if team_size < 4 or team_size > 10:
                messagebox.showerror("Error", "Team size must be between 4 and 10!")
                return
        except:
            messagebox.showerror("Error", "Invalid team size! Please enter a number 4-10.")
            return
        
        self.clear_all_tabs()
        self.status_bar.config(text="Processing... Running ULTRA STRICT validation...")
        self.root.update()
        
        try:
            results = self.validate_csv(filename, team_size)

            # Update all text tabs
            self.summary_tab.delete('1.0', tk.END)
            self.gender_tab.delete('1.0', tk.END)
            self.school_tab.delete('1.0', tk.END)
            self.cgpa_tab.delete('1.0', tk.END)
            self.critical_tab.delete('1.0', tk.END)
            self.quality_tab.delete('1.0', tk.END)

            self.summary_tab.insert('1.0', results.get('summary', 'No summary available'))
            self.gender_tab.insert('1.0', results.get('gender', 'No gender issues.'))
            self.school_tab.insert('1.0', results.get('school', 'No school issues.'))
            self.cgpa_tab.insert('1.0', results.get('cgpa', 'No CGPA issues.'))
            self.critical_tab.insert('1.0', results.get('critical', 'No critical issues.'))
            self.quality_tab.insert('1.0', results.get('quality', 'No quality issues.'))

            self.inspector_display.insert('1.0', "✓ Data loaded successfully!\n\n")
            self.inspector_display.insert(tk.END, f"Total teams available: {len(self.all_teams)}\n\n")
            self.inspector_display.insert(tk.END, "Enter Tutorial and Team # above, then click 'Find Team'\n")
            self.inspector_display.insert(tk.END, "OR click 'List All Teams' to browse all teams.\n")

            total_issues = len(self.all_issues)
            critical = sum(1 for i in self.all_issues if i['severity'] == 'CRITICAL')
            warning = sum(1 for i in self.all_issues if i['severity'] == 'WARNING')
            info = sum(1 for i in self.all_issues if i['severity'] == 'INFO')

            self.status_bar.config(
                text=f"✓ Validation complete! Score: {results['score']:.1f}% | Grade: {results['grade']} | Issues: {total_issues} (🚨{critical}/⚠️{warning}/ℹ️{info})"
            )

            messagebox.showinfo(
                "Validation Complete",
                f"Overall Score: {results['score']:.1f}%\n"
                f"Grade: {results['grade']}\n"
                f"Strictness: {self.strictness.get()}\n"
                f"Issues found: {total_issues} (🚨 {critical}, ⚠️ {warning}, ℹ️ {info})\n\n"
                f"Check 'Critical Issues' tab for detailed reports."
            )

            # --- NEW: Auto-save validation output to folder Logs/TX ---
            try:
                import os
                from datetime import datetime

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                folder_path = os.path.join("Logs", f"T{team_size}")
                os.makedirs(folder_path, exist_ok=True)  # create Logs/T5 if not exists

                output_filename = os.path.join(folder_path, f"T{team_size}_Logs_{timestamp}.txt")

                with open(output_filename, "w", encoding="utf-8") as f:
                    f.write("="*80 + "\n")
                    f.write("TEAM VALIDATION LOG\n")
                    f.write("="*80 + "\n")
                    f.write(f"Timestamp: {datetime.now():%Y-%m-%d %H:%M:%S}\n")
                    f.write(f"CSV File:   {self.file_path.get()}\n")
                    f.write(f"Team Size:  {self.team_size.get()}\n")
                    f.write(f"Strictness: {self.strictness.get()}\n")
                    f.write(f"Score:      {results['score']:.1f}% | Grade: {results['grade']}\n")
                    f.write(f"Issues:     {total_issues} (🚨{critical}/⚠️{warning}/ℹ️{info})\n")
                    f.write("="*80 + "\n\n")

                    f.write("[SUMMARY REPORT]\n")
                    f.write("-"*80 + "\n")
                    f.write(self.summary_tab.get("1.0", tk.END))
                    f.write("\n")

                    f.write("[CRITICAL ISSUES REPORT]\n")
                    f.write("-"*80 + "\n")
                    f.write(self.critical_tab.get("1.0", tk.END))
                    f.write("\n")

                print(f"Validation results saved to {output_filename}")
            except Exception as e:
                print(f"Error saving validation output: {e}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            self.status_bar.config(text="Error during validation.")

    
    def validate_csv(self, filename, expected_team_size):
        file = open(filename, 'r', encoding='utf-8')
        lines = file.readlines()
        file.close()
        
        if len(lines) < 2:
            raise Exception("CSV file is empty or has no data rows!")
        
        header = lines[0].strip().split(',')
        col_map = self.detect_column_mapping(header)
        
        required = ['tutorial', 'id', 'school', 'gender', 'cgpa', 'team']
        missing = [field for field in required if field not in col_map]
        if missing:
            raise Exception(f"Could not detect required columns: {', '.join(missing)}")
        
        # STRICT CHECK 1: Duplicate Student IDs
        all_ids = []
        students = []
        duplicate_ids = set()
        
        for i in range(1, len(lines)):
            line = lines[i].strip()
            if not line:
                continue
            
            parts = line.split(',')
            if len(parts) <= max(col_map.values()):
                continue
            
            try:
                student_id = parts[col_map['id']].strip()
                
                # Check for duplicates
                if student_id in all_ids:
                    duplicate_ids.add(student_id)
                    self.add_issue('CRITICAL', 'Data Integrity', f"Duplicate Student ID: {student_id}")
                all_ids.append(student_id)
                
                student = {
                    'tutorial': parts[col_map['tutorial']].strip(),
                    'id': student_id,
                    'name': parts[col_map['name']].strip() if 'name' in col_map else 'N/A',
                    'school': parts[col_map['school']].strip(),
                    'gender': parts[col_map['gender']].strip(),
                    'cgpa': parts[col_map['cgpa']].strip(),
                    'team': parts[col_map['team']].strip()
                }
                
                # STRICT CHECK 2: Data format validation
                try:
                    cgpa_val = float(student['cgpa'])
                    if cgpa_val < 0 or cgpa_val > 5:
                        self.add_issue('CRITICAL', 'Data Integrity', f"Invalid CGPA {cgpa_val} for student {student_id}")
                except:
                    self.add_issue('CRITICAL', 'Data Integrity', f"Non-numeric CGPA for student {student_id}")
                
                if not student['gender'].upper() in ['M', 'MALE', 'F', 'FEMALE']:
                    self.add_issue('WARNING', 'Data Integrity', f"Invalid gender '{student['gender']}' for student {student_id}")
                
                students.append(student)
            except Exception as e:
                self.add_issue('WARNING', 'Data Integrity', f"Malformed row at line {i+1}: {str(e)}")
                continue
        
        if len(students) == 0:
            raise Exception("No valid student records found in CSV!")
        
        self.students_data = students
        
        # Calculate adaptive thresholds
        tutorials_list = {}
        for s in students:
            tut = s['tutorial']
            if tut not in tutorials_list:
                tutorials_list[tut] = []
            tutorials_list[tut].append(s)
        
        self.tutorial_demographics = {}
        for tut, tut_students in tutorials_list.items():
            self.tutorial_demographics[tut] = self.calculate_tutorial_thresholds(tut_students, expected_team_size)
        
        # Group by tutorial and team
        tutorials = {}
        self.all_teams = {}
        
        for s in students:
            tut, team = s['tutorial'], s['team']
            if tut not in tutorials:
                tutorials[tut] = {}
            if team not in tutorials[tut]:
                tutorials[tut][team] = []
            tutorials[tut][team].append(s)
            
            team_key = (tut, team)
            self.all_teams[team_key] = tutorials[tut][team]
        
        # STRICT CHECK 3: Team numbering consistency
        all_team_nums = set()
        for tut in tutorials:
            for team_num in tutorials[tut]:
                try:
                    num = int(team_num)
                    all_team_nums.add(num)
                except:
                    self.add_issue('WARNING', 'Data Quality', f"Non-numeric team number '{team_num}' in tutorial {tut}")
        
        if all_team_nums:
            expected_teams = set(range(1, max(all_team_nums) + 1))
            missing_teams = expected_teams - all_team_nums
            if missing_teams:
                self.add_issue('WARNING', 'Data Quality', f"Missing team numbers: {sorted(list(missing_teams))[:10]}")
        
        # Main Analysis
        total_teams = sum(len(teams) for teams in tutorials.values())
        gender_balanced, gender_imbalanced = 0, []
        school_balanced, school_imbalanced = 0, []
        all_team_means, all_team_stds, cgpa_high_variance = [], [], []
        team_sizes = []
        size_violations = []
        empty_teams = []
        
        strictness = self.strictness.get()
        
        for tut_name in tutorials:
            thresholds = self.tutorial_demographics[tut_name]
            
            for team_num in tutorials[tut_name]:
                team = tutorials[tut_name][team_num]
                size = len(team)
                team_sizes.append(size)
                
                # STRICT CHECK 4: Team size violations
                if size == 0:
                    empty_teams.append((tut_name, team_num))
                    self.add_issue('CRITICAL', 'Team Formation', f"Empty team: Tutorial {tut_name}, Team {team_num}")
                
                if size != expected_team_size:
                    size_violations.append((tut_name, team_num, size, expected_team_size))
                    if strictness in ["ULTRA", "NIGHTMARE"]:
                        if abs(size - expected_team_size) > 1:
                            self.add_issue('CRITICAL', 'Team Formation', 
                                         f"Team size {size} deviates significantly from expected {expected_team_size} (Tutorial {tut_name}, Team {team_num})")
                        else:
                            self.add_issue('WARNING', 'Team Formation', 
                                         f"Team size {size} differs from expected {expected_team_size} (Tutorial {tut_name}, Team {team_num})")
                
                # Gender check
                males = sum(1 for s in team if s['gender'].upper() in ['M', 'MALE'])
                females = len(team) - males
                
                if males <= thresholds['male_max'] and females <= thresholds['female_max']:
                    gender_balanced += 1
                else:
                    gender_imbalanced.append((tut_name, team_num, males, females, size, thresholds['male_max'], thresholds['female_max']))
                    self.add_issue('WARNING', 'Gender Balance', 
                                 f"Tutorial {tut_name}, Team {team_num}: M={males}, F={females} (max: {thresholds['male_max']}M/{thresholds['female_max']}F)")
                
                # STRICT CHECK 5: Single gender teams (nightmare mode)
                if strictness == "NIGHTMARE":
                    if males == 0 or females == 0:
                        self.add_issue('CRITICAL', 'Gender Balance', 
                                     f"Single-gender team detected: Tutorial {tut_name}, Team {team_num} (M={males}, F={females})")
                
                # School check
                max_school = (size // 2) + 1
                school_count = {}
                for s in team:
                    school_count[s['school']] = school_count.get(s['school'], 0) + 1
                
                school_ok = True
                for school, count in school_count.items():
                    if count > max_school:
                        school_imbalanced.append((tut_name, team_num, school, count, size, max_school))
                        school_ok = False
                        self.add_issue('WARNING', 'School Diversity', 
                                     f"Tutorial {tut_name}, Team {team_num}: {school} has {count}/{size} members (max: {max_school})")
                
                if school_ok:
                    school_balanced += 1
                
                # STRICT CHECK 6: Single school teams
                if len(school_count) == 1 and size > 1:
                    self.add_issue('CRITICAL', 'School Diversity', 
                                 f"All members from same school: Tutorial {tut_name}, Team {team_num} ({list(school_count.keys())[0]})")
                
                # CGPA check
                cgpas = [float(s['cgpa']) for s in team if s['cgpa']]
                if len(cgpas) > 1:
                    mean = sum(cgpas) / len(cgpas)
                    std = math.sqrt(sum((x - mean) ** 2 for x in cgpas) / len(cgpas))
                    all_team_means.append(mean)
                    all_team_stds.append(std)
                    
                    # STRICT CHECK 7: Extreme CGPA variance
                    if strictness == "NIGHTMARE" and std >= 0.6:
                        cgpa_high_variance.append((tut_name, team_num, mean, std))
                        self.add_issue('WARNING', 'CGPA Distribution', 
                                     f"Very high CGPA variance: Tutorial {tut_name}, Team {team_num} (std={std:.3f})")
                    elif std >= 0.7:
                        cgpa_high_variance.append((tut_name, team_num, mean, std))
                        self.add_issue('WARNING', 'CGPA Distribution', 
                                     f"Extreme CGPA variance: Tutorial {tut_name}, Team {team_num} (std={std:.3f})")
                    
                    # STRICT CHECK 8: CGPA outliers within team
                    if strictness in ["ULTRA", "NIGHTMARE"]:
                        for s in team:
                            try:
                                cgpa = float(s['cgpa'])
                                if abs(cgpa - mean) > 2 * std and std > 0:
                                    self.add_issue('INFO', 'CGPA Distribution', 
                                                 f"Potential outlier: {s['name']} (CGPA {cgpa:.2f}) in Tutorial {tut_name}, Team {team_num} (mean={mean:.2f}, std={std:.2f})")
                            except:
                                pass
        
        # STRICT CHECK 9: Tutorial size consistency
        tutorial_sizes = {}
        for tut, tut_students in tutorials_list.items():
            tutorial_sizes[tut] = len(tut_students)
        
        if len(set(tutorial_sizes.values())) > 3:  # More than 3 different sizes
            self.add_issue('WARNING', 'Data Quality', f"High variation in tutorial sizes: {dict(list(tutorial_sizes.items())[:5])}")
        
        # STRICT CHECK 10: Teams per tutorial consistency
        teams_per_tutorial = {tut: len(tutorials[tut]) for tut in tutorials}
        expected_teams_per_tut = {tut: (len(tutorials_list[tut]) + expected_team_size - 1) // expected_team_size 
                                  for tut in tutorials_list}
        
        for tut in tutorials:
            if teams_per_tutorial[tut] != expected_teams_per_tut[tut]:
                self.add_issue('WARNING', 'Team Formation', 
                             f"Tutorial {tut}: Expected {expected_teams_per_tut[tut]} teams, got {teams_per_tutorial[tut]}")
        
        
        # STRICT CHECK 11: STEM Sorting Order
        stem_sorted, stem_violations = self.check_stem_sorting()
        if not stem_sorted:
            self.add_issue('WARNING', 'Data Quality', 
                          f"CSV not sorted by STEM status: {len(stem_violations)} violation(s)")
            for violation in stem_violations[:5]:  # Show first 5 violations
                self.add_issue('INFO', 'Data Quality', 
                              f"Row {violation['index']+2}: {violation['school']} (STEM) appears after non-STEM schools")

# Calculate scores with penalties
        gender_balance_rate = (gender_balanced / total_teams) * 100
        school_balance_rate = (school_balanced / total_teams) * 100
        high_var = sum(1 for std in all_team_stds if std >= 0.5)
        cgpa_score = 100 - (high_var / total_teams * 100) if all_team_stds else 100
        
        # Apply penalties based on critical issues
        critical_count = sum(1 for i in self.all_issues if i['severity'] == 'CRITICAL')
        penalty = min(critical_count * 2, 20)  # Max 20% penalty
        
        overall_score = (gender_balance_rate * 0.4 + school_balance_rate * 0.4 + cgpa_score * 0.2) - penalty
        overall_score = max(0, overall_score)  # Floor at 0
        
        if overall_score >= 95:
            grade = "A+ (Excellent)"
        elif overall_score >= 90:
            grade = "A  (Very Good)"
        elif overall_score >= 85:
            grade = "B+ (Good)"
        elif overall_score >= 80:
            grade = "B  (Acceptable)"
        elif overall_score >= 75:
            grade = "C+ (Needs Improvement)"
        elif overall_score >= 70:
            grade = "C  (Poor)"
        else:
            grade = "F  (Failed)"
        
        summary = self.build_summary(students, total_teams, expected_team_size, team_sizes,
                                     gender_balanced, len(gender_imbalanced), gender_balance_rate,
                                     school_balanced, len(school_imbalanced), school_balance_rate,
                                     all_team_means, all_team_stds, overall_score, grade, col_map, penalty)
        
        gender = self.build_gender_report_adaptive(gender_imbalanced)
        school = self.build_school_report(school_imbalanced)
        cgpa = self.build_cgpa_report(cgpa_high_variance, all_team_means, all_team_stds, total_teams)
        critical = self.build_critical_report()
        quality = self.build_quality_report(len(students), total_teams, duplicate_ids, size_violations, empty_teams)
        
        return {
            'summary': summary, 'gender': gender, 'school': school, 'cgpa': cgpa,
            'critical': critical, 'quality': quality,
            'score': overall_score, 'grade': grade
        }
    
    def build_critical_report(self):
        """Build comprehensive report showing ALL issues by severity."""
        if not self.all_issues:
            return "✅ No issues detected! Perfect allocation.\n\nYour algorithm is flawless."
        
        # Sort issues by severity level: CRITICAL > WARNING > INFO
        severity_order = {'CRITICAL': 3, 'WARNING': 2, 'INFO': 1}
        sorted_issues = sorted(self.all_issues, key=lambda x: severity_order.get(x['severity'], 0), reverse=True)

        report = "="*70 + "\n"
        report += f"ALL ISSUES FOUND ({len(self.all_issues)} total)\n"
        report += "="*70 + "\n\n"

        current_severity = None
        severity_counts = {'CRITICAL': 0, 'WARNING': 0, 'INFO': 0}

        for i, issue in enumerate(sorted_issues, 1):
            sev = issue['severity']
            severity_counts[sev] += 1

        for sev in ['CRITICAL', 'WARNING', 'INFO']:
            issues = [issue for issue in sorted_issues if issue['severity'] == sev]
            if not issues:
                continue
            # Header per severity
            icons = {'CRITICAL': '🚨', 'WARNING': '⚠️', 'INFO': 'ℹ️'}
            report += f"{icons.get(sev, '')} {sev} ISSUES ({len(issues)}):\n"
            report += "-"*70 + "\n"
            for idx, issue in enumerate(issues, 1):
                report += f"{idx:3d}. [{issue['category']}] {issue['message']}\n"
            report += "\n"

        return report
    
    def build_quality_report(self, total_students, total_teams, duplicates, size_violations, empty_teams):
        """Build data quality report."""
        s = "="*70 + "\n"
        s += "DATA QUALITY ANALYSIS\n"
        s += "="*70 + "\n\n"
        
        s += f"Total Records: {total_students}\n"
        s += f"Total Teams: {total_teams}\n\n"
        
        s += "QUALITY CHECKS:\n"
        s += "-"*70 + "\n"
        
        s += f"✓ Duplicate Student IDs: {len(duplicates)}\n"
        if duplicates:
            s += f"  IDs: {list(duplicates)[:10]}\n"
        
        s += f"✓ Team Size Violations: {len(size_violations)}\n"
        if size_violations and len(size_violations) <= 20:
            for tut, team, size, expected in size_violations[:20]:
                s += f"  - Tutorial {tut}, Team {team}: size {size} (expected {expected})\n"
        
        s += f"✓ Empty Teams: {len(empty_teams)}\n"
        if empty_teams:
            for tut, team in empty_teams:
                s += f"  - Tutorial {tut}, Team {team}\n"
        
        
        # Check STEM sorting
        stem_sorted, stem_violations = self.check_stem_sorting()
        s += f"✓ STEM Sorting: {'CORRECT' if stem_sorted else 'INCORRECT'}\n"
        if not stem_sorted:
            s += f"   {len(stem_violations)} sorting violation(s) detected\n"
            for violation in stem_violations[:10]:  # Show up to 10 violations
                s += f"   - {violation['issue']}\n"

        return s
    
    # ... [Keep all other methods: find_team, list_all_teams, display_team_details, build_summary, build_gender_report_adaptive, build_school_report, build_cgpa_report] ...
    
    def find_team(self):
        tutorial = self.search_tutorial.get().strip()
        team = self.search_team.get().strip()
        
        if not tutorial or not team:
            messagebox.showwarning("Input Required", "Please enter both Tutorial and Team number!")
            return
        
        team_key = (tutorial, team)
        if team_key not in self.all_teams:
            self.inspector_display.delete('1.0', tk.END)
            self.inspector_display.insert('1.0', f"❌ Team not found!\n\nTutorial: {tutorial}\nTeam: {team}")
            return
        
        self.display_team_details(tutorial, team)
    
    def list_all_teams(self):
        if not self.all_teams:
            messagebox.showwarning("No Data", "Please run validation first!")
            return
        
        self.inspector_display.delete('1.0', tk.END)
        self.inspector_display.insert('1.0', "="*70 + "\n")
        self.inspector_display.insert(tk.END, "ALL TEAMS SUMMARY\n")
        self.inspector_display.insert(tk.END, "="*70 + "\n\n")
        
        tutorials = {}
        for (tut, team), members in self.all_teams.items():
            if tut not in tutorials:
                tutorials[tut] = []
            tutorials[tut].append((team, len(members)))
        
        for tut in sorted(tutorials.keys()):
            self.inspector_display.insert(tk.END, f"\nTutorial {tut}:\n")
            self.inspector_display.insert(tk.END, "-"*70 + "\n")
            for team, size in sorted(tutorials[tut], key=lambda x: int(x[0]) if x[0].isdigit() else x[0]):
                self.inspector_display.insert(tk.END, f"  Team {team}: {size} members\n")
        
        self.inspector_display.insert(tk.END, f"\n{'='*70}\n")
        self.inspector_display.insert(tk.END, f"Total: {len(self.all_teams)} teams\n")
    
    def display_team_details(self, tutorial, team):
        team_key = (tutorial, team)
        members = self.all_teams[team_key]
        
        self.inspector_display.delete('1.0', tk.END)
        self.inspector_display.insert('1.0', "="*70 + "\n")
        self.inspector_display.insert(tk.END, f"TEAM DETAILS: Tutorial {tutorial}, Team {team}\n")
        self.inspector_display.insert(tk.END, "="*70 + "\n\n")
        
        self.inspector_display.insert(tk.END, f"Team Size: {len(members)}\n\n")
        
        if tutorial in self.tutorial_demographics:
            thresholds = self.tutorial_demographics[tutorial]
            max_male = thresholds['male_max']
            max_female = thresholds['female_max']
            self.inspector_display.insert(tk.END, f"Tutorial demographics: {thresholds['male_ratio']*100:.1f}% M, {thresholds['female_ratio']*100:.1f}% F\n")
            self.inspector_display.insert(tk.END, f"Adaptive limits: ≤{max_male} males, ≤{max_female} females\n\n")
        else:
            max_male = max_female = (len(members) // 2) + 1
        
        males = sum(1 for s in members if s['gender'].upper() in ['M', 'MALE'])
        females = len(members) - males
        
        gender_balanced = males <= max_male and females <= max_female
        gender_status = "✓ BALANCED" if gender_balanced else "⚠ IMBALANCED"
        
        self.inspector_display.insert(tk.END, f"Gender Distribution: {gender_status}\n")
        self.inspector_display.insert(tk.END, f"  Males:   {males} (max: {max_male})\n")
        self.inspector_display.insert(tk.END, f"  Females: {females} (max: {max_female})\n\n")
        
        school_count = {}
        for s in members:
            school_count[s['school']] = school_count.get(s['school'], 0) + 1
        
        max_school = (len(members) // 2) + 1
        school_balanced = all(count <= max_school for count in school_count.values())
        school_status = "✓ BALANCED" if school_balanced else "⚠ IMBALANCED"
        
        self.inspector_display.insert(tk.END, f"School Distribution: {school_status}\n")
        for school, count in sorted(school_count.items()):
            marker = "⚠" if count > max_school else " "
            self.inspector_display.insert(tk.END, f" {marker} {school:15s}: {count} (max: {max_school})\n")
        self.inspector_display.insert(tk.END, "\n")
        
        cgpas = [float(s['cgpa']) for s in members if s['cgpa']]
        if cgpas:
            mean = sum(cgpas) / len(cgpas)
            std = math.sqrt(sum((x - mean) ** 2 for x in cgpas) / len(cgpas))
            
            self.inspector_display.insert(tk.END, f"CGPA Statistics:\n")
            self.inspector_display.insert(tk.END, f"  Mean:   {mean:.3f}\n")
            self.inspector_display.insert(tk.END, f"  Std:    {std:.3f}\n")
            self.inspector_display.insert(tk.END, f"  Range:  {min(cgpas):.3f} to {max(cgpas):.3f}\n\n")
        
        self.inspector_display.insert(tk.END, "="*70 + "\n")
        self.inspector_display.insert(tk.END, "TEAM MEMBERS:\n")
        self.inspector_display.insert(tk.END, "="*70 + "\n\n")
        
        for i, student in enumerate(members, 1):
            self.inspector_display.insert(tk.END, f"{i}. {student['name']}\n")
            self.inspector_display.insert(tk.END, f"   ID:     {student['id']}\n")
            self.inspector_display.insert(tk.END, f"   School: {student['school']}\n")
            self.inspector_display.insert(tk.END, f"   Gender: {student['gender']}\n")
            self.inspector_display.insert(tk.END, f"   CGPA:   {student['cgpa']}\n\n")
    
    def build_summary(self, students, total_teams, expected_size, team_sizes, 
                     gender_bal, gender_imbal, gender_rate,
                     school_bal, school_imbal, school_rate,
                     means, stds, score, grade, col_map, penalty):
        s = "="*70 + "\n"
        s += f"TEAM ALLOCATION VALIDATION SUMMARY ({self.strictness.get()} MODE)\n"
        s += "="*70 + "\n\n"
        
        s += f"✓ Strictness Level: {self.strictness.get()}\n"
        s += f"✓ Total Issues Found: {len(self.all_issues)}\n"
        if penalty > 0:
            s += f"⚠️  Score Penalty: -{penalty:.1f}%\n"
        s += "\n"
        
        s += f"Total Students: {len(students)}\n"
        s += f"Total Teams:    {total_teams}\n"
        s += f"Expected Size:  {expected_size}\n\n"
        
        size_counts = {}
        for size in team_sizes:
            size_counts[size] = size_counts.get(size, 0) + 1
        
        s += "TEAM SIZE DISTRIBUTION:\n"
        s += "-"*70 + "\n"
        for size in sorted(size_counts.keys()):
            count = size_counts[size]
            perc = (count / total_teams) * 100
            status = "✓" if size == expected_size else "⚠"
            s += f"{status} Size {size}: {count:4d} teams ({perc:5.1f}%)\n"
        
        s += "\n" + "="*70 + "\n"
        s += "BALANCE SUMMARY\n"
        s += "="*70 + "\n\n"
        
        s += f"GENDER BALANCE:\n"
        s += f"  ✓ Balanced:   {gender_bal:4d} teams ({gender_rate:5.1f}%)\n"
        s += f"  ✗ Imbalanced: {gender_imbal:4d} teams ({100-gender_rate:5.1f}%)\n\n"
        
        s += f"SCHOOL DIVERSITY:\n"
        s += f"  ✓ Balanced:   {school_bal:4d} teams ({school_rate:5.1f}%)\n"
        s += f"  ✗ Imbalanced: {school_imbal:4d} teams ({100-school_rate:5.1f}%)\n\n"
        
        if means:
            s += f"CGPA STATISTICS:\n"
            s += f"  Average team mean: {sum(means)/len(means):.3f}\n"
            s += f"  Average team std:  {sum(stds)/len(stds):.3f}\n"
            s += f"  Range: {min(means):.3f} to {max(means):.3f}\n\n"
        
        s += "="*70 + "\n"
        s += "OVERALL QUALITY SCORE\n"
        s += "="*70 + "\n\n"
        s += f"Gender Balance:     {gender_rate:5.1f}%\n"
        s += f"School Diversity:   {school_rate:5.1f}%\n"
        if stds:
            cgpa_dist = 100 - (sum(1 for std in stds if std >= 0.5) / len(stds) * 100)
        else:
            cgpa_dist = 100
        s += f"CGPA Distribution:  {cgpa_dist:5.1f}%\n"
        if penalty > 0:
            s += f"Penalty:            -{penalty:.1f}%\n"
        s += "-"*70 + "\n"
        s += f"FINAL SCORE:        {score:5.1f}%\n"
        s += f"GRADE:              {grade}\n"
        
        return s
    
    def build_gender_report_adaptive(self, imbalanced):
        if not imbalanced:
            return "✅ Perfect gender balance!\nAll teams respect tutorial demographics."
        
        s = f"GENDER-IMBALANCED TEAMS ({len(imbalanced)} total)\n"
        s += "="*70 + "\n\n"
        for i, (tut, team, m, f, size, max_m, max_f) in enumerate(imbalanced, 1):
            s += f"{i:3d}. Tutorial {tut:6s}, Team {team:4s}: M={m}, F={f} "
            s += f"(size={size}, max: {max_m}M/{max_f}F)\n"
        return s
    
    def build_school_report(self, imbalanced):
        if not imbalanced:
            return "✅ Perfect school diversity!\nAll teams have proper school balance."
        
        s = f"SCHOOL-IMBALANCED TEAMS ({len(imbalanced)} total)\n"
        s += "="*70 + "\n\n"
        for i, (tut, team, school, count, size, max_allow) in enumerate(imbalanced, 1):
            s += f"{i:3d}. Tutorial {tut:6s}, Team {team:4s}: {school:15s} "
            s += f"has {count}/{size} members (max: {max_allow})\n"
        return s
    
    def build_cgpa_report(self, high_var, means, stds, total_teams):
        s = "CGPA VARIANCE ANALYSIS\n"
        s += "="*70 + "\n\n"
        
        if not stds:
            return s + "No CGPA data available.\n"
        
        low_var = sum(1 for std in stds if std < 0.3)
        med_var = sum(1 for std in stds if 0.3 <= std < 0.5)
        high_v = sum(1 for std in stds if std >= 0.5)
        
        s += f"Low variance (< 0.3):      {low_var:4d} teams ({low_var/total_teams*100:5.1f}%)\n"
        s += f"Medium variance (0.3-0.5): {med_var:4d} teams ({med_var/total_teams*100:5.1f}%)\n"
        s += f"High variance (≥ 0.5):     {high_v:4d} teams ({high_v/total_teams*100:5.1f}%)\n\n"
        
        if high_var:
            s += f"Teams with HIGH variance: {len(high_var)}\n"
            s += "-"*70 + "\n"
            for i, (tut, team, mean, std) in enumerate(high_var[:100], 1):
                s += f"{i:3d}. Tutorial {tut:6s}, Team {team:4s}: Mean={mean:.2f}, Std={std:.2f}\n"
        else:
            s += "✅ All teams have acceptable CGPA variance!\n"
        
        return s


if __name__ == "__main__":
    root = tk.Tk()
    app = TeamValidatorGUI(root)
    root.mainloop()
