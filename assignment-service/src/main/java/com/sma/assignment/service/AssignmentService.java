package com.sma.assignment.service;

import com.sma.assignment.dto.AssignmentAiDetectionRequest;
import com.sma.assignment.dto.AssignmentAiDetectionResponse;
import com.sma.assignment.dto.AssignmentGradingRequest;
import com.sma.assignment.dto.AssignmentGradingResponse;
import com.sma.assignment.dto.AssignmentGuidingRequest;
import com.sma.assignment.dto.AssignmentGuidingResponse;

public interface AssignmentService {

    AssignmentGuidingResponse generateGuidance(AssignmentGuidingRequest request);

    AssignmentGradingResponse generateGradingSuggestion(AssignmentGradingRequest request);

    AssignmentAiDetectionResponse detectAiContent(AssignmentAiDetectionRequest request);
}
