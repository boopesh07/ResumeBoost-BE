from sqlalchemy import Column, String, Text
from . import db

class CoverLetterStatistic(db.Model):
    __tablename__ = 'cover_letter_statistics'
    id = Column(String, primary_key=True)
    input_resume = Column(Text, nullable=False)
    input_job_description = Column(Text, nullable=False)
    cover_letter = Column(Text, nullable=False)
