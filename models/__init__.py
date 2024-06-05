from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .resume_stat import ResumeBoostStatistic
from .cover_letter_stat import CoverLetterStatistic
