"""
Utility module for generating admission data according to specifications
"""
import pandas as pd
import random
from datetime import datetime, date
from ..models import EducationalProgram


def generate_admission_data(target_date=None):
    """
    Generate admission data according to the specifications:
    - Different dates (Aug 1-4)
    - Different programs (PM, IVT, ITSS, IB)
    - Specific numbers of applicants per program and date
    - Cross-program intersections
    """
    if target_date is None:
        target_date = date.today()
    
    # Define educational programs with their codes and seat counts
    programs_info = {
        'PM': {'name': 'Прикладная математика', 'seats': 40},
        'IVT': {'name': 'Информатика и вычислительная техника', 'seats': 50},
        'ITSS': {'name': 'Инфокоммуникационные технологии и системы связи', 'seats': 30},
        'IB': {'name': 'Информационная безопасность', 'seats': 20}
    }
    
    # Define applicant counts per date and program (from spec Table 8)
    applicant_counts = {
        '2023-08-01': {'PM': 60, 'IVT': 100, 'ITSS': 50, 'IB': 70},
        '2023-08-02': {'PM': 380, 'IVT': 370, 'ITSS': 350, 'IB': 260},
        '2023-08-03': {'PM': 1000, 'IVT': 1150, 'ITSS': 1050, 'IB': 800},
        '2023-08-04': {'PM': 1240, 'IVT': 1390, 'ITSS': 1240, 'IB': 1190}
    }
    
    # Define intersection counts for pairs of programs (from spec Table 9)
    pair_intersections = {
        '2023-08-01': {
            ('PM', 'IVT'): 22, ('PM', 'ITSS'): 17, ('PM', 'IB'): 20,
            ('IVT', 'ITSS'): 19, ('IVT', 'IB'): 22, ('ITSS', 'IB'): 17
        },
        '2023-08-02': {
            ('PM', 'IVT'): 190, ('PM', 'ITSS'): 190, ('PM', 'IB'): 150,
            ('IVT', 'ITSS'): 190, ('IVT', 'IB'): 140, ('ITSS', 'IB'): 120
        },
        '2023-08-03': {
            ('PM', 'IVT'): 760, ('PM', 'ITSS'): 600, ('PM', 'IB'): 410,
            ('IVT', 'ITSS'): 750, ('IVT', 'IB'): 460, ('ITSS', 'IB'): 500
        },
        '2023-08-04': {
            ('PM', 'IVT'): 1090, ('PM', 'ITSS'): 1110, ('PM', 'IB'): 1070,
            ('IVT', 'ITSS'): 1050, ('IVT', 'IB'): 1040, ('ITSS', 'IB'): 1090
        }
    }
    
    # Define intersection counts for triple/four programs (from spec Table 10)
    triple_four_intersections = {
        '2023-08-01': {
            ('PM', 'IVT', 'ITSS'): 5, ('PM', 'IVT', 'IB'): 5,
            ('IVT', 'ITSS', 'IB'): 5, ('PM', 'ITSS', 'IB'): 5,
            ('PM', 'IVT', 'ITSS', 'IB'): 3
        },
        '2023-08-02': {
            ('PM', 'IVT', 'ITSS'): 70, ('PM', 'IVT', 'IB'): 70,
            ('IVT', 'ITSS', 'IB'): 70, ('PM', 'ITSS', 'IB'): 70,
            ('PM', 'IVT', 'ITSS', 'IB'): 50
        },
        '2023-08-03': {
            ('PM', 'IVT', 'ITSS'): 500, ('PM', 'IVT', 'IB'): 260,
            ('IVT', 'ITSS', 'IB'): 300, ('PM', 'ITSS', 'IB'): 250,
            ('PM', 'IVT', 'ITSS', 'IB'): 200
        },
        '2023-08-04': {
            ('PM', 'IVT', 'ITSS'): 1020, ('PM', 'IVT', 'IB'): 1020,
            ('IVT', 'ITSS', 'IB'): 1000, ('PM', 'ITSS', 'IB'): 1040,
            ('PM', 'IVT', 'ITSS', 'IB'): 1000
        }
    }
    
    # Convert target date to string for lookup
    date_str = target_date.strftime('%Y-%m-%d')
    
    if date_str not in applicant_counts:
        # Use defaults if date not in spec
        date_str = '2023-08-01'
    
    # Get counts for this date
    counts = applicant_counts[date_str]
    pair_int = pair_intersections.get(date_str, {})
    triple_four_int = triple_four_intersections.get(date_str, {})
    
    # Generate unique applicant IDs
    total_applicants = sum(counts.values())
    applicant_ids = list(range(1, total_applicants + 1))
    
    # Create base dataframes for each program
    all_data = []
    
    # Start with triple/four-way intersections to ensure proper overlap
    processed_applicants = set()
    
    # Handle 4-program intersections
    if ('PM', 'IVT', 'ITSS', 'IB') in triple_four_int:
        count = triple_four_int[('PM', 'IVT', 'ITSS', 'IB')]
        selected_ids = random.sample(applicant_ids, min(count, len(applicant_ids)))
        for aid in selected_ids[:count]:
            if aid in processed_applicants:
                continue
            # Add this applicant to all 4 programs
            for prog in ['PM', 'IVT', 'ITSS', 'IB']:
                all_data.append(create_applicant_record(aid, prog, target_date))
            processed_applicants.add(aid)
    
    # Handle 3-program intersections
    for progs, count in triple_four_int.items():
        if len(progs) == 3:  # Three-way intersection
            selected_ids = random.sample(applicant_ids, min(count, len(applicant_ids)))
            for aid in selected_ids:
                if aid in processed_applicants:
                    continue
                # Add this applicant to these 3 programs
                for prog in progs:
                    all_data.append(create_applicant_record(aid, prog, target_date))
                processed_applicants.add(aid)
    
    # Handle 2-program intersections
    for progs, count in pair_int.items():
        if len(progs) == 2:  # Two-way intersection
            selected_ids = random.sample(applicant_ids, min(count, len(applicant_ids)))
            for aid in selected_ids:
                if aid in processed_applicants:
                    continue
                # Add this applicant to these 2 programs
                for prog in progs:
                    all_data.append(create_applicant_record(aid, prog, target_date))
                processed_applicants.add(aid)
    
    # Now fill remaining spots for each program
    for prog, needed_count in counts.items():
        current_prog_count = len([d for d in all_data if d['educational_program'] == prog])
        still_needed = needed_count - current_prog_count
        
        if still_needed > 0:
            available_ids = [aid for aid in applicant_ids if aid not in processed_applicants]
            selected_ids = random.sample(available_ids, min(still_needed, len(available_ids)))
            
            for aid in selected_ids:
                all_data.append(create_applicant_record(aid, prog, target_date))
                processed_applicants.add(aid)
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    
    # Ensure we have the right structure as specified in spec Section 7
    required_columns = [
        'applicant_id', 'consent_given', 'priority_op', 'physics_ikt',
        'russian_lang', 'math', 'individual_achievements', 'total_score', 'educational_program'
    ]
    
    # Make sure all required columns exist
    for col in required_columns:
        if col not in df.columns:
            if col == 'consent_given':
                df[col] = [random.choice([True, False]) for _ in range(len(df))]
            elif col == 'priority_op':
                df[col] = [random.randint(1, 4) for _ in range(len(df))]
            elif col in ['physics_ikt', 'russian_lang', 'math', 'individual_achievements']:
                # Generate realistic scores
                if col == 'physics_ikt':
                    df[col] = [random.randint(0, 100) for _ in range(len(df))]
                elif col == 'russian_lang':
                    df[col] = [random.randint(0, 100) for _ in range(len(df))]
                elif col == 'math':
                    df[col] = [random.randint(0, 100) for _ in range(len(df))]
                else:  # individual_achievements
                    df[col] = [random.randint(0, 10) for _ in range(len(df))]
            elif col == 'total_score':
                df[col] = df['physics_ikt'] + df['russian_lang'] + df['math'] + df['individual_achievements']
            elif col == 'educational_program':
                # Already handled above
                pass
            elif col == 'applicant_id':
                # Already handled above
                pass
    
    return df


def create_applicant_record(applicant_id, program, date):
    """
    Create a single applicant record with realistic data
    """
    # Generate random scores
    physics_ikt = random.randint(0, 100)
    russian_lang = random.randint(0, 100)
    math = random.randint(0, 100)
    individual_achievements = random.randint(0, 10)
    total_score = physics_ikt + russian_lang + math + individual_achievements
    
    # Randomly assign priority (1-4) and consent status
    priority = random.randint(1, 4)
    consent = random.choice([True, False])
    
    return {
        'applicant_id': applicant_id,
        'consent_given': consent,
        'priority_op': priority,
        'physics_ikt': physics_ikt,
        'russian_lang': russian_lang,
        'math': math,
        'individual_achievements': individual_achievements,
        'total_score': total_score,
        'educational_program': program,
        'date_added': date
    }


def initialize_educational_programs(db):
    """
    Initialize educational programs in the database
    """
    programs_info = [
        {'code': 'PM', 'name': 'Прикладная математика', 'budget_places': 40},
        {'code': 'IVT', 'name': 'Информатика и вычислительная техника', 'budget_places': 50},
        {'code': 'ITSS', 'name': 'Инфокоммуникационные технологии и системы связи', 'budget_places': 30},
        {'code': 'IB', 'name': 'Информационная безопасность', 'budget_places': 20}
    ]
    
    for prog_info in programs_info:
        existing = EducationalProgram.query.filter_by(code=prog_info['code']).first()
        if not existing:
            program = EducationalProgram(**prog_info)
            db.session.add(program)
    
    db.session.commit()


def load_sample_data():
    """
    Load sample data from CSV files for demonstration
    """
    import os
    from pathlib import Path
    
    # Base directory for sample data
    base_path = Path(__file__).parent.parent.parent / 'sample_data'
    
    # Define educational programs and dates
    programs = ['pm', 'ivt', 'itss']  # Using only the programs mentioned in the problem statement
    dates = ['01', '02', '03', '04']  # August 1-4
    
    records_loaded = 0
    
    # Load data for each program and date combination
    for program in programs:
        for date in dates:
            csv_file = base_path / f"{program}_{date}.csv"
            if csv_file.exists():
                # Read the CSV file
                df = pd.read_csv(csv_file)
                
                # Ensure the dataframe has the required columns
                required_columns = [
                    'applicant_id', 'consent_given', 'priority_op', 'physics_ikt',
                    'russian_lang', 'math', 'individual_achievements', 'total_score', 'educational_program'
                ]
                
                # Add educational_program column if it doesn't exist
                if 'educational_program' not in df.columns:
                    df['educational_program'] = program.upper()
                
                # Add date information
                from datetime import datetime
                target_date = datetime.strptime(f"2023-08-{date}", "%Y-%m-%d").date()
                
                # Add the data to the database via the controller's save function
                from ..controllers.main_controller import save_admission_data
                save_admission_data(df)
                
                records_loaded += len(df)
    
    return f"Loaded {records_loaded} records from sample data files"