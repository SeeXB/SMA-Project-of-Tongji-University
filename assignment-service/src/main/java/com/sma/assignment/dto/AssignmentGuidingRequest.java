package com.sma.assignment.dto;

import jakarta.validation.constraints.NotBlank;
import java.util.List;

public record AssignmentGuidingRequest(
        @NotBlank String assignmentId,
        @NotBlank String courseId,
        @NotBlank String userId,
        @NotBlank String prompt,
        List<String> contextFileIds
) {
}
