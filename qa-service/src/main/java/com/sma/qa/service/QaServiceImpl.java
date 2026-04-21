package com.sma.qa.service;

import com.sma.qa.dto.QaAskRequest;
import com.sma.qa.dto.QaAskResponse;
import com.sma.qa.dto.QaCitation;
import com.sma.qa.dto.QaHistoryDetailResponse;
import com.sma.qa.dto.QaHistoryListResponse;
import com.sma.qa.dto.QaHistorySummary;
import com.sma.qa.dto.QaMessage;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.UUID;
import org.springframework.stereotype.Service;

@Service
public class QaServiceImpl implements QaService {

    @Override
    public QaAskResponse ask(QaAskRequest request) {
        return new QaAskResponse(
                request.historyId() == null || request.historyId().isBlank() ? UUID.randomUUID().toString() : request.historyId(),
                "Bounded contexts help keep domain models isolated and easier to evolve independently.",
                List.of(new QaCitation("slide-4", "Week 4 DDD Deck", "Bounded contexts separate domain models.")),
                UUID.randomUUID().toString()
        );
    }

    @Override
    public QaHistoryListResponse listHistory(String userId, String courseId) {
        return new QaHistoryListResponse(
                List.of(new QaHistorySummary(UUID.randomUUID().toString(), courseId, "What is an aggregate?", OffsetDateTime.now()))
        );
    }

    @Override
    public QaHistoryDetailResponse getHistory(String historyId) {
        return new QaHistoryDetailResponse(
                historyId,
                List.of(
                        new QaMessage("user", "What is an aggregate?", OffsetDateTime.now().minusMinutes(2)),
                        new QaMessage("assistant", "An aggregate is a consistency boundary in DDD.", OffsetDateTime.now().minusMinutes(1))
                )
        );
    }
}
