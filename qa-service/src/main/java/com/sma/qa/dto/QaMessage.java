package com.sma.qa.dto;

import java.time.OffsetDateTime;

public record QaMessage(
        String role,
        String content,
        OffsetDateTime createdAt
) {
}
