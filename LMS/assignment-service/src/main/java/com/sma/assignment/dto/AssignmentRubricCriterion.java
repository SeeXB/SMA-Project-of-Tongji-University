package com.sma.assignment.dto;

public record AssignmentRubricCriterion(
        String criterionId,
        String title,
        double maxScore,
        String description
) {
}
