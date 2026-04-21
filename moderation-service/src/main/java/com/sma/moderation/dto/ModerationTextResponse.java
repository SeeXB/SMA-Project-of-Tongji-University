package com.sma.moderation.dto;

import java.util.Map;

public record ModerationTextResponse(
        boolean flagged,
        Map<String, Double> categoryScores,
        String reason
) {
}
