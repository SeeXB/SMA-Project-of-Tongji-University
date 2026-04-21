package com.sma.qa.dto;

import java.util.List;

public record QaHistoryDetailResponse(
        String historyId,
        List<QaMessage> messages
) {
}
