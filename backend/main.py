from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from supabase_client import supabase_db

from discoveries.approve import router as discovery_approve_router
from discoveries.create import router as discovery_create_router
from discoveries.list import router as discovery_list_router
from discoveries.get import router as discovery_get_router
from discoveries.analyze import router as discovery_analyze_router

# ==========================================
# AUTH
# ==========================================

from auth.register import router as register_router
from auth.login import router as login_router
from auth.me import router as me_router
from auth.api_key import router as api_key_router


# ==========================================
# ENGAGEMENTS
# ==========================================

from engagements.create import router as engagement_router
from engagements.list import router as engagement_list_router
from engagements.get import router as engagement_get_router
from engagements.update import router as engagement_update_router


# ==========================================
# FINDINGS
# ==========================================

from findings.create import router as finding_router
from findings.list import router as finding_list_router
from findings.get import router as finding_get_router
from findings.update import router as finding_update_router
from findings.status import router as finding_status_router


# ==========================================
# EVIDENCE
# ==========================================

from evidence.create import router as evidence_router
from evidence.list import router as evidence_list_router
from evidence.screenshot import router as screenshot_router
from evidence.delete import router as evidence_delete_router


# ==========================================
# REPORTS
# ==========================================

from reports.generate import router as report_router


# ==========================================
# DASHBOARD
# ==========================================

from dashboard.stats import router as dashboard_stats_router


# ==========================================
# FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="Notiqx API",
    description="Backend API for Notiqx penetration testing platform",
    version="0.1.0"
)


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# AUTH ROUTES
# ==========================================

app.include_router(register_router)
app.include_router(login_router)
app.include_router(me_router)
app.include_router(api_key_router)


# ==========================================
# ENGAGEMENT ROUTES
# ==========================================

app.include_router(engagement_router)
app.include_router(engagement_list_router)
app.include_router(engagement_get_router)
app.include_router(engagement_update_router)


# ==========================================
# FINDING ROUTES
# ==========================================

app.include_router(finding_router)
app.include_router(finding_list_router)
app.include_router(finding_get_router)
app.include_router(finding_update_router)
app.include_router(finding_status_router)


# ==========================================
# EVIDENCE ROUTES
# ==========================================

app.include_router(evidence_router)
app.include_router(evidence_list_router)
app.include_router(screenshot_router)
app.include_router(evidence_delete_router)

app.include_router(discovery_create_router)
app.include_router(discovery_list_router)
app.include_router(discovery_get_router)
app.include_router(discovery_analyze_router)
app.include_router(discovery_approve_router)


# ==========================================
# REPORT ROUTES
# ==========================================

app.include_router(report_router)


# ==========================================
# DASHBOARD ROUTES
# ==========================================

app.include_router(dashboard_stats_router)


# ==========================================
# ROOT
# ==========================================

@app.get("/")
async def root():
    return {
        "message": "Notiqx API is running!",
        "status": "ok"
    }


# ==========================================
# SUPABASE TEST
# ==========================================

@app.get("/test-supabase")
async def test_supabase():

    response = (
        supabase_db
        .table("profiles")
        .select("id")
        .limit(1)
        .execute()
    )

    return {
        "message": "Supabase connection successful!",
        "data": response.data
    }