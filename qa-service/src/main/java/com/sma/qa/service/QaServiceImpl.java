package com.sma.qa.service;

import com.sma.qa.dto.AiInferenceRequest;
import com.sma.qa.dto.AiInferenceResponse;
import com.sma.qa.dto.QaAskRequest;
import com.sma.qa.dto.QaAskResponse;
import com.sma.qa.dto.QaCitation;
import com.sma.qa.dto.QaHistoryDetailResponse;
import com.sma.qa.dto.QaHistoryListResponse;
import com.sma.qa.dto.QaHistorySummary;
import com.sma.qa.dto.QaMessage;
import com.sma.qa.dto.RagRetrievalItem;
import com.sma.qa.dto.RagRetrievalRequest;
import com.sma.qa.dto.RagRetrievalResponse;
import com.sma.qa.integration.AiGatewayClient;
import com.sma.qa.integration.RagServiceClient;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import org.springframework.stereotype.Service;

@Service
public class QaServiceImpl implements QaService {

    private final RagServiceClient ragServiceClient;
    private final AiGatewayClient aiGatewayClient;
    private final ConcurrentMap<String, ConversationSession> historyStore = new ConcurrentHashMap<>();

    public QaServiceImpl(
            RagServiceClient ragServiceClient,
            AiGatewayClient aiGatewayClient
    ) {
        this.ragServiceClient = ragServiceClient;
        this.aiGatewayClient = aiGatewayClient;
    }

    @Override
    public QaAskResponse ask(QaAskRequest request) {
        String historyId = request.historyId() == null || request.historyId().isBlank()
                ? UUID.randomUUID().toString()
                : request.historyId();
        String traceId = UUID.randomUUID().toString();

        ConversationSession session = historyStore.computeIfAbsent(
                historyId,
                ignored -> new ConversationSession(request.userId(), request.courseId())
        );
        session.addMessage("user", request.question());

        RagRetrievalResponse ragResponse = ragServiceClient.retrieve(
                new RagRetrievalRequest(
                        request.courseId(),
                        request.question(),
                        request.topK() == null || request.topK() < 1 ? 3 : request.topK(),
                        Map.of("courseId", request.courseId())
                )
        );

        String prompt = buildQaPrompt(request, historyId, session.messages(), ragResponse.results());
        AiInferenceResponse inferenceResponse = aiGatewayClient.inferSync(
                new AiInferenceRequest(
                        "qa",
                        prompt,
                        traceId,
                        request.userId(),
                        Map.of(
                                "courseId", request.courseId(),
                                "historyId", historyId,
                                "knowledgeBase", request.courseId(),
                                "retrievalCount", String.valueOf(ragResponse.results().size())
                        )
                )
        );

        session.addMessage("assistant", inferenceResponse.outputText());

        return new QaAskResponse(
                historyId,
                inferenceResponse.outputText(),
                ragResponse.results().stream().map(this::toCitation).toList(),
                inferenceResponse.traceId()
        );
    }

    @Override
    public QaHistoryListResponse listHistory(String userId, String courseId) {
        return new QaHistoryListResponse(
                historyStore.entrySet().stream()
                        .filter(entry -> entry.getValue().userId().equals(userId))
                        .filter(entry -> courseId == null || courseId.isBlank() || entry.getValue().courseId().equals(courseId))
                        .sorted(Comparator.comparing(
                                (Map.Entry<String, ConversationSession> entry) -> entry.getValue().updatedAt()
                        ).reversed())
                        .map(entry -> new QaHistorySummary(
                                entry.getKey(),
                                entry.getValue().courseId(),
                                entry.getValue().lastUserQuestion(),
                                entry.getValue().updatedAt()
                        ))
                        .toList()
        );
    }

    @Override
    public QaHistoryDetailResponse getHistory(String historyId) {
        ConversationSession session = historyStore.get(historyId);
        if (session == null) {
            return new QaHistoryDetailResponse(historyId, List.of());
        }
        return new QaHistoryDetailResponse(historyId, session.messages());
    }

    private String buildQaPrompt(
            QaAskRequest request,
            String historyId,
            List<QaMessage> historyMessages,
            List<RagRetrievalItem> retrievalItems
    ) {
        String conversationHistory = historyMessages.stream()
                .limit(Math.max(0, historyMessages.size() - 1))
                .map(message -> message.role() + ": " + message.content())
                .reduce((left, right) -> left + "\n" + right)
                .orElse("No prior conversation.");

        String retrievedContext = retrievalItems.isEmpty()
                ? "No relevant course context was retrieved from the knowledge base."
                : retrievalItems.stream()
                        .map(item -> """
                                Source document: %s
                                Chunk id: %s
                                Relevance score: %.4f
                                Content: %s
                                """.formatted(
                                item.documentId(),
                                item.chunkId(),
                                item.score(),
                                item.text()
                        ))
                        .reduce((left, right) -> left + "\n---\n" + right)
                        .orElse("No relevant course context was retrieved from the knowledge base.");

        return """
                You are a teaching assistant for a university course inside Canvas.
                Answer the student's question using the retrieved course context first.
                If the retrieved context is insufficient, say so clearly and provide the best concise explanation you can.
                Keep the answer accurate, concise, and student-friendly.
                Mention key terms exactly as they appear in the course material when possible.

                Course id: %s
                User id: %s
                History id: %s

                Conversation history:
                %s

                Retrieved course context:
                %s

                Student question:
                %s
                """.formatted(
                request.courseId(),
                request.userId(),
                historyId,
                conversationHistory,
                retrievedContext,
                request.question()
        );
    }

    private QaCitation toCitation(RagRetrievalItem item) {
        String sourceTitle = item.metadata() != null && item.metadata().get("sourceTitle") != null
                ? item.metadata().get("sourceTitle")
                : item.documentId();
        String excerpt = item.text() == null
                ? ""
                : item.text().length() > 180 ? item.text().substring(0, 180) + "..." : item.text();

        return new QaCitation(item.chunkId(), sourceTitle, excerpt);
    }

    private static final class ConversationSession {
        private final String userId;
        private final String courseId;
        private final List<QaMessage> messages = new ArrayList<>();
        private OffsetDateTime updatedAt = OffsetDateTime.now();

        private ConversationSession(String userId, String courseId) {
            this.userId = userId;
            this.courseId = courseId;
        }

        private synchronized void addMessage(String role, String content) {
            messages.add(new QaMessage(role, content, OffsetDateTime.now()));
            updatedAt = OffsetDateTime.now();
        }

        private synchronized List<QaMessage> messages() {
            return List.copyOf(messages);
        }

        private synchronized OffsetDateTime updatedAt() {
            return updatedAt;
        }

        private String userId() {
            return userId;
        }

        private String courseId() {
            return courseId;
        }

        private synchronized String lastUserQuestion() {
            for (int index = messages.size() - 1; index >= 0; index--) {
                QaMessage message = messages.get(index);
                if ("user".equals(message.role())) {
                    return message.content();
                }
            }
            return "";
        }
    }
}
