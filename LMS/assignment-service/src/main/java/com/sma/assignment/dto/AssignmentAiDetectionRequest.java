package com.sma.assignment.dto;

import jakarta.validation.constraints.NotBlank;

public record AssignmentAiDetectionRequest(
        @NotBlank String assignmentId,
        @NotBlank String submissionId,
        @NotBlank String content
) {
}
