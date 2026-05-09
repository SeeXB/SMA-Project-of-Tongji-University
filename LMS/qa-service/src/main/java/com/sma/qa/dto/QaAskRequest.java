package com.sma.qa.dto;

import jakarta.validation.constraints.NotBlank;

public record QaAskRequest(
        @NotBlank String courseId,
        @NotBlank String userId,
        String historyId,
        @NotBlank String question,
        Integer topK
) {
}
