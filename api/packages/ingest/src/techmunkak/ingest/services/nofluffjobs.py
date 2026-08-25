import json
from techmunkak.core.db import connection
from techmunkak.ingest.models import JobUrl

def create_job(job_url: JobUrl, data: dict):
    with connection() as conn:
        conn.execute("""
            insert into bronze.nofluffjobs_jobs(
                job_url_id,
                external_id,
                url,
                title,
                daily_tasks,
                category,
                seniority,
                technology,
                company_url,
                company_name,
                description,
                benefits,
                salary_range_bottom,
                salary_range_top,
                salary_period,
                salary_currency,
                required_skills,
                nice_to_have_skills,
                requirements,
                posted_at,
                expired_at,
                regions
            )
            values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)          
        """, (
            job_url.id,
            data["external_id"],
            job_url.url,
            data["title"],
            json.dumps(data["daily_tasks"]),
            data["category"],
            json.dumps(data["seniority"]),
            data["technology"],
            data["company_url"],
            data["company_name"],
            data["description"],
            json.dumps(data["benefits"]),
            data["salary_range_bottom"],
            data["salary_range_top"],
            data["salary_period"],
            data["salary_currency"],
            json.dumps(data["required_skills"]),
            json.dumps(data["nice_to_have_skills"]),
            data["requirements"],
            data["posted_at"],
            data["expired_at"],
            json.dumps(data["regions"]),
        ))
        
        conn.commit()