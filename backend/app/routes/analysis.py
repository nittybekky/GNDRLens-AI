from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from ..models.base import get_db
from ..models.analysis import Analysis
from ..services.analysis_service import AnalysisService
from datetime import datetime, timedelta

router = APIRouter()
analysis_service = AnalysisService()

@router.post("/analyze")
async def analyze_text_route(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        data = await request.json()
        text = data.get("content")
        # Required fields
        if not text:
            raise HTTPException(status_code=400, detail="Text content is required")
            
        # Optional fields
        context = {
            'industry': data.get('industry'),
            'language': data.get('language'),
            'location': data.get('location'),
            'additional_context': data.get('context', {})
        }
        
        # Perform analysis
        analysis_result = await analysis_service.analyze_content(
            text=text,
            context=context,
            industry=context['industry'],
            db=db
        )
        
        print("Model response:", analysis_result)
        return {
            "status": "success",
            "data": analysis_result
        }
        
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/metrics")
async def get_metrics(
    db: Session = Depends(get_db),
    days: int = Query(default=30, ge=1, le=365),
    industry: Optional[str] = None
):
    try:
        # Base query
        query = db.query(Analysis).filter(
            Analysis.created_at >= datetime.utcnow() - timedelta(days=days)
        )
        
        # Apply industry filter if specified
        if industry:
            query = query.filter(Analysis.industry == industry)
        
        # Aggregate metrics
        metrics = db.query(
            func.avg(Analysis.equity_score).label('avg_equity_score'),
            func.avg(Analysis.violence_prevention_score).label('avg_violence_score'),
            func.avg(Analysis.care_support_score).label('avg_care_score'),
            func.avg(Analysis.policy_implementation_score).label('avg_policy_score'),
            func.count().label('total_analyses')
        ).filter(
            Analysis.created_at >= datetime.utcnow() - timedelta(days=days)
        )
        
        if industry:
            metrics = metrics.filter(Analysis.industry == industry)
            
        metrics = metrics.first()
        
        # Get trend data
        trend_data = db.query(
            func.date(Analysis.created_at).label('date'),
            func.avg(Analysis.equity_score).label('equity_score'),
            func.count().label('analysis_count')
        ).filter(
            Analysis.created_at >= datetime.utcnow() - timedelta(days=days)
        )
        
        if industry:
            trend_data = trend_data.filter(Analysis.industry == industry)
            
        trend_data = trend_data.group_by(
            func.date(Analysis.created_at)
        ).all()
        
        return {
            "metrics": {
                "average_equity_score": float(metrics.avg_equity_score) if metrics.avg_equity_score else 0,
                "average_violence_prevention_score": float(metrics.avg_violence_score) if metrics.avg_violence_score else 0,
                "average_care_support_score": float(metrics.avg_care_score) if metrics.avg_care_score else 0,
                "average_policy_score": float(metrics.avg_policy_score) if metrics.avg_policy_score else 0,
                "total_analyses": metrics.total_analyses
            },
            "trend_data": [
                {
                    "date": str(t.date),
                    "equity_score": float(t.equity_score) if t.equity_score else 0,
                    "analysis_count": t.analysis_count
                }
                for t in trend_data
            ]
        }
        
    except Exception as e:
        print(f"Metrics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve metrics: {str(e)}")