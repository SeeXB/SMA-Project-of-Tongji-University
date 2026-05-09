package com.sma.qa.dto;

import java.util.List;

public record RagRetrievalResponse(
        String query,
        List<RagRetrievalItem> results,
        String collectionName
) {
}
