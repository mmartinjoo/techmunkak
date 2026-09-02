from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from techmunkak.core.config import settings
from techmunkak.skill_gap_analysis import selectors
from techmunkak.skill_gap_analysis.models import Job

class SkillGapAnalysis(BaseModel):
    summary: str | None = Field(description="Brief, overall summary of the analysis", default=None)
    priority_actions: list[str] = Field(description="Priority actions to take based on the analysis")
    missing_skills: list[str] = Field(description="Skills present in jobs but missing from the CV. Only include the most frequent skills that are presented in multiple jobs.")
    existing_skills: list[str] = Field(description="Skills present in jobs and in the CV")
    overall_match_percentage: float = Field(description="Overall skill match percentage (0-100)")
    recommendations: list[str] = Field(description="Recommendations to close the skill gap")

def analyze_skill_gap(
    cv_content: str, 
    target_role: str,
    target_job_keys: list[str],
) -> SkillGapAnalysis:
    if cv_content is None or cv_content == "":
        raise ValueError("CV content is empty")
    
    if len(target_job_keys) == 0:
        raise ValueError("Target job keys is empty")
    
    jobs = selectors.find_jobs(job_keys=target_job_keys)
    if len(jobs) == 0:
        raise ValueError("Target jobs is empty")
    
    jobs_md = _jobs_to_markdown(jobs=jobs)
    
    model = init_chat_model(        
        model_provider=settings.skill_gap_analysis_llm_provider,
        model=settings.skill_gap_analysis_llm_model,
        temperature=0.1,
    )
    
    return model.with_structured_output(SkillGapAnalysis).invoke(f"""
        You are a skill gap analyzer who help a tech person identify what skills they lack for a specifi position
        Please analyze the skill gap between the following CV and target jobs.
                    
        CV Content:
        {cv_content}
        
        The target role the user is want the analysis for:
        {target_role}
        
        The jobs we found in our database and are similar to the target role:
        {jobs_md}
        
        Please provide a detailed skill gap analysis.
    """)
    
def _jobs_to_markdown(jobs: list[Job]) -> str:
    md = ""
    for job in jobs:
        md += f"## {job.title}\n"
        md += f"{job.description}\n"
        md += "### Required skills\n"
        for skill in job.skills:
            md += f"- {skill.name}\n"
    return md
    