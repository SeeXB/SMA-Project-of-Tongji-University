package com.sma.qa.dto;

import java.time.OffsetDateTime;

public record QaHistorySummary(
        String historyId,
        String courseId,
        String lastQuestion,
        OffsetDateTime updatedAt
) {
}
