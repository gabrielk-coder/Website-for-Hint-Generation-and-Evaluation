# =====================================================
# Answer generation prompt template
# =====================================================

def answer_for_answer_agnostic_prompt(question, max_tokens):
    target_words = int(max_tokens * 0.5)
    
    if target_words < 10:
        style_instruction = "Respond with a single phrase or keyword only. No full sentences."
    else:
        style_instruction = "Respond with one extremely concise sentence."

    return (f"""
### INSTRUCTION
Provide the answer to the Question below. 

### STRICT CONSTRAINTS
1. LENGTH: {style_instruction} Keep it under {target_words} words.
2. STYLE: Telegraphic and data-centric. No filler words. No intro/outro.
3. FORMAT: Plain text only.
4. CONTENT: High information density. Omit articles (a, an, the) if possible to save space.
5. SAFETY: If offensive, return "Cannot answer." If unknown, return "Answer unavailable."

### INPUT
Question: {question}

### OUTPUT
(Direct answer only): """)

def answer_for_answer_aware_prompt(question, max_tokens, answer):
    max_words = int(max_tokens * 0.6) 
    
    reference_content = answer if answer and answer.strip() else "No reference provided. Use general knowledge."

    safe_q = question.replace("{", "{{").replace("}", "}}")
    safe_ref = reference_content.replace("{", "{{").replace("}", "}}")

    return (f"""
### INPUT DATA
Question: {safe_q}
Reference Material: {safe_ref}

### INSTRUCTION
Extract the specific answer from the Reference Material.

### STRICT CONSTRAINTS
1. LENGTH: Maximum {max_words} words. Ideally much shorter.
2. SOURCE TRUTH: Rely ONLY on the Reference Material.
3. STYLE: Distill the answer down to its core facts. Do not write conversationally. 
4. NEGATIVE CONSTRAINT: Do not start with "The answer is" or "According to the text."
5. FORMAT: Plain text.

### OUTPUT
(The distilled answer):
""")

# =====================================================
# Candidate generation prompt template
# =====================================================

def prompt_candidates(num_candidates, question, max_tokens, hints=None):
    hints_section = ""
    if hints and len(hints) > 0:
        formatted_list = "\n".join([f"- {hint}" for hint in hints])
        hints_section = f"Contextual Hints:\n{formatted_list}\n"

    num_distractors = num_candidates - 1
    
    word_limit = max(3, int(max_tokens * 0.6))

    return (
        "You are a quiz generator engine designed for extreme brevity.\n\n"
        
        "### TASK\n"
        f"Generate exactly {num_candidates} multiple-choice options for the Question.\n"
        
        "### INPUT DATA\n"
        f"Question: {question}\n"
        f"{hints_section}\n"
        
        "### CONTENT RULES\n"
        "- **Brevity:** Options must be short phrases or single words.\n"
        f"- **Limit:** STRICTLY fewer than {word_limit} words per option.\n"
        "- **Plausibility:** Distractors must be realistic but incorrect.\n"
        "- **Format:** Raw text only. No numbering, no markdown, no punctuation at the end.\n"
        "- **Distinctness:** No duplicate meanings.\n\n"

        "### STRUCTURAL RULE (CRITICAL)\n"
        f"Output exactly {num_candidates} lines:\n"
        f"1. First {num_distractors} lines: INCORRECT options.\n"
        "2. LAST line: CORRECT option.\n"
        "3. Do not label them.\n\n"

        "### OUTPUT\n"
    )