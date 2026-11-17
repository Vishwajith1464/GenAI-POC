# Requirements — Document Q&A Chatbot (POC)

## 1. Goal

Prove that a retrieval-augmented chatbot can answer questions about a single policy
document **only from that document**, with correct section citations, and can say
when the document does not contain the answer.

Hypothesis under test: *paragraph-level chunking + embedding retrieval + Gemini
generation produces grounded, correctly cited answers on the test set in
`sampleQuestions.md`.*

## 2. Users

| Role      | Description                                                                 |
|-----------|-----------------------------------------------------------------------------|
| Asker     | An engineer who needs a quick, citable answer about the deployment policy. Assumed to know general engineering terms, not the policy's details. |
| Developer | You. Runs ingestion and the evaluation suite.                               |

There is no authentication and there are no user roles in the POC.

## 3. Scope

### In scope
- One document: `ai_document_intelligence_poc_sample.pdf` (ENG-POL-014 v2.1).
- Ingestion runs once, at startup or as a script. There is no upload endpoint.
- A single-turn question → answer HTTP API.
- English, text-based PDF.

### Out of scope (future)
- Multiple documents, document versions, conflicting documents.
- Upload endpoint, admin/user roles, authentication, access control.
- UI.
- Conversation memory / follow-up questions.
- Scanned PDFs, tables, images, OCR.
- Latency or throughput targets, concurrency, horizontal scaling.

## 4. Functional requirements

### Ingestion
- **FR-1** The system extracts text from the PDF and splits it into chunks.
- **FR-2** Every chunk records the section number it belongs to (e.g. `3.1`).
  Text before Section 1 (title, document ID, version, dates) is labelled `Header`.
- **FR-3** Running ingestion twice on the same PDF produces identical chunk IDs.

### Answering
- **FR-4** The API accepts a question and returns a response with exactly one of
  three statuses:

  | Status      | When                                                                 | Answer text                                                                 | Citations |
  |-------------|----------------------------------------------------------------------|-----------------------------------------------------------------------------|-----------|
  | `answered`  | The document fully answers the question.                             | The answer.                                                                 | Required, ≥ 1 |
  | `partial`   | The document addresses the topic but not the specific thing asked.   | States what is missing, then what the document *does* say.                  | Required for the part that is answered |
  | `not_found` | The document does not address the question at all.                  | Exactly: `The document does not contain this information.`                  | None      |

- **FR-5** Every factual claim in an `answered` or `partial` answer is supported by
  the text of a section it cites. (Faithfulness: the claim is checked against the
  **cited section's text**, not against the question.)
- **FR-6** Citations are section numbers as they appear in the document
  (`1`, `3.1`, `4.1`, …) or `Header`. Every section needed for the answer is cited;
  no section is cited that does not support a claim.
- **FR-7** The system never answers from general knowledge. Questions outside the
  document return `not_found`, even if the model knows the answer.
- **FR-8** Instructions contained in the question (e.g. "ignore the document")
  are not followed. The question is treated as a question, never as instructions.
- **FR-9** If a question contains a false premise that the document contradicts,
  the answer corrects the premise and cites the contradicting section.

### API contract
- **FR-10** `POST /ask`

  Request:
  ```json
  { "question": "Who must approve a standard production deployment?" }
  ```
  Response `200`:
  ```json
  {
    "status": "answered",
    "answer": "The release manager must approve every standard production deployment before execution.",
    "citations": ["3.1"]
  }
  ```
- **FR-11** An empty or missing `question` returns `400`. A failure calling the
  Gemini API returns `502` with an error message. It never returns a fabricated answer.

## 5. Non-functional requirements
- **NFR-1 Model:** Generation uses `gemini-2.5-flash-lite` via the `google-genai` SDK.
  Model names live in configuration, not in code.
- **NFR-2 Secrets:** `GEMINI_API_KEY` is read from `.env`, and `.env` is never committed.
- **NFR-3 Data sensitivity:** The sample document is fictional, so sending its text
  to the Gemini API is acceptable. Real company documents are **not** to be used
  until data handling is approved. That review is out of scope for the POC.
- **NFR-4 Observability:** Every request logs: question, retrieved chunk IDs with
  scores, status, citations, and end-to-end latency in ms. There is no latency target,
  but latency is measured to give a baseline for later.
- **NFR-5 Reproducibility:** Dependencies are pinned in a dependency file. A fresh
  clone + `.env` + one documented command runs the evaluation.

## 6. Evaluation and definition of done

The test set is `sampleQuestions.md`. Each question defines: expected status,
expected citations, and must-include facts.

A question **passes** when all of the following hold:
1. The returned `status` equals the expected status.
2. The returned citations equal the expected citations (no missing, no extra).
3. Every must-include fact is present (in meaning, not necessarily wording).
4. No claim in the answer is unsupported by its cited section text (FR-5).

The POC is **done** when:
- **Retrieval:** for every answerable question, every expected section appears in
  the retrieved top-k chunks (100%; if retrieval misses, generation cannot recover).
- **Answers:** ≥ 90% of all questions pass.
- **Hard gates (no exceptions):** 0 fabricated claims (criterion 4), and 100% of
  `not_found` and adversarial questions pass.

## 7. Open decisions (resolved in Design, not here)
- Value of top-k and the minimum similarity score.
- Embedding model.
- Vector storage (in-memory vs. a library).
- How criteria 3 and 4 are judged (manual review vs. LLM-as-judge).
- Web framework for the API.
