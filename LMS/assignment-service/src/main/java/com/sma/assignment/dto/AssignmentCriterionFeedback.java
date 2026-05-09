package com.sma.assignment.dto;

public record AssignmentCriterionFeedback(
        String criterionId,
        double suggestedScore,
        String feedback
) {
}
