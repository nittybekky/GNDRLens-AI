# app/models/analysis.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from datetime import datetime
from .base import Base
import json

class Analysis(Base):
    __tablename__ = 'analyses'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    analysis_type = Column(String(50), nullable=False)  # e.g., "gender_equity"
    results = Column(JSON, nullable=False)  # Store complete analysis results
    context = Column(JSON, nullable=True)  # Store analysis context
    industry = Column(String(50), nullable=True)
    language = Column(String(10), nullable=True)
    location = Column(String(100), nullable=True)
    
    # Derived metrics for querying and filtering
    equity_score = Column(Float, nullable=True)
    violence_prevention_score = Column(Float, nullable=True)
    care_support_score = Column(Float, nullable=True)
    policy_implementation_score = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.results:
            self._extract_scores()

    def _extract_scores(self):
        """Extract key scores from analysis results for querying"""
        if isinstance(self.results, str):
            results = json.loads(self.results)
        else:
            results = self.results

        self.equity_score = results.get('overall_assessment', {}).get('equity_score')
        
        if 'industry_context' in results:
            industry_context = results['industry_context']
            self.violence_prevention_score = industry_context.get('violence_prevention', {}).get('benchmark_comparison', {}).get('current_score')
            self.care_support_score = industry_context.get('unpaid_care', {}).get('benchmark_comparison', {}).get('current_score')
            self.policy_implementation_score = industry_context.get('policy_effectiveness', {}).get('benchmark_comparison', {}).get('current_score')
