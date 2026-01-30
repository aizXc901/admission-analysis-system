"""
Utility module for calculating passing scores based on admission data
"""
from ..models import db, Applicant, EducationalProgram, AdmissionData
from datetime import datetime, date


def calculate_passing_scores(target_date):
    """
    Calculate passing scores for all educational programs based on the algorithm:
    - Only consider applicants who gave consent for enrollment
    - Consider priorities (1-4) when determining who gets accepted
    - Account for movement between programs based on priorities
    """
    programs = EducationalProgram.query.all()
    scores = {}
    
    for program in programs:
        # Get all applicants for this program on the target date who gave consent
        applicants = db.session.query(AdmissionData).filter(
            AdmissionData.date == target_date,
            AdmissionData.educational_program == program.code,
            AdmissionData.consent_given == True
        ).order_by(AdmissionData.total_score.desc()).all()
        
        # If there are fewer applicants than seats, return 'НЕДОБОР' (Shortage)
        if len(applicants) <= program.budget_places:
            scores[program.code] = {
                'score': 'НЕДОБОР',
                'places_available': program.budget_places,
                'applicants_count': len(applicants),
                'accepted_count': len(applicants)
            }
        else:
            # Get the score of the last person who gets accepted (the passing score)
            passing_applicant = applicants[program.budget_places - 1]
            next_applicant = applicants[program.budget_places] if program.budget_places < len(applicants) else None
            
            scores[program.code] = {
                'score': passing_applicant.total_score,
                'places_available': program.budget_places,
                'applicants_count': len(applicants),
                'accepted_count': program.budget_places,
                'next_score': next_applicant.total_score if next_applicant else None
            }
    
    # More complex algorithm considering priorities and cross-program movements
    # This handles situations where applicants apply to multiple programs with different priorities
    final_scores = calculate_advanced_passing_scores(target_date)
    
    # Merge the results - use advanced calculation where possible
    for prog_code, advanced_result in final_scores.items():
        if advanced_result['score'] != 'НЕДОБОР':
            scores[prog_code] = advanced_result
    
    return scores


def calculate_advanced_passing_scores(target_date):
    """
    Advanced calculation considering priorities and multi-program applications
    """
    programs = EducationalProgram.query.all()
    program_seats = {prog.code: prog.budget_places for prog in programs}
    
    # Get all applicants for all programs on the target date who gave consent
    all_applicants = db.session.query(AdmissionData).filter(
        AdmissionData.date == target_date,
        AdmissionData.consent_given == True
    ).order_by(AdmissionData.total_score.desc()).all()
    
    # Group applicants by applicant_id to handle those applying to multiple programs
    applicants_by_id = {}
    for app in all_applicants:
        if app.applicant_id not in applicants_by_id:
            applicants_by_id[app.applicant_id] = []
        applicants_by_id[app.applicant_id].append(app)
    
    # Track which programs have filled seats
    filled_seats = {prog_code: 0 for prog_code in program_seats.keys()}
    accepted_applicants = {prog_code: [] for prog_code in program_seats.keys()}
    
    # Sort applicants by total score descending, then by priority ascending
    all_sorted_applicants = sorted(all_applicants, key=lambda x: (-x.total_score, x.priority_op))
    
    # Assign applicants to programs based on their preferences and scores
    for app in all_sorted_applicants:
        # Find the highest priority program this applicant hasn't been assigned to yet
        # among their applied programs
        eligible_programs = [a.educational_program for a in applicants_by_id[app.applicant_id]]
        
        assigned = False
        for prog_code in sorted(eligible_programs, 
                                key=lambda p: min(a.priority_op for a in applicants_by_id[app.applicant_id] 
                                                if a.educational_program == p)):
            if filled_seats[prog_code] < program_seats[prog_code]:
                accepted_applicants[prog_code].append(app)
                filled_seats[prog_code] += 1
                assigned = True
                break  # Applicant assigned to one program only
        
        if not assigned:
            # Applicant didn't get into any of their preferred programs
            continue
    
    # Calculate final scores
    scores = {}
    for prog in programs:
        if len(accepted_applicants[prog.code]) == 0:
            scores[prog.code] = {
                'score': 'НЕДОБОР',
                'places_available': prog.budget_places,
                'applicants_count_with_consent': len([a for a in all_applicants if a.educational_program == prog.code and a.consent_given]),
                'accepted_count': 0
            }
        elif len(accepted_applicants[prog.code]) < prog.budget_places:
            scores[prog.code] = {
                'score': 'НЕДОБОР',
                'places_available': prog.budget_places,
                'applicants_count_with_consent': len([a for a in all_applicants if a.educational_program == prog.code and a.consent_given]),
                'accepted_count': len(accepted_applicants[prog.code])
            }
        else:
            # Passing score is the score of the last accepted applicant
            last_accepted = accepted_applicants[prog.code][-1]
            scores[prog.code] = {
                'score': last_accepted.total_score,
                'places_available': prog.budget_places,
                'applicants_count_with_consent': len([a for a in all_applicants if a.educational_program == prog.code and a.consent_given]),
                'accepted_count': len(accepted_applicants[prog.code]),
                'highest_score': max((a.total_score for a in accepted_applicants[prog.code]), default=0),
                'lowest_score': last_accepted.total_score
            }
    
    return scores


def get_statistics_for_date(target_date):
    """
    Get comprehensive statistics for a specific date
    """
    programs = EducationalProgram.query.all()
    stats = {}
    
    for program in programs:
        # All applicants for this program
        all_applicants = db.session.query(AdmissionData).filter(
            AdmissionData.date == target_date,
            AdmissionData.educational_program == program.code
        ).all()
        
        # Applicants with consent
        consent_applicants = [a for a in all_applicants if a.consent_given]
        
        # Count by priority
        priority_counts = {1: 0, 2: 0, 3: 0, 4: 0}
        for app in all_applicants:
            if 1 <= app.priority_op <= 4:
                priority_counts[app.priority_op] += 1
        
        # Accepted applicants (based on passing score algorithm)
        passing_scores = calculate_passing_scores(target_date)
        accepted_count = passing_scores[program.code]['accepted_count'] if passing_scores[program.code]['score'] != 'НЕДОБОР' else len(consent_applicants)
        
        # Accepted by priority
        accepted_by_priority = {1: 0, 2: 0, 3: 0, 4: 0}
        if passing_scores[program.code]['score'] != 'НЕДОБОР':
            # Need to implement the logic to determine which accepted applicants had which priority
            # For now, we'll calculate based on the advanced algorithm
            advanced_results = calculate_advanced_passing_scores(target_date)
            if program.code in advanced_results:
                accepted_apps = advanced_results[program.code].get('accepted_applicants', [])
                for app in accepted_apps:
                    if 1 <= app.priority_op <= 4:
                        accepted_by_priority[app.priority_op] += 1
        
        stats[program.code] = {
            'program_name': program.name,
            'total_applications': len(all_applicants),
            'budget_places': program.budget_places,
            'applications_by_priority': priority_counts,
            'applications_with_consent': len(consent_applicants),
            'accepted_total': accepted_count,
            'accepted_by_priority': accepted_by_priority
        }
    
    return stats