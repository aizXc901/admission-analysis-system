"""
Main controller for the Admission Analysis System
"""
from flask import render_template, request, jsonify, send_file
from ..models import db, Applicant, EducationalProgram, AdmissionData
from ..utils.data_generator import generate_admission_data
from ..utils.calculator import calculate_passing_scores
from ..utils.report_generator import generate_pdf_report
from datetime import datetime, date
import pandas as pd
import json


from flask import Blueprint
bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Main page displaying admission data visualization"""
    # Get all educational programs
    programs = EducationalProgram.query.all()
    
    # Get latest admission data
    today = date.today()
    latest_data = AdmissionData.query.filter_by(date=today).all()
    
    return render_template('index.html', programs=programs, data=latest_data)


@bp.route('/upload', methods=['POST'])
def upload_data():
    """Upload admission data from external sources"""
    try:
        # Handle file upload
        uploaded_file = request.files.get('file')
        
        if uploaded_file and uploaded_file.filename.endswith(('.xlsx', '.csv')):
            # Process the uploaded file
            if uploaded_file.filename.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file)
            
            # Save data to database
            save_admission_data(df)
            
            return jsonify({'status': 'success', 'message': 'Data uploaded successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid file format'}), 400
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@bp.route('/update_database', methods=['POST'])
def update_database():
    """Update database with new admission data, following the rules:
    - Remove applicants not present in new data
    - Add new applicants
    - Update existing applicants
    """
    try:
        # Get date and new data from request
        req_data = request.json
        target_date = datetime.strptime(req_data['date'], '%Y-%m-%d').date()
        new_data = req_data['data']
        
        # Get current data for this date
        current_data = {item.applicant_id: item for item in 
                       AdmissionData.query.filter_by(date=target_date).all()}
        
        # Process updates/additions
        for applicant_data in new_data:
            applicant_id = applicant_data['applicant_id']
            
            if applicant_id in current_data:
                # Update existing applicant
                applicant_record = current_data[applicant_id]
                applicant_record.consent_given = applicant_data['consent_given']
                applicant_record.priority_op = applicant_data['priority_op']
                applicant_record.physics_ikt = applicant_data['physics_ikt']
                applicant_record.russian_lang = applicant_data['russian_lang']
                applicant_record.math = applicant_data['math']
                applicant_record.individual_achievements = applicant_data['individual_achievements']
                applicant_record.total_score = applicant_data['total_score']
                applicant_record.educational_program = applicant_data['educational_program']
            else:
                # Add new applicant
                new_admission = AdmissionData(
                    date=target_date,
                    applicant_id=applicant_id,
                    educational_program=applicant_data['educational_program'],
                    consent_given=applicant_data['consent_given'],
                    priority_op=applicant_data['priority_op'],
                    physics_ikt=applicant_data['physics_ikt'],
                    russian_lang=applicant_data['russian_lang'],
                    math=applicant_data['math'],
                    individual_achievements=applicant_data['individual_achievements'],
                    total_score=applicant_data['total_score']
                )
                db.session.add(new_admission)
        
        # Identify and remove applicants not in new data
        new_applicant_ids = {item['applicant_id'] for item in new_data}
        for applicant_id, record in current_data.items():
            if applicant_id not in new_applicant_ids:
                db.session.delete(record)
        
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Database updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@bp.route('/passing_scores')
def get_passing_scores():
    """Calculate and return passing scores for all educational programs"""
    try:
        # Get date parameter, default to today
        date_str = request.args.get('date')
        if date_str:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            target_date = date.today()
        
        # Calculate passing scores
        scores = calculate_passing_scores(target_date)
        
        return jsonify({
            'date': target_date.isoformat(),
            'scores': scores
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@bp.route('/api/applicants')
def get_applicants():
    """API endpoint to get filtered applicants data"""
    try:
        # Get filter parameters
        date_str = request.args.get('date', '')
        program = request.args.get('program', '')
        priority = request.args.get('priority', '')
        consent = request.args.get('consent', '')
        
        # Parse date
        if date_str:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            target_date = date.today()
        
        # Build query
        query = AdmissionData.query.filter(AdmissionData.date == target_date)
        
        if program:
            query = query.filter(AdmissionData.educational_program == program)
        
        if priority:
            query = query.filter(AdmissionData.priority_op == int(priority))
        
        if consent == 'true':
            query = query.filter(AdmissionData.consent_given == True)
        
        applicants = query.order_by(AdmissionData.total_score.desc()).all()
        
        # Convert to JSON-serializable format
        applicants_data = []
        for applicant in applicants:
            applicants_data.append({
                'id': applicant.id,
                'applicant_id': applicant.applicant_id,
                'educational_program': applicant.educational_program,
                'priority_op': applicant.priority_op,
                'consent_given': applicant.consent_given,
                'physics_ikt': applicant.physics_ikt,
                'russian_lang': applicant.russian_lang,
                'math': applicant.math,
                'individual_achievements': applicant.individual_achievements,
                'total_score': applicant.total_score
            })
        
        return jsonify({'applicants': applicants_data})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@bp.route('/api/stats')
def get_stats():
    """API endpoint to get statistics data"""
    try:
        date_str = request.args.get('date', '')
        if date_str:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            target_date = date.today()
        
        # Get all educational programs
        programs = EducationalProgram.query.all()
        
        # Calculate passing scores
        passing_scores = calculate_passing_scores(target_date)
        
        # Prepare stats data
        stats_data = []
        for program in programs:
            # Get all applicants for this program on the target date
            all_applicants = AdmissionData.query.filter(
                AdmissionData.date == target_date,
                AdmissionData.educational_program == program.code
            ).count()
            
            # Get applicants with consent for this program
            consent_applicants = AdmissionData.query.filter(
                AdmissionData.date == target_date,
                AdmissionData.educational_program == program.code,
                AdmissionData.consent_given == True
            ).count()
            
            stats_data.append({
                'code': program.code,
                'program_name': program.name,
                'places': program.budget_places,
                'applications': all_applicants,
                'with_consent': consent_applicants,
                'passing_score': passing_scores[program.code]['score'] if program.code in passing_scores else 'Н/Д'
            })
        
        return jsonify({'stats': stats_data})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@bp.route('/generate_report', methods=['POST'])
def generate_report():
    """Generate PDF report with admission statistics"""
    try:
        req_data = request.json
        report_date = datetime.strptime(req_data.get('date', ''), '%Y-%m-%d').date() if req_data.get('date') else date.today()
        
        # Generate the report
        report_path = generate_pdf_report(report_date)
        
        return send_file(report_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


def save_admission_data(df):
    """Save admission data from DataFrame to database"""
    for _, row in df.iterrows():
        # Check if applicant exists
        existing_applicant = Applicant.query.filter_by(applicant_id=row['applicant_id']).first()
        
        if not existing_applicant:
            # Create new applicant
            applicant = Applicant(
                applicant_id=row['applicant_id'],
                date_added=date.today(),
                consent_given=row['consent_given'],
                priority_op=row['priority_op'],
                physics_ikt=row['physics_ikt'],
                russian_lang=row['russian_lang'],
                math=row['math'],
                individual_achievements=row['individual_achievements'],
                total_score=row['total_score'],
                educational_program=row['educational_program']
            )
            db.session.add(applicant)
        else:
            # Update existing applicant
            existing_applicant.consent_given = row['consent_given']
            existing_applicant.priority_op = row['priority_op']
            existing_applicant.physics_ikt = row['physics_ikt']
            existing_applicant.russian_lang = row['russian_lang']
            existing_applicant.math = row['math']
            existing_applicant.individual_achievements = row['individual_achievements']
            existing_applicant.total_score = row['total_score']
            existing_applicant.educational_program = row['educational_program']
    
    db.session.commit()


@bp.route('/load_sample_data', methods=['POST'])
def load_sample_data():
    """Load sample data from CSV files for demonstration"""
    try:
        from ..utils.data_generator import load_sample_data
        result = load_sample_data()
        
        return jsonify({'status': 'success', 'message': f'Sample data loaded: {result}'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500