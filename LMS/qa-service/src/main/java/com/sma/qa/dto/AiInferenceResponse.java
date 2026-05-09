package com.sma.qa.dto;

public record AiInferenceResponse(
        String capability,
        String traceId,
        String outputText,
        String provider,
        String model
) {
}
