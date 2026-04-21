### Canvas AI-Enhanced Subsystem API

Unified contract for the six-core-microservice Canvas AI-Enhanced Subsystem. Business services own domain workflows and relational data, AI Gateway owns model orchestration, and RAG Service owns vector storage and retrieval.

#### Base URLs

| URL | Description |
|-----|-------------|
| `http://localhost:9000` | Unified API gateway |
| `http://localhost` | Direct service access |

#### Course Service APIs

##### POST `/course/summarize`

Summarize course slides.

###### RequestBody

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `fileId` | string | Yes | Canvas file identifier. |
| `courseId` | string | Yes | Course identifier. |
| `userId` | string | Yes | Current user identifier. |
| `accessToken` | string | Yes | Canvas access token used for mock verification. |
| `preferredLanguage` | string | No | Preferred summary language such as `English`. |

###### Responses

**200 OK**

| Field | Type | Description |
|-------|------|-------------|
| `fileId` | string | File identifier. |
| `courseId` | string | Course identifier. |
| `summaryText` | string | Generated summary text. |
| `generatedBy` | string | Upstream model/provider marker. |
| `traceId` | string | Request trace identifier. |

##### POST `/course/generate-quiz`

Generate formative quiz questions from course material.

###### RequestBody

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `courseId` | string | Yes | Course identifier. |
| `fileId` | string | Yes | Source file identifier. |
| `questionCount` | integer | Yes | Number of questions to generate. |
| `difficulty` | string | No | Difficulty level such as `easy`, `medium`, or `hard`. |
| `userId` | string | Yes | Current user identifier. |

###### Responses

**200 OK**

| Field | Type | Description |
|-------|------|-------------|
| `quizId` | string | Generated quiz identifier. |
| `courseId` | string | Course identifier. |
| `questions` | array | Generated quiz questions. Each item contains `questionId`, `stem`, `options`, `answer`, and `explanation`. |

#### Assignment Service APIs

##### POST `/assignment/guiding`

Generate assignment guidance.

###### RequestBody

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `assignmentId` | string | Yes | Assignment identifier. |
| `courseId` | string | Yes | Course identifier. |
| `userId` | string | Yes | Current user identifier. |
| `prompt` | string | Yes | User guidance request or focus area. |
| `contextFileIds` | array[string] | No | Related Canvas file identifiers. |

###### Responses

**200 OK**

| Field | Type | Description |
|-------|------|-------------|
| `assignmentId` | string | Assignment identifier. |
| `guidanceText` | string | Generated guidance text. |
| `traceId` | string | Request trace identifier. |

##### POST `/assignment/grading`

Generate grading suggestions.

###### RequestBody

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `assignmentId` | string | Yes | Assignment identifier. |
| `submissionId` | string | Yes | Submission identifier. |
| `graderId` | string | Yes | Teacher or grader identifier. |
| `submissionText` | string | Yes | Submission content to evaluate. |
| `rubric` | array | Yes | Rubric criteria list. Each item contains `criterionId`, `title`, `maxScore`, and `description`. |

###### Responses

**200 OK**

| Field | Type | Description |
|-------|------|-------------|
| `assignmentId` | string | Assignment identifier. |
| `submissionId` | string | Submission identifier. |
| `totalScoreSuggestion` | number | Suggested total score. |
| `criterionFeedback` | array | Criterion-level feedback. Each item contains `criterionId`, `suggestedScore`, and `feedback`. |

##### POST `/assignment/detect-ai`

Detect AI-generated characteristics in assignment content.

###### RequestBody

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `assignmentId` | string | Yes | Assignment identifier. |
| `submissionId` | string | Yes | Submission identifier. |
| `content` | string | Yes | Submission text to inspect. |

###### Responses

**200 OK**

| Field | Type | Description |
|-------|------|-------------|
| `submissionId` | string | Submission identifier. |
| `aiProbability` | number | Estimated AI-generation probability. |
| `rationale` | string | Explanation of the assessment. |
| `flagged` | boolean | Whether the submission should be flagged for review. |

#### QA Service APIs

##### POST `/qa/ask`

Ask a question about course content.

###### RequestBody

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `courseId` | string | Yes | Course identifier. |
| `userId` | string | Yes | Current user identifier. |
| `historyId` | string | No | Existing QA conversation identifier. |
| `question` | string | Yes | User question. |
| `topK` | integer | No | Number of retrieval results to use. |

###### Responses

**200 OK**

| Field | Type | Description |
|-------|------|-------------|
| `historyId` | string | QA conversation identifier. |
| `answer` | string | Generated answer. |
| `citations` | array | Source citations. Each item contains `sourceId`, `sourceTitle`, and `excerpt`. |
| `traceId` | string | Request trace identifier. |

##### GET `/qa/history-list`

List QA session history.

###### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `userId` | string | Yes | Current user identifier. |
| `courseId` | string | No | Optional course filter. |

###### Responses

**200 OK**

| Field | Type | Description |
|-------|------|-------------|
| `histories` | array | QA history summary list. Each item contains `historyId`, `courseId`, `lastQuestion`, and `updatedAt`. |

##### GET `/qa/history/{history_id}`

Get a QA conversation history.

###### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `history_id` | string | Yes | QA history identifier. |

###### Responses

**200 OK**

| Field | Type | Description |
|-------|------|-------------|
| `historyId` | string | QA history identifier. |
| `messages` | array | Conversation messages. Each item contains `role`, `content`, and `createdAt`. |

#### Moderation Service APIs

##### POST `/moderation/text`

Moderate plain text content.

###### RequestBody

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | Yes | Text content to review. |
| `userId` | string | Yes | Current user identifier. |
| `scene` | string | No | Moderation scene such as `discussion`, `submission`, or `announcement`. |

###### Responses

**200 OK**

| Field | Type | Description |
|-------|------|-------------|
| `flagged` | boolean | Whether the content is flagged. |
| `categoryScores` | object | Risk scores by moderation category. |
| `reason` | string | Human-readable moderation explanation. |

##### POST `/moderation/file`

Moderate uploaded file content.

###### RequestBody

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `fileId` | string | Yes | File identifier. |
| `userId` | string | Yes | Current user identifier. |
| `fileType` | string | Yes | File media type or extension. |
| `extractedText` | string | No | Text extracted from the file for moderation. |

###### Responses

**200 OK**

| Field | Type | Description |
|-------|------|-------------|
| `fileId` | string | File identifier. |
| `flagged` | boolean | Whether the file is flagged. |
| `reason` | string | Human-readable moderation explanation. |

#### AI Gateway Service APIs

##### POST `/ai/infer-sync`

Run synchronous model inference.

###### RequestBody

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `capability` | string | Yes | AI capability name such as `slide-summary` or `qa-answer`. |
| `prompt` | string | Yes | Final prompt sent to the model. |
| `traceId` | string | No | Upstream trace identifier. |
| `userId` | string | No | Current user identifier. |
| `metadata` | object | No | Additional structured request metadata. |

###### Responses

**200 OK**

| Field | Type | Description |
|-------|------|-------------|
| `capability` | string | AI capability name. |
| `traceId` | string | Trace identifier. |
| `outputText` | string | Generated model output. |
| `provider` | string | LLM provider name. |
| `model` | string | Model identifier. |

##### POST `/ai/infer-async`

Submit asynchronous model inference.

###### RequestBody

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `capability` | string | Yes | AI capability name. |
| `prompt` | string | Yes | Final prompt sent to the model. |
| `userId` | string | No | Current user identifier. |
| `callbackUrl` | string | No | Optional callback URL for completion notification. |
| `metadata` | object | No | Additional structured request metadata. |

###### Responses

**202 Accepted**

| Field | Type | Description |
|-------|------|-------------|
| `taskId` | string | Accepted task identifier. |
| `status` | string | Initial task status. |
| `acceptedAt` | string | Acceptance timestamp. |

##### GET `/ai/result/{task_id}`

Query asynchronous inference result.

###### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `task_id` | string | Yes | Async task identifier. |

###### Responses

**200 OK**

| Field | Type | Description |
|-------|------|-------------|
| `taskId` | string | Task identifier. |
| `status` | string | Current task status. |
| `outputText` | string | Generated output when available. |
| `errorMessage` | string | Error message when the task fails. |

##### GET `/ai/token-statistic`

Query token usage statistics.

###### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `userId` | string | No | Filter by user identifier. |
| `from` | string | No | Start timestamp or date. |
| `to` | string | No | End timestamp or date. |

###### Responses

**200 OK**

| Field | Type | Description |
|-------|------|-------------|
| `userId` | string | User identifier. |
| `totalPromptTokens` | integer | Total prompt token usage. |
| `totalCompletionTokens` | integer | Total completion token usage. |
| `totalCostUsd` | number | Estimated cost in USD. |

#### RAG Service APIs

##### POST `/rag/store`

Store content embeddings.

###### RequestBody

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `knowledgeBase` | string | Yes | Knowledge base name or namespace. |
| `documentId` | string | Yes | Source document identifier. |
| `metadata` | object | No | Document-level metadata. |
| `chunks` | array | Yes | Content chunks to embed and store. Each item contains `chunkId`, `text`, and `sequence`. |

###### Responses

**202 Accepted**

| Field | Type | Description |
|-------|------|-------------|
| `documentId` | string | Source document identifier. |
| `storedChunkCount` | integer | Number of stored chunks. |
| `status` | string | Storage status. |

##### POST `/rag/retrieval`

Retrieve semantically similar content.

###### RequestBody

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `knowledgeBase` | string | Yes | Knowledge base name or namespace. |
| `query` | string | Yes | User retrieval query. |
| `topK` | integer | No | Maximum number of results to return. |
| `filters` | object | No | Optional structured metadata filters. |

###### Responses

**200 OK**

| Field | Type | Description |
|-------|------|-------------|
| `query` | string | Original retrieval query. |
| `results` | array | Retrieval matches. Each item contains `chunkId`, `documentId`, `score`, and `text`. |
