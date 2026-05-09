package com.sma.assignment.dto;

import java.util.List;

public record AssignmentGradingResponse(
        String assignmentId,
        String submissionId,
        double totalScoreSuggestion,
        List<AssignmentCriterionFeedback> criterionFeedback
) {
}
