package com.sma.qa.dto;

import java.util.List;

public record QaAskResponse(
        String historyId,
        String answer,
        List<QaCitation> citations,
        String traceId
) {
}
