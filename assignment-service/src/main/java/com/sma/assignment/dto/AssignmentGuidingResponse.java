package com.sma.assignment.dto;

public record AssignmentGuidingResponse(
        String assignmentId,
        String guidanceText,
        String traceId
) {
}
