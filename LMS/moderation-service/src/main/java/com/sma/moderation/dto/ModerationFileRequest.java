package com.sma.moderation.dto;

import jakarta.validation.constraints.NotBlank;

public record ModerationFileRequest(
        @NotBlank String fileId,
        @NotBlank String userId,
        @NotBlank String fileType,
        String extractedText
) {
}
