package com.sma.assignment.service;

import com.sma.assignment.dto.AssignmentAiDetectionRequest;
import com.sma.assignment.dto.AssignmentAiDetectionResponse;
import com.sma.assignment.dto.AssignmentCriterionFeedback;
import com.sma.assignment.dto.AssignmentGradingRequest;
import com.sma.assignment.dto.AssignmentGradingResponse;
import com.sma.assignment.dto.AssignmentGuidingRequest;
import com.sma.assignment.dto.AssignmentGuidingResponse;
import java.util.List;
import java.util.UUID;
import org.springframework.stereotype.Service;

@Service
public class AssignmentServiceImpl implements AssignmentService {

    @Override
    public AssignmentGuidingResponse generateGuidance(AssignmentGuidingRequest request) {
        return new AssignmentGuidingResponse(
                request.assignmentId(),
                "Break the task into milestones, cite credible sources, and align your answer to the rubric.",
                UUID.randomUUID().toString()
        );
    }

    @Override
    public AssignmentGradingResponse generateGradingSuggestion(AssignmentGradingRequest request) {
        List<AssignmentCriterionFeedback> feedback = request.rubric().stream()
                .map(item -> new AssignmentCriterionFeedback(
                        item.criterionId(),
                        item.maxScore() * 0.85,
                        "The submission addresses the criterion with room for clearer evidence."
                ))
                .toList();

        double totalScore = feedback.stream().mapToDouble(AssignmentCriterionFeedback::suggestedScore).sum();
        return new AssignmentGradingResponse(request.assignmentId(), request.submissionId(), totalScore, feedback);
    }

    @Override
    public AssignmentAiDetectionResponse detectAiContent(AssignmentAiDetectionRequest request) {
        double probability = Math.min(0.95, Math.max(0.10, request.content().length() / 5000.0));
        return new AssignmentAiDetectionResponse(
                request.submissionId(),
                probability,
                probability > 0.7,
                "Heuristic placeholder based on uniform writing style and low variation."
        );
    }
}
