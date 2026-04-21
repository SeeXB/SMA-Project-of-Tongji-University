package com.sma.moderation.dto;

import jakarta.validation.constraints.NotBlank;

public record ModerationTextRequest(
        @NotBlank String text,
        @NotBlank String userId,
        @NotBlank String scene
) {
}
