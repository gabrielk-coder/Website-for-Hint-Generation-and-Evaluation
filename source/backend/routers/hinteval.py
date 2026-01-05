from fastapi import APIRouter, Depends, Request, HTTPException
from typing import List

# Shared logic imports
from backend.database.connection import get_db
from backend.dependencies import get_or_create_session_id

# Pydantic Models
from backend.Objects.api_models import (
    GenerateReq, EvaluateReq, HintReq, SaveHintBody, 
    SaveCandidateBody, DeleteCandidateBody, UpdateAnswerReq, 
    PresetBody, RegenerateAnswerReq, RegenerateCandidatesReq
)

# Services
from backend.services import (
    question_service,
    hint_service,
    candidate_service,
    generation_service,
    evaluation_service,
    save_and_load_service
)

# Initialize Router
# All paths here will automatically start with /hinteval
router = APIRouter(prefix="/hinteval", tags=["HintEval"])

# ==========================
# GENERATION API
# ==========================

@router.post("/generate")
def generate(req: GenerateReq, request: Request, conn=Depends(get_db)):
    session_id = get_or_create_session_id(request)
    return generation_service.process_generation(
        conn=conn,
        session_id=session_id,
        question=req.question,
        num_hints=req.num_hints,
        temperature=req.temperature,
        max_tokens=req.max_tokens,
        model_name=req.model_name,
        answer_aware=(req.answer is not None and req.answer != ""), 
        provided_answer=req.answer
    )

@router.post("/regenerate_answer")
def regenerate_answer(req: RegenerateAnswerReq, request: Request, conn=Depends(get_db)):
    session_id = get_or_create_session_id(request)
    qid = question_service.get_latest_question_id(conn, session_id)
    if not qid:
        raise HTTPException(400, "No active question found.")
    
    q_data = question_service.get_question_and_answer(conn, session_id)
    if not q_data['question']:
         raise HTTPException(400, "Question text missing.")

    new_ans = generation_service.generate_only_answer(
        conn, 
        q_data['question'], 
        req.model_name, 
        req.temperature, 
        req.max_tokens,
        question_id=qid,
        hints=[h['hint_text'] for h in hint_service.get_hints_for_session(conn, session_id)]
    )
    
    question_service.clear_metrics_for_question(conn, qid)
    return {"status": "success", "answer": new_ans}

@router.post("/regenerate_candidates")
def regenerate_candidates(req: RegenerateCandidatesReq, request: Request, conn=Depends(get_db)):
    session_id = get_or_create_session_id(request)
    try:
        candidate_service.delete_all_candidates(conn, session_id)
        cands = candidate_service.generate_candidates_for_session(
            conn, 
            session_id, 
            req.num_candidates, 
            req.model_name, 
            req.temperature, 
            req.max_tokens,
            req.hints
        )
        return {"status": "success", "candidates": cands}
    except ValueError as e:
        raise HTTPException(400, str(e))

# ==========================
# EVALUATION API (Trigger)
# ==========================

@router.post("/evaluate")
def evaluate(req: EvaluateReq, request: Request, conn=Depends(get_db)):
    session_id = get_or_create_session_id(request)
    return evaluation_service.run_evaluation_and_persist(
        conn=conn,
        session_id=session_id,
        question=req.question,
        hints=req.hints,
        answer=req.answer,
        model_name=req.model_name,
        num_candidates=req.num_candidates,
        temperature=req.temperature,
        max_tokens=req.max_tokens
    )

# ==========================
# STATE & DATA API
# ==========================

@router.get("/session_state")
def get_session_state(request: Request, conn=Depends(get_db)):
    session_id = get_or_create_session_id(request)
    return question_service.get_full_session_state(conn, session_id)

@router.get("/get_question")
def get_question(request: Request, conn=Depends(get_db)):
    session_id = get_or_create_session_id(request)
    return question_service.get_question_and_answer(conn, session_id)

@router.get("/get-hints")
def get_hints(request: Request, conn=Depends(get_db)):
    session_id = get_or_create_session_id(request)
    return {"hints": hint_service.get_hints_for_session(conn, session_id)}

@router.get("/get_candidates")
def get_candidates(request: Request, conn=Depends(get_db)):
    session_id = get_or_create_session_id(request)
    return {"candidates": candidate_service.get_candidates(conn, session_id)}

# ==========================
# MANIPULATION API (CRUD)
# ==========================

@router.post("/save_hint")
def save_hint(body: SaveHintBody, request: Request, conn=Depends(get_db)):
    session_id = get_or_create_session_id(request)
    if not body.hint_text: raise HTTPException(400, "Empty hint text")
    
    hid = hint_service.save_hint(conn, session_id, body.hint_text)
    return {"status": "success", "hint_id": hid, "hint_text": body.hint_text}

@router.post("/update_hint")
def update_hint(body: HintReq, request: Request, conn=Depends(get_db)):
    hint_service.update_hint(conn, body.hint_id, body.hint_text)
    return {"status": "success", "hint_id": body.hint_id}

@router.post("/delete_hint")
def delete_hint(body: HintReq, conn=Depends(get_db)):
    hint_service.delete_hint(conn, body.hint_id)
    return {"status": "success"}

@router.post("/delete_all_hints")
def delete_all_hints(request: Request, conn=Depends(get_db)):
    session_id = get_or_create_session_id(request)
    hint_service.delete_all_hints(conn, session_id)
    return {"status": "success"}

@router.post("/save_candidate")
def save_candidate(body: SaveCandidateBody, request: Request, conn=Depends(get_db)):
    session_id = get_or_create_session_id(request)
    try:
        candidate_service.save_candidate(conn, session_id, body.candidate_text, body.candidate_index)
        return {"status": "success"}
    except (ValueError, IndexError) as e:
        raise HTTPException(400, detail=str(e))

@router.post("/delete_candidate")
def delete_candidate(body: DeleteCandidateBody, request: Request, conn=Depends(get_db)):
    session_id = get_or_create_session_id(request)
    try:
        candidate_service.delete_candidate(conn, session_id, body.candidate_index)
        return {"status": "success"}
    except IndexError as e:
        raise HTTPException(400, detail=str(e))

@router.post("/delete_all_candidates")
def delete_all_candidates(request: Request, conn=Depends(get_db)):
    session_id = get_or_create_session_id(request)
    candidate_service.delete_all_candidates(conn, session_id)
    return {"status": "success"}

@router.post("/reset_all")
def reset_all(request: Request, conn=Depends(get_db)):
    session_id = get_or_create_session_id(request)
    question_service.reset_session(conn, session_id)
    return {"status": "success"}

@router.post("/update_answer")
def update_answer(body: UpdateAnswerReq, request: Request, conn=Depends(get_db)):
    session_id = get_or_create_session_id(request)
    qid = question_service.get_latest_question_id(conn, session_id)
    
    if not qid:
        raise HTTPException(400, "No active question found to update.")
    
    question_service.update_existing_answer(conn, qid, body.answer)
    question_service.clear_metrics_for_question(conn, qid)
    
    return {"status": "success"}

@router.post("/load_preset")
def load_preset(body: PresetBody, request: Request, conn=Depends(get_db)):
    session_id = get_or_create_session_id(request)
    question_service.reset_session(conn, session_id)
    save_and_load_service.load_full_preset_state(conn, session_id, body.data)
    return {"status": "success"}