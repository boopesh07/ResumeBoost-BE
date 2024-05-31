from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Text

db = SQLAlchemy()

class ResumeBoostStatistic(db.Model):
    __tablename__ = 'resume_boost_statistics'
    id = Column(String, primary_key=True)
    input_resume = Column(Text, nullable=False)
    input_job_description = Column(Text, nullable=False)
    tailored_resume = Column(Text, nullable=False)
    keywords_inserted = Column(Text, nullable=False)
    score_improvement = Column(String, nullable=False)
    project_suggestions = Column(Text, nullable=False)
