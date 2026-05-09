package com.sma.qa.dto;

import java.util.Map;

public record RagRetrievalItem(
        String chunkId,
        String documentId,
        double score,
        String text,
        Map<String, String> metadata
) {
}
