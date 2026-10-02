import random
import csv
import os

def load_salary_data():
    data = {
        'base_salaries': {},
        'education_multipliers': {},
        'location_multipliers': {},
        'companies': {},
        'education_levels': set(),
        'job_roles': set(),
        'locations': set(),
        'job_education_requirements': {}
    }
    
    try:
        with open(os.path.join('data', 'salary_data.csv'), 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Store base salary and job role
                job_role = row['job_role']
                data['job_roles'].add(job_role)
                data['base_salaries'][job_role] = float(row['base_salary'])
                
                # Store education multiplier and level if present
                if row['education_level'] and row['education_multiplier']:
                    education = row['education_level']
                    data['education_levels'].add(education)
                    data['education_multipliers'][education] = float(row['education_multiplier'])
                
                # Store location and multiplier if present
                if row['location'] and row['location_multiplier']:
                    location = row['location']
                    data['locations'].add(location)
                    data['location_multipliers'][location] = float(row['location_multiplier'])
                
                # Store companies
                companies = [row[f'company{i}'] for i in range(1, 6) if row[f'company{i}']]
                if companies:
                    data['companies'][job_role] = companies
                
                # Store minimum education requirement
                if row['min_education']:
                    data['job_education_requirements'][job_role] = row['min_education']
    except Exception as e:
        print(f"Error reading salary_data.csv: {e}")
        return None
    
    # Convert sets to sorted lists for consistent ordering
    data['education_levels'] = sorted(list(data['education_levels']))
    data['job_roles'] = sorted(list(data['job_roles']))
    data['locations'] = sorted(list(data['locations']))
    return data

# Load data once when module is imported
SALARY_DATA = load_salary_data()

# Initialize lists from salary_data.csv
education_levels = SALARY_DATA['education_levels'] if SALARY_DATA else []
job_roles = SALARY_DATA['job_roles'] if SALARY_DATA else []
locations = SALARY_DATA['locations'] if SALARY_DATA else []

# Education level hierarchy (from lowest to highest)
EDUCATION_HIERARCHY = ['High School', 'Diploma', 'Associate', 'Bachelor', 'Master', 'PhD']

def get_job_roles_by_education(education):
    """Get job roles available for a given education level"""
    if not SALARY_DATA:
        return []
    
    # Find the index of the given education level
    try:
        education_index = EDUCATION_HIERARCHY.index(education)
    except ValueError:
        return []
    
    # Return jobs where the person's education level is >= minimum required education
    available_jobs = []
    for job, min_education in SALARY_DATA['job_education_requirements'].items():
        try:
            min_education_index = EDUCATION_HIERARCHY.index(min_education)
            if education_index >= min_education_index:
                available_jobs.append(job)
        except ValueError:
            continue
    
    return sorted(available_jobs)

def predict_salary(experience, education, job_role, location):
    if not SALARY_DATA:
        raise ValueError("Failed to load salary data")

    # Validate inputs
    if not all([experience, education, job_role, location]):
        raise ValueError("All fields are required")

    if job_role not in SALARY_DATA['base_salaries']:
        raise ValueError(f"Invalid job role: {job_role}")

    if education not in SALARY_DATA['education_multipliers']:
        raise ValueError(f"Invalid education level: {education}")

    if location not in SALARY_DATA['location_multipliers']:
        raise ValueError(f"Invalid location: {location}")

    try:
        experience = float(experience)
        if experience < 0:
            raise ValueError("Experience cannot be negative")
    except ValueError:
        raise ValueError("Invalid experience value")

    # Calculate base salary
    base_salary = SALARY_DATA['base_salaries'][job_role]

    # Apply education multiplier
    salary = base_salary * SALARY_DATA['education_multipliers'][education]

    # Apply location multiplier
    salary = salary * SALARY_DATA['location_multipliers'][location]

    # Apply experience multiplier (5% increase per year)
    salary = salary * (1 + (0.05 * experience))

    # Add some random variation (±5%)
    variation = random.uniform(-0.05, 0.05)
    salary = salary * (1 + variation)

    return round(salary, 2)

def get_companies_for_role(job_role):
    if not SALARY_DATA:
        return []
    return SALARY_DATA['companies'].get(job_role, [])
