package com.sma.course.dto;

import java.util.Map;

public record AiInferenceRequest(
        String capability,
        String prompt,
        String traceId,
        String userId,
        Map<String, String> metadata
) {
}
