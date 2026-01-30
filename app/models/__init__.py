"""
Database models for the Admission Analysis System
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Applicant(db.Model):
    """
    Model representing an applicant
    """
    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, nullable=False)  # Unique identifier
    date_added = db.Column(db.Date, nullable=False)  # Date when record was added
    consent_given = db.Column(db.Boolean, default=False)  # Agreement to enrollment
    priority_op = db.Column(db.Integer, nullable=False)  # Priority of educational program (1-4)
    physics_ikt = db.Column(db.Integer, default=0)  # Physics/ICT score
    russian_lang = db.Column(db.Integer, default=0)  # Russian language score
    math = db.Column(db.Integer, default=0)  # Math score
    individual_achievements = db.Column(db.Integer, default=0)  # Individual achievements score
    total_score = db.Column(db.Integer, nullable=False)  # Sum of all scores
    educational_program = db.Column(db.String(50), nullable=False)  # Educational program code (PM, IVT, ITSS, IB)


class EducationalProgram(db.Model):
    """
    Model representing an educational program
    """
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)  # PM, IVT, ITSS, IB
    name = db.Column(db.String(100), nullable=False)  # Full name
    budget_places = db.Column(db.Integer, nullable=False)  # Number of budget places


class AdmissionData(db.Model):
    """
    Model to store admission data snapshots by date
    """
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicant.applicant_id'), nullable=False)
    educational_program = db.Column(db.String(50), nullable=False)
    consent_given = db.Column(db.Boolean, default=False)
    priority_op = db.Column(db.Integer, nullable=False)
    physics_ikt = db.Column(db.Integer, default=0)
    russian_lang = db.Column(db.Integer, default=0)
    math = db.Column(db.Integer, default=0)
    individual_achievements = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    applicant = db.relationship('Applicant', backref=db.backref('admission_data', lazy=True))