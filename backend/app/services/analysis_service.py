import google.generativeai as genai
from google.cloud import translate_v2 as translate
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
import json, re, os
import requests
from dotenv import load_dotenv
from ..models.analysis import Analysis

class AnalysisService:
    def __init__(self):
        try:
            load_dotenv()
            script_dir = os.path.dirname(os.path.abspath(__file__))
            script_dir = os.path.dirname(os.path.abspath(__file__))
            credentials_path = os.path.join(script_dir, os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

            api_key = os.getenv("GOOGLE_API_KEY")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.translate_client = translate.Client()
            
            # Load gender-specific context databases
            self.gender_terms = self._load_gender_terms()
            self.industry_benchmarks = self._load_industry_benchmarks()
            self.violence_indicators = self._load_violence_indicators()
            self.care_work_metrics = self._load_care_work_metrics()
            self.policy_frameworks = self._load_policy_frameworks()
        except Exception as e:
            print(f"Error initializing services: {e}")
            raise


    def detect_language(self, text: str) -> str:
        """Detect the language of the provided text."""
        result = self.translate_client.detect_language(text)
        return result["language"]

    def get_user_location(self) -> str:
        """Detect the user's approximate location based on their IP address."""
        try:
            response = requests.get("https://ipinfo.io")
            if response.status_code == 200:
                data = response.json()
                return data.get("country", "global")
        except Exception as e:
            print(f"Location detection failed: {e}")
        return "global"

    def translate_text(self, text: str, target_language: str) -> str:
        """Translate text to the specified target language."""
        translation = self.translate_client.translate(text, target_language=target_language)
        return translation["translatedText"]
    
    def _load_gender_terms(self) -> Dict:
        """Load database of gender-related terms and their contexts"""
        return {
             "explicit_bias": [
                "women can't", "girls shouldn't", "male-only", "feminine weakness",
                "maternal risk", "emotional decision", "bossy woman", "hysteric"
            ],
            "implicit_bias": [
                "nurturing role", "support position", "office mom", "aggressive for a woman",
                "ambitious woman", "work-life balance", "family responsibilities"
            ],
            "violence_related": [
                "threatening", "intimidating", "controlling", "coercive",
                "hostile", "aggressive", "retaliatory", "punitive"
            ],
            "care_work_related": [
                "childcare duties", "eldercare responsibilities", "domestic duties",
                "household management", "family obligations", "caretaking role"
            ],
            "inclusive_alternatives": {
                "chairman": "chairperson",
                "businessman": "business person",
                "policeman": "police officer",
                "mankind": "humanity",
                "manpower": "workforce"
            },
            "empowerment_terms": [
                "leadership", "achievement", "expertise", "professional growth",
                "equal opportunity", "mentorship", "advancement"
            ]
        }

    
    def _load_violence_indicators(self) -> Dict:
        """Load comprehensive violence and harassment indicators"""
        return {
            "physical_violence": [
                "physical threats", "intimidation", "unsafe conditions",
                "restricted movement", "physical isolation"
            ],
            "psychological_violence": [
                "verbal abuse", "gaslighting", "manipulation",
                "emotional abuse", "psychological manipulation"
            ],
            "economic_violence": [
                "financial control", "economic threats", "withholding resources",
                "salary discrimination", "promotion discrimination"
            ],
            "digital_violence": [
                "online harassment", "cyberstalking", "digital surveillance",
                "online threats", "privacy violations"
            ],
            "risk_factors": [
                "power imbalance", "isolation", "lack of support systems",
                "financial dependency", "fear of retaliation"
            ],
            "protective_factors": [
                "clear reporting mechanisms", "support networks",
                "financial independence", "strong policies",
                "accountability measures"
            ]
        }

    def _load_care_work_metrics(self) -> Dict:
        """Load metrics for analyzing unpaid care work impact"""
        return {
            "time_allocation": {
                "childcare_hours": 0,
                "eldercare_hours": 0,
                "household_maintenance": 0,
                "emotional_labor": 0
            },
            "workplace_policies": {
                "flexible_hours": False,
                "remote_work": False,
                "parental_leave": 0,
                "caregiving_support": False
            },
            "economic_impact": {
                "career_interruptions": 0,
                "promotion_delays": 0,
                "wage_penalties": 0,
                "retirement_impact": 0
            },
            "support_indicators": {
                "childcare_facilities": False,
                "eldercare_assistance": False,
                "domestic_help_allowance": False,
                "caregiver_networks": False
            }
        }

    def _load_policy_frameworks(self) -> Dict:
        """Load gender equity policy frameworks and recommendations"""
        return {
            "workplace_policies": {
                "recruitment": [
                    "blind recruitment processes",
                    "diverse interview panels",
                    "standardized evaluation criteria"
                ],
                "advancement": [
                    "transparent promotion criteria",
                    "leadership development programs",
                    "mentorship initiatives"
                ],
                "compensation": [
                    "pay equity audits",
                    "transparent salary bands",
                    "performance evaluation standardization"
                ]
            },
            "care_support_policies": {
                "leave_policies": [
                    "paid parental leave",
                    "flexible caregiving leave",
                    "sabbatical options"
                ],
                "workplace_flexibility": [
                    "flexible hours",
                    "remote work options",
                    "compressed work weeks"
                ],
                "support_services": [
                    "on-site childcare",
                    "eldercare referral services",
                    "caregiver support networks"
                ]
            },
            "safety_policies": {
                "prevention": [
                    "anti-harassment training",
                    "bystander intervention programs",
                    "climate surveys"
                ],
                "response": [
                    "reporting mechanisms",
                    "investigation procedures",
                    "victim support services"
                ],
                "accountability": [
                    "clear consequences",
                    "regular policy review",
                    "transparency reports"
                ]
            }
        }

    def _load_industry_benchmarks(self) -> Dict:
        """Load industry-specific gender equity benchmarks"""
        return {
            "tech": {
                "leadership_representation": 0.30,
                "pay_gap_threshold": 0.05,
                "promotion_rate_ratio": 1.0,
                "violence_prevention_score": 0.8,
                "care_support_score": 0.7,
                "policy_implementation_score": 0.75
            },
            "healthcare": {
                "leadership_representation": 0.40,
                "pay_gap_threshold": 0.03,
                "promotion_rate_ratio": 1.0,
                "violence_prevention_score": 0.9,
                "care_support_score": 0.8,
                "policy_implementation_score": 0.85
            }
        }

    async def analyze_content(
        self, 
        text: str, 
        context: Optional[Dict] = None,
        industry: Optional[str] = None,
        db: Session = None
    ) -> Dict:
        """
        Analyze content for gender equity issues with industry-specific context including violence prevention,
        care work recognition, and policy recommendations
        """
        # Detect language and translate if needed
        source_language = self.detect_language(text)
        analysis_text = text if source_language == 'en' else self.translate_text(text, 'en')
        
        # Generating our prompt
        prompt = self._generate_gender_equity_prompt(analysis_text, industry)
        
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config={
                    'temperature': 0.2,
                    'top_p': 0.9,
                    'top_k': 50,
                    'max_output_tokens': 2048,
                },
                safety_settings={
                    'HARASSMENT': 'BLOCK_NONE',
                    'HATE_SPEECH': 'BLOCK_NONE'
                }
            )

            # Parse and enhance response
            cleaned_response = re.sub(r'```(?:json)?\n?(.*?)\n?```|^(?:json|JSON)\s*', r'\1', response.text, flags=re.DOTALL).strip()
            analysis = json.loads(cleaned_response)
            enhanced_analysis = self._enhance_gender_analysis(analysis, industry)
            
            # We'll Store analysis if database session provided. As the app grows, we'll use the db
            if db:
                self._store_analysis(db, text, enhanced_analysis, context)
            
            return enhanced_analysis

        except Exception as e:
            print(f"Analysis failed: {str(e)}")
            return {"status": "error", "error": str(e)}

    def _generate_gender_equity_prompt(self, text: str, industry: Optional[str] = None) -> str:
        """Generate a gender equity focused prompt for Gemini"""
        industry_context = f"Industry Context: {industry.upper()} sector analysis" if industry else ""
        
        return f"""
        You are an advanced AI system specialized in gender equity analysis. Analyze the following text with special attention to gender-related issues, biases, violence prevention, unpaid care work, policy implications and opportunities for promoting equality.

        {industry_context}

        1. GENDER BIAS DETECTION
        - Identify explicit and implicit gender biases
        - Detect stereotypical language and assumptions
        - Flag discriminatory patterns in language
        - Identify missed opportunities for inclusion
        
        2. REPRESENTATION ANALYSIS
        - Analyze representation of women and girls
        - Assess power dynamics and agency
        - Evaluate visibility and voice
        
        3. WORKPLACE EQUITY ASSESSMENT
        - Identify barriers to advancement
        - Analyze leadership opportunity language
        - Detect pay equity issues
        - Assess work-life balance assumptions
        
        4. SAFETY AND DIGNITY
        - Flag potential harassment indicators
        - Identify undermining or diminishing language
        - Assess psychological safety implications
        
        5. EMPOWERMENT OPPORTUNITIES
        - Identify areas for strengthening agency
        - Flag mentorship and growth opportunities
        - Suggest inclusive alternatives

        6. VIOLENCE PREVENTION
        - Identify explicit and subtle forms of violence
        - Detect harassment risk indicators
        - Analyze power dynamics and vulnerabilities
        - Assess existing safety measures
        - Flag potential escalation patterns
        - Evaluate reporting and support mechanisms
        
        7. UNPAID CARE WORK 
        - Identify assumptions about care responsibilities
        - Analyze work-life balance implications
        - Assess recognition of unpaid work
        - Evaluate support for caregivers
        - Analyze career impact of care duties
        - Flag discriminatory patterns
        
        8. POLICY IMPLICATIONS 
        - Identify policy gaps and opportunities
        - Assess implementation effectiveness
        - Evaluate monitoring mechanisms
        - Analyze resource allocation
        - Flag enforcement challenges
        - Suggest policy improvements


        Text to analyze: {text}

        Please make response really detailed. Any metric that has a score should also have some backup details. If the text request does not qualify for any oof the issues we are analyzing, please say so instead of leaving them blank. There must always be priority actions for overall assessment. Respond ONLY in JSON format with the following structure:
        {{
            "bias_detection": {{
                "explicit_biases": [
                    {{
                        "bias": <specific bias>,
                        "context": <explanation>,
                        "impact": <potential harm>,
                        "suggestion": <improvement>
                    }}
                ],
                "implicit_biases": [<similar structure>],
                "stereotypes": [<similar structure>],
                "bias_score": <float 0-1>
            }},
            "representation_analysis": {{
                "visibility_score": <float 0-1>,
                "agency_score": <float 0-1>,
                "power_dynamics": [<specific observations>],
                "improvement_areas": [<specific suggestions>]
            }},
            "workplace_equity": {{
                "advancement_barriers": [<specific barriers>],
                "leadership_language": {{
                    "inclusive_score": <float 0-1>,
                    "flags": [<specific issues>]
                }},
                "pay_equity_flags": [<potential issues>],
                "work_life_assumptions": [<detected assumptions>]
            }},
            "safety_assessment": {{
                "harassment_indicators": [<potential flags>],
                "undermining_language": [<specific examples>],
                "psychological_safety": {{
                    "score": <float 0-1>,
                    "concerns": [<specific issues>]
                }}
            }},
            "empowerment_opportunities": {{
                "growth_language": [<positive examples>],
                "mentorship_opportunities": [<specific suggestions>],
                "inclusive_alternatives": [<specific improvements>]
            }},
            "violence_prevention": {{
                "risk_indicators": [
                    {{
                        "type": <violence type>,
                        "indicator": <specific flag>,
                        "context": <situation details>,
                        "severity": <"high", "medium", "low">,
                        "mitigation": <specific recommendation>
                    }}
                ],
                "safety_measures": {{
                    "existing": [<current measures>],
                    "gaps": [<missing measures>],
                    "recommendations": [<specific improvements>]
                }},
                "power_dynamics": {{
                    "risk_factors": [<specific factors>],
                    "protective_factors": [<existing protections>],
                    "improvements": [<recommended changes>]
                }},
                "overall_safety_score": <float 0-1>
            }},
            "unpaid_care_analysis": {{
                "care_responsibilities": [
                    {{
                        "type": <care type>,
                        "assumption": <specific assumption>,
                        "impact": <career/workplace effect>,
                        "support_needed": <specific support>
                    }}
                ],
                "work_life_measures": {{
                    "flexibility_score": <float 0-1>,
                    "support_score": <float 0-1>,
                    "gaps": [<specific gaps>],
                    "recommendations": [<specific improvements>]
                }},
                "economic_impact": {{
                    "career_progression": <impact assessment>,
                    "compensation_effects": [<specific effects>],
                    "mitigation_strategies": [<specific strategies>]
                }},
                "care_recognition_score": <float 0-1>
            }},
            "policy_recommendations": {{
                "current_policies": {{
                    "strengths": [<existing good policies>],
                    "weaknesses": [<policy gaps>],
                    "implementation_score": <float 0-1>
                }},
                "recommended_policies": [
                    {{
                        "focus_area": <specific area>,
                        "recommendation": <policy suggestion>,
                        "rationale": <justification>,
                        "implementation_steps": [<specific steps>],
                        "success_metrics": [<measurement criteria>],
                        "priority": <"high", "medium", "low">
                    }}
                ],
                "resource_implications": {{
                    "required_resources": [<specific needs>],
                    "potential_challenges": [<specific challenges>],
                    "mitigation_strategies": [<specific strategies>]
                }},
                "monitoring_framework": {{
                    "metrics": [<specific metrics>],
                    "data_needs": [<required data>],
                    "review_frequency": <recommended frequency>
                }}
            }},
            "overall_assessment": {{
                "equity_score": <float 0-1>,
                "priority_actions": [
                    {{
                        "issue": <specific issue>,
                        "impact": <potential harm>,
                        "recommendation": <specific suggestion>,
                        "priority": <"high", "medium", "low">
                    }}
                ]
            }}
        }}
        """

    def _enhance_gender_analysis(self, analysis: Dict, industry: Optional[str] = None) -> Dict:
        """Enhance the basic analysis with industry-specific insights"""
        if not industry or industry not in self.industry_benchmarks:
            return analysis
            
        benchmarks = self.industry_benchmarks[industry]
        
        # Add industry-specific context and recommendations
        analysis["industry_context"] = {
            "benchmarks": benchmarks,
            "gap_analysis": self._calculate_industry_gaps(analysis, benchmarks),
            "recommendations": self._generate_industry_recommendations(analysis, benchmarks),
            "violence_prevention": self._analyze_violence_prevention(analysis, benchmarks),
            "unpaid_care": self._analyze_care_work(analysis, benchmarks),
            "policy_effectiveness": self._analyze_policy_framework(analysis, benchmarks)
        }
        
        return analysis

    def _calculate_industry_gaps(self, analysis: Dict, benchmarks: Dict) -> Dict:
        """Calculate comprehensive gaps between current state and industry benchmarks"""
        return {
            "leadership_gaps": {
                "executive_gap": benchmarks["leadership_representation"]["executive_level"] - analysis.get("representation_analysis", {}).get("visibility_score", 0),
                "management_gap": benchmarks["leadership_representation"]["senior_management"] - analysis.get("representation_analysis", {}).get("agency_score", 0),
                "pipeline_gap": benchmarks["advancement_metrics"]["leadership_pipeline"] - analysis.get("workplace_equity", {}).get("leadership_language", {}).get("inclusive_score", 0)
            },
            "pay_equity_gaps": {
                "base_pay_gap": benchmarks["pay_equity"]["gap_threshold"],
                "bonus_gap": benchmarks["pay_equity"]["bonus_gap_threshold"],
                "promotion_gap": benchmarks["pay_equity"]["promotion_adjustment"]
            },
            "safety_gaps": {
                "prevention_gap": benchmarks["safety_metrics"]["violence_prevention_score"] - analysis.get("violence_prevention", {}).get("overall_safety_score", 0),
                "reporting_gap": benchmarks["safety_metrics"]["harassment_reporting_mechanism"] - analysis.get("safety_assessment", {}).get("psychological_safety", {}).get("score", 0),
                "response_gap": benchmarks["safety_metrics"]["response_effectiveness"] - analysis.get("violence_prevention", {}).get("overall_safety_score", 0)
            },
            "care_support_gaps": {
                "leave_gap": benchmarks["care_support"]["parental_leave_score"] - analysis.get("unpaid_care_analysis", {}).get("care_recognition_score", 0),
                "flexibility_gap": benchmarks["care_support"]["flexible_work_score"] - analysis.get("unpaid_care_analysis", {}).get("work_life_measures", {}).get("flexibility_score", 0),
                "support_gap": benchmarks["care_support"]["caregiving_support"] - analysis.get("unpaid_care_analysis", {}).get("work_life_measures", {}).get("support_score", 0)
            },
            "policy_gaps": {
                "implementation_gap": benchmarks["policy_implementation"]["overall_score"] - analysis.get("policy_recommendations", {}).get("current_policies", {}).get("implementation_score", 0),
                "accountability_gap": benchmarks["policy_implementation"]["accountability_measures"],
                "resource_gap": benchmarks["policy_implementation"]["resource_allocation"]
            }
        }
        

    def _generate_industry_recommendations(self, analysis: Dict, benchmarks: Dict) -> List[Dict]:
        """Generate comprehensive industry-specific recommendations based on analysis and benchmarks"""
        
        gaps = self._calculate_industry_gaps(analysis, benchmarks)
        recommendations = []
        
        # Leadership and Representation
        if gaps["leadership_gaps"]["executive_gap"] > 0.1:
            recommendations.append({
                "area": "leadership_representation",
                "priority": "high",
                "type": "structural",
                "recommendation": "Implement targeted executive leadership development program",
                "actions": [
                    "Establish sponsorship program pairing senior executives with high-potential women",
                    "Create rotation opportunities in P&L roles",
                    "Set clear diversity targets for executive searches"
                ],
                "metrics": [
                    "Percentage increase in women executives",
                    "Promotion rates to executive positions",
                    "Retention rates of women in leadership pipeline"
                ],
                "timeline": "12-18 months",
                "resources_needed": [
                    "Executive development budget",
                    "External leadership coaches",
                    "Mentorship program infrastructure"
                ]
            })

        # Pay Equity Interventions
        if gaps["pay_equity_gaps"]["base_pay_gap"] > benchmarks["pay_equity"]["gap_threshold"]:
            recommendations.append({
                "area": "pay_equity",
                "priority": "high",
                "type": "immediate",
                "recommendation": "Implement comprehensive pay equity analysis and adjustment program",
                "actions": [
                    "Conduct detailed pay equity audit",
                    "Establish clear salary bands",
                    "Create standardized promotion criteria",
                    "Implement regular pay gap monitoring"
                ],
                "metrics": [
                    "Reduction in pay gap percentage",
                    "Pay equity by role and level",
                    "Promotion rate parity"
                ],
                "timeline": "6-12 months",
                "resources_needed": [
                    "Compensation analysis tools",
                    "Budget for pay adjustments",
                    "HR analytics capabilities"
                ]
            })

        # Safety and Violence Prevention
        if gaps["safety_gaps"]["prevention_gap"] > 0.1:
            recommendations.append({
                "area": "safety",
                "priority": "high",
                "type": "critical",
                "recommendation": "Enhance workplace safety and violence prevention framework",
                "actions": [
                    "Implement comprehensive safety training",
                    "Establish anonymous reporting system",
                    "Create rapid response protocol",
                    "Develop support services network"
                ],
                "metrics": [
                    "Incident reporting rates",
                    "Response time to reports",
                    "Training completion rates",
                    "Employee safety perception scores"
                ],
                "timeline": "3-6 months",
                "resources_needed": [
                    "Training platform",
                    "Reporting system",
                    "Support services budget"
                ]
            })

        # Care Support Systems
        if gaps["care_support_gaps"]["support_gap"] > 0.15:
            recommendations.append({
                "area": "care_support",
                "priority": "high",
                "type": "structural",
                "recommendation": "Develop comprehensive care support infrastructure",
                "actions": [
                    "Implement flexible work policies",
                    "Establish care support allowances",
                    "Create return-to-work programs",
                    "Develop caregiver networks"
                ],
                "metrics": [
                    "Utilization of care support programs",
                    "Return-to-work rates",
                    "Career progression of caregivers",
                    "Employee satisfaction scores"
                ],
                "timeline": "6-12 months",
                "resources_needed": [
                    "Care support budget",
                    "Policy framework",
                    "Program management resources"
                ]
            })

        # Policy Implementation
        if gaps["policy_gaps"]["implementation_gap"] > 0.1:
            recommendations.append({
                "area": "policy",
                "priority": "medium",
                "type": "systemic",
                "recommendation": "Strengthen policy implementation and monitoring framework",
                "actions": [
                    "Establish policy oversight committee",
                    "Create implementation roadmap",
                    "Develop monitoring mechanisms",
                    "Regular policy effectiveness reviews"
                ],
                "metrics": [
                    "Policy implementation rates",
                    "Compliance scores",
                    "Employee awareness levels",
                    "Policy effectiveness measures"
                ],
                "timeline": "9-12 months",
                "resources_needed": [
                    "Policy management system",
                    "Training resources",
                    "Monitoring tools"
                ]
            })

        # Industry-Specific Recommendations
        industry_specific = self._generate_industry_specific_recommendations(
            analysis, 
            benchmarks, 
            gaps
        )
        recommendations.extend(industry_specific)

        # Prioritize and sort recommendations
        return self._prioritize_recommendations(recommendations, gaps)

    def _generate_industry_specific_recommendations(
        self, 
        analysis: Dict, 
        benchmarks: Dict, 
        gaps: Dict
    ) -> List[Dict]:
        """Generate industry-specific recommendations based on sector characteristics"""
        
        industry_recs = []
        industry = analysis.get("industry", "").lower()

        if industry == "tech":
            if gaps["leadership_gaps"]["pipeline_gap"] > 0.1:
                industry_recs.append({
                    "area": "tech_pipeline",
                    "priority": "high",
                    "type": "structural",
                    "recommendation": "Build inclusive technical leadership pipeline",
                    "actions": [
                        "Create technical mentorship programs",
                        "Implement blind coding assessments",
                        "Establish returnship programs",
                        "Partner with women in tech organizations"
                    ],
                    "metrics": [
                        "Women in technical leadership roles",
                        "Technical hiring diversity",
                        "Technical promotion rates"
                    ],
                    "timeline": "12-18 months"
                })

        elif industry == "healthcare":
            if gaps["care_support_gaps"]["flexibility_gap"] > 0.1:
                industry_recs.append({
                    "area": "healthcare_workforce",
                    "priority": "high",
                    "type": "operational",
                    "recommendation": "Implement healthcare-specific flexibility framework",
                    "actions": [
                        "Create shift-trading platform",
                        "Establish predictive scheduling",
                        "Develop emergency care support",
                        "Implement job-sharing programs"
                    ],
                    "metrics": [
                        "Schedule flexibility usage",
                        "Staff satisfaction scores",
                        "Care coverage metrics"
                    ],
                    "timeline": "6-12 months"
                })

        elif industry == "finance":
            if gaps["pay_equity_gaps"]["bonus_gap"] > benchmarks["pay_equity"]["bonus_gap_threshold"]:
                industry_recs.append({
                    "area": "financial_compensation",
                    "priority": "high",
                    "type": "immediate",
                    "recommendation": "Address finance-specific compensation disparities",
                    "actions": [
                        "Review bonus allocation criteria",
                        "Analyze client assignment patterns",
                        "Standardize deal credit attribution",
                        "Implement transparent commission structures"
                    ],
                    "metrics": [
                        "Bonus gap reduction",
                        "Deal participation equity",
                        "Client portfolio diversity"
                    ],
                    "timeline": "3-6 months"
                })

        return industry_recs

    def _prioritize_recommendations(
        self, 
        recommendations: List[Dict], 
        gaps: Dict
    ) -> List[Dict]:
        """Prioritize recommendations based on gap analysis and impact potential"""
        
        def calculate_priority_score(rec):
            # Base priority scores
            priority_scores = {"high": 3, "medium": 2, "low": 1}
            
            # Initial score based on priority
            score = priority_scores[rec["priority"]]
            
            # Adjust based on gap severity
            gap_area = rec["area"]
            if gap_area in gaps:
                gap_severity = max(gaps[gap_area].values())
                score += gap_severity * 2
                
            # Adjust based on recommendation type
            type_multipliers = {
                "critical": 2.0,
                "immediate": 1.8,
                "structural": 1.5,
                "systemic": 1.3,
                "operational": 1.2
            }
            score *= type_multipliers.get(rec["type"], 1.0)
            
            return score
        
        # Sort recommendations by calculated priority score
        sorted_recs = sorted(
            recommendations,
            key=calculate_priority_score,
            reverse=True
        )
        
        # Add implementation sequence numbers
        for i, rec in enumerate(sorted_recs, 1):
            rec["implementation_sequence"] = i
            
        return sorted_recs


    def _analyze_violence_prevention(self, analysis: Dict, benchmarks: Dict) -> Dict:
        """Analyze violence prevention measures and gaps"""
        violence_indicators = self._extract_violence_indicators(analysis)
        current_score = self._calculate_violence_prevention_score(violence_indicators)
        
        return {
            "risk_assessment": {
                "severity_levels": self._evaluate_violence_risks(violence_indicators),
                "risk_patterns": self._identify_risk_patterns(violence_indicators),
                "vulnerability_factors": self._assess_vulnerabilities(violence_indicators)
            },
            "prevention_measures": {
                "existing_measures": self._evaluate_existing_measures(violence_indicators),
                "recommended_measures": self._recommend_prevention_measures(violence_indicators),
                "implementation_timeline": self._generate_implementation_timeline(violence_indicators)
            },
            "benchmark_comparison": {
                "current_score": current_score,
                "industry_benchmark": benchmarks["safety_metrics"]["violence_prevention_score"],
                "gap_analysis": {
                    "prevention_gap": benchmarks["safety_metrics"]["violence_prevention_score"] - current_score,
                    "reporting_gap": benchmarks["safety_metrics"]["harassment_reporting_mechanism"] - analysis.get("safety_assessment", {}).get("psychological_safety", {}).get("score", 0),
                    "response_gap": benchmarks["safety_metrics"]["response_effectiveness"] - current_score
                },
                "improvement_priorities": self._identify_improvement_priorities(violence_indicators, benchmarks)
            },
            "monitoring_framework": {
                "metrics": self._define_monitoring_metrics(violence_indicators),
                "reporting_schedule": self._create_reporting_schedule(),
                "accountability_measures": self._define_accountability_measures()
            }
        }

    def _analyze_care_work(self, analysis: Dict, benchmarks: Dict) -> Dict:
        """Analyze unpaid care work recognition and support"""
        care_indicators = self._extract_care_indicators(analysis)
        return {
            "care_burden_assessment": self._evaluate_care_burden(care_indicators),
            "support_measures": self._recommend_care_support(care_indicators),
            "benchmark_comparison": {
                "current_score": self._calculate_care_support_score(care_indicators),
                "industry_benchmark": benchmarks["care_support_score"],
                "gap_analysis": self._calculate_care_support_gaps(care_indicators, benchmarks)
            }
        }

    def _analyze_policy_framework(self, analysis: Dict, benchmarks: Dict) -> Dict:
        """Analyze policy framework effectiveness"""
        policy_indicators = self._extract_policy_indicators(analysis)
        return {
            "policy_assessment": self._evaluate_policy_effectiveness(policy_indicators),
            "policy_recommendations": self._generate_policy_recommendations(policy_indicators),
            "benchmark_comparison": {
                "current_score": self._calculate_policy_score(policy_indicators),
                "industry_benchmark": benchmarks["policy_implementation_score"],
                "gap_analysis": self._calculate_policy_gaps(policy_indicators, benchmarks)
            }
        }
    
    def _store_analysis(self, db: Session, text: str, analysis: Dict, context: Optional[Dict] = None):
        """Store analysis results in database"""
        analysis_record = Analysis(
            text=text,
            analysis_type="gender_equity",
            results=json.dumps(analysis),
            context=json.dumps(context) if context else None,
            created_at=datetime.utcnow()
        )
        
        db.add(analysis_record)
        db.commit()
        db.refresh(analysis_record)
