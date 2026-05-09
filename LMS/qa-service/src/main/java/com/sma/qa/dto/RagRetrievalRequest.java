package com.sma.qa.dto;

import java.util.Map;

public record RagRetrievalRequest(
        String knowledgeBase,
        String query,
        int topK,
        Map<String, String> filters
) {
}
