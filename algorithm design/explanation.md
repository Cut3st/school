# Team Allocation System - README

## Overview
This Python application automatically creates balanced student teams based on tutorial groups, ensuring diversity in CGPA, gender, and STEM/Non-STEM school representation. The algorithm prioritizes fairness and balanced distribution while respecting team size constraints.

---

## Core Balancing Philosophy

The system uses a **minority-first, ratio-constrained** approach:

1. **Ratio Calculation**: Determines acceptable maximums for each category (male/female/STEM/non-STEM) based on the overall population
2. **Minority Priority**: Students from underrepresented groups are placed first to ensure they aren't squeezed out later
3. **CGPA Sorting**: Students are sorted by academic performance and distributed to prevent clustering of high/low performers
4. **Constraint Checking**: Every placement is validated against gender and STEM balance rules

---

## Constants

### `STEM_SCHOOLS`
```python
["CCDS", "CCEB", "CoE", "EEE", "MAE", "SPMS", "SBS", "MSE", "CEE"]
```
List of school codes considered STEM (Science, Technology, Engineering, Mathematics). Students from these schools are counted as STEM; all other non-empty schools are Non-STEM.

---

## Function Documentation

### `read_file(filename)`
**Purpose**: Loads and validates student data from a CSV file.

**Process**:
1. Opens CSV with headers: `['tutorial', 'id', 'name', 'school', 'gender', 'cgpa']`
2. Skips the header row (`next(reader)`)
3. Ignores completely empty rows
4. Converts `cgpa` field from string to float
5. Initializes `team` field to 0 for all students
6. Appends valid records to the students list

**Error Handling**: 
- Prints warning for invalid CGPA values
- Skips malformed rows without crashing

**Returns**: List of dictionaries, each representing a student with validated data.

---

### `calculate_ratio(students, team_size)`
**Purpose**: Computes maximum allowed members per category for any team.

**Formula**:
```
tolerance = 0.15 + (team_size - 5) * 0.02
male_max = round(team_size * (male_population/total + tolerance))
female_max = round(team_size * (female_population/total + tolerance))
stem_max = round(team_size * (stem_population/total + tolerance))
nonstem_max = round(team_size * (nonstem_population/total + tolerance))
```

**Tolerance Logic**: 
- Base tolerance is 15%
- Increases by 2% for each member above 5 (e.g., team_size=8 → 21% tolerance)
- Allows flexibility beyond strict population proportions

**Edge Case**: If no students, returns minimum team size of 1 for all categories.

**Returns**: Dictionary with `male_max`, `female_max`, `stem_max`, `nonstem_max` values.

---

### `count_gender(team)`
**Purpose**: Tallies male and female students in a team.

**Recognition**:
- Male: `'M'` or `'MALE'` (case-insensitive)
- Female: `'F'` or `'FEMALE'` (case-insensitive)

**Returns**: Tuple `(male_count, female_count)`

---

### `count_stem(team)`
**Purpose**: Tallies STEM and Non-STEM students in a team.

**Logic**: 
- Increments `stem` if `student['school']` is in `STEM_SCHOOLS`
- Increments `nonstem` if `student['school']` is not empty and not in STEM list

**Returns**: Tuple `(stem_count, nonstem_count)`

---

### `check_balanced(team, student, team_size, ratio)`
**Purpose**: Validates if adding a student maintains all balance constraints.

**Process**:
1. Creates temporary team (current team + new student)
2. Checks if team would exceed `team_size`
3. Counts gender and STEM in temporary team
4. Verifies all counts are within `ratio` maximums

**Returns**: `True` if balanced, `False` otherwise.

---

### `group_by_tutorial(students)`
**Purpose**: Segregates students by their tutorial class.

**Process**: Iterates through students, grouping them into a dictionary where keys are tutorial IDs and values are lists of students.

**Returns**: Dictionary `{tutorial_id: [student_list]}`

---

### `sort_by_cgpa(students)`
**Purpose**: Sorts students by CGPA in **descending order** (highest first).

**Algorithm**: Uses **selection sort** (O(n²) complexity):
1. Finds maximum CGPA in unsorted portion
2. Swaps it with the current position
3. Repeats until sorted

**Why Selection Sort**: Stable for small datasets; predictable performance.

**Returns**: Same list sorted in-place by CGPA.

---

### `form_teams(students, team_size)`
**Purpose**: Core algorithm that creates balanced teams within one tutorial.

#### Phase 1: Setup
1. Calculate `ratio` constraints for the tutorial
2. Determine number of teams: `(total_students + team_size - 1) // team_size`
3. Distribute remainder: Some teams get `base_size + 1`, others get `base_size`

#### Phase 2: Categorization & Sorting
**Splits students into four pools** (all sorted by CGPA descending):
- `stem`: STEM school students
- `nonstem`: Non-STEM school students
- `males`: Male students
- `females`: Female students

**Identifies Minority/Majority**:
- `stem_minority` / `stem_majority`: Smaller/larger of STEM vs Non-STEM
- `gender_minority` / `gender_majority`: Smaller/larger of Male vs Female

**Shuffles majority groups**: Randomizes order to prevent predictable placement patterns.

#### Phase 3: Minority Placement (Priority)
1. **STEM Minority First**: Places them round-robin across teams (team 0, 1, 2..., then wrap)
2. **Gender Minority Next**: Also round-robin, skipping already-placed students

This ensures underrepresented groups get first choice of slots.

#### Phase 4: Majority Placement (Constraint-Aware)
Processes majority groups in order: Gender Majority → STEM Majority

**For each student**:
1. **Constraint Check**: Starting from `current_team`, searches for first team where student fits within `ratio` limits
2. **Fallback**: If no team satisfies constraints, places in team with most available space
3. **Updates**: Marks student as placed, advances `current_team` to next index

**CGPA Diversification**: Since all pools are CGPA-sorted, high performers are distributed evenly across teams during round-robin placement.

**Returns**: List of teams, where each team is a list of student dictionaries.

---

### `write_csv(all_students, filename)`
**Purpose**: Exports final team assignments to CSV.

**Process**:
1. Groups students by `(tutorial, team)` tuple
2. **Sorts groups**: Uses bubble sort on the tuple keys (tutorial ascending, team ascending)
3. Writes sorted rows to CSV with all original fields plus `team` number

**Output Format**: `tutorial`, `id`, `school`, `name`, `gender`, `cgpa`, `team`

---

### `main()`
**Purpose**: Command-line interface and orchestration.

**Workflow**:
1. Prompts for team size (validates 4-10 range)
2. Loads students from `records.csv`
3. Groups by tutorial
4. Forms teams for each tutorial sequentially
5. Assigns global team numbers (increments across tutorials)
6. Saves to `FCS1_Team2_Joshua.csv`
7. Prints completion message

---

## CGPA Diversification Explained

The algorithm ensures **CGPA heterogeneity** through:

1. **Sorted Pools**: Each category (STEM, Non-STEM, Male, Female) is sorted by CGPA descending
2. **Round-Robin Distribution**: Minority groups are placed in sequential team order (0→1→2→...), spreading high and low performers
3. **Sequential Processing**: High-CGPA students are processed first, grabbing early slots in all teams
4. **Example**: If 3 teams and STEM minority = [3.9, 3.8, 3.7, 3.6, ...], placement is:
   - Team 0: 3.9
   - Team 1: 3.8
   - Team 2: 3.7
   - Team 0: 3.6
   - ...and so on

Result: Each team receives a similar CGPA distribution curve.

---

## Gender & STEM Balancing Explained

### Ratio Calculation Example
For a tutorial with 30 students (18 Male, 12 Female, 20 STEM, 10 Non-STEM) and `team_size=6`:

```
tolerance = 0.15 + (6-5)*0.02 = 0.17
male_max = round(6 * (18/30 + 0.17)) = round(6 * 0.77) = 5
female_max = round(6 * (12/30 + 0.17)) = round(6 * 0.57) = 4
stem_max = round(6 * (20/30 + 0.17)) = round(6 * 0.84) = 6
nonstem_max = round(6 * (10/30 + 0.17)) = round(6 * 0.50) = 3
```

### Placement Constraints
- No team can exceed 5 males or 4 females
- No team can exceed 6 STEM or 3 Non-STEM students
- The `check_balanced()` function enforces these limits for every single placement

### Minority Protection
If females are minority (12 vs 18 males), they get placed first, guaranteeing they won't be excluded when male majority fills remaining slots.

---

## Sample Input (`records.csv`)

```csv
tutorial,id,name,school,gender,cgpa
T1,S123456,Alice Tan,SPMS,F,3.85
T1,S123457,Bob Lim,CoE,M,3.92
T1,S123458,Charlie Wong,SSS,M,3.45
T1,S123459,Diana Ng,MAE,F,3.78
T1,S123460,Eric Chua,CCDS,M,3.65
T1,S123461,Fiona Lee,NBS,F,3.50
T2,S123462,George Ho,EEE,M,3.80
T2,S123463,Helen Chan,SOH,F,3.60
```

## Sample Output (`FCS1_Team2_Joshua.csv`)

```csv
tutorial,id,school,name,gender,cgpa,team
T1,S123456,SPMS,Alice Tan,F,3.85,1
T1,S123457,CoE,Bob Lim,M,3.92,1
T1,S123458,SSS,Charlie Wong,M,3.45,2
T1,S123459,MAE,Diana Ng,F,3.78,2
T1,S123460,CCDS,Eric Chua,M,3.65,1
T1,S123461,NBS,Fiona Lee,F,3.5,2
T2,S123462,EEE,George Ho,M,3.8,3
T2,S123463,SOH,Helen Chan,F,3.6,3
```

---

## Key Design Decisions

| Feature | Rationale |
|---------|-----------|
| **Tutorial Isolation** | Prevents cross-tutorial scheduling conflicts; keeps teams co-located |
| **Minority-First Placement** | Guarantees representation; prevents majority monopolization |
| **Dynamic Tolerance** | Larger teams need more flexibility; scales with size |
| **Fallback Placement** | Ensures all students are placed even if strict balance is impossible |
| **In-Place Sorting** | Memory efficient for small datasets (<500 students) |
| **Global Team Numbers** | Unique identifiers across all tutorials for easy reference |

---

## Usage Instructions

1. **Prepare Input**: Create `records.csv` with required columns
2. **Run Script**: Execute `python team_allocator.py`
3. **Enter Team Size**: Input number between 4-10 when prompted
4. **Check Output**: Results saved to `FCS1_Team2_Joshua.csv`
5. **Review Warnings**: Check console for any CGPA parsing errors

---

## Limitations & Considerations

- **No Homogeneity Checks**: Algorithm doesn't enforce *minimum* members per category
- **O(n²) Sorting**: Selection sort may be slow for >1000 students; consider `sorted()` for better performance
- **Single CSV Input**: Hardcoded filename; could be made configurable
- **Binary Gender**: Only recognizes M/F; doesn't handle non-binary or unspecified genders
- **No Preference Handling**: Doesn't account for student preferences or conflicts

---

## Performance Characteristics

- **Time Complexity**: O(n²) due to selection sort; O(n×m) for placement (n=students, m=teams)
- **Space Complexity**: O(n) for student list; O(n) for team structures
- **Scalability**: Suitable for up to ~500 students per tutorial on modern hardware