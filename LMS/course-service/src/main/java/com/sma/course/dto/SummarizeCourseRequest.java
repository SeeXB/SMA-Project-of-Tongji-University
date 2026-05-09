package com.sma.course.dto;

import jakarta.validation.constraints.NotBlank;

public record SummarizeCourseRequest(
        @NotBlank String fileId,
        @NotBlank String courseId,
        @NotBlank String userId,
        @NotBlank String accessToken,
        String preferredLanguage
) {
}
