package com.sma.moderation.dto;

public record ModerationFileResponse(
        String fileId,
        boolean flagged,
        String reason
) {
}
