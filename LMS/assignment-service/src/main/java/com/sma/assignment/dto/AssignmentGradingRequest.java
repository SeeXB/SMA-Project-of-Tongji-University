package com.sma.assignment.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import java.util.List;

public record AssignmentGradingRequest(
        @NotBlank String assignmentId,
        @NotBlank String submissionId,
        @NotBlank String graderId,
        String submissionText,
        @NotEmpty List<AssignmentRubricCriterion> rubric
) {
}
