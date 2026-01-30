"""
Script to initialize the database and create tables
"""
import os
from app.models import db, EducationalProgram
from app.main import create_app
from app.utils.data_generator import initialize_educational_programs


def init_database():
    """Initialize the database with tables and initial data"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Initialize educational programs
        initialize_educational_programs(db)
        
        print("Database initialized successfully!")
        print("Tables created:")
        print("- Applicant")
        print("- EducationalProgram") 
        print("- AdmissionData")
        print("\nEducational programs initialized:")
        programs = EducationalProgram.query.all()
        for prog in programs:
            print(f"- {prog.code}: {prog.name} ({prog.budget_places} places)")


if __name__ == "__main__":
    init_database()