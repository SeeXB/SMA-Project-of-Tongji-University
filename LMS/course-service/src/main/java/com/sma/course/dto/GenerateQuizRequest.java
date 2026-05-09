package com.sma.course.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;

public record GenerateQuizRequest(
        @NotBlank String fileId,
        @NotBlank String courseId,
        @NotBlank String userId,
        @NotBlank String accessToken,
        @Min(1) @Max(10) int questionCount,
        String difficulty
) {
}
