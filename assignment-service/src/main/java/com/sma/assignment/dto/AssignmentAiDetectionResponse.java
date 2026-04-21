package com.sma.assignment.dto;

public record AssignmentAiDetectionResponse(
        String submissionId,
        double aiProbability,
        boolean flagged,
        String rationale
) {
}
