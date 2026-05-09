package com.sma.assignment.controller;

import com.sma.assignment.dto.AssignmentAiDetectionRequest;
import com.sma.assignment.dto.AssignmentAiDetectionResponse;
import com.sma.assignment.dto.AssignmentGradingRequest;
import com.sma.assignment.dto.AssignmentGradingResponse;
import com.sma.assignment.dto.AssignmentGuidingRequest;
import com.sma.assignment.dto.AssignmentGuidingResponse;
import com.sma.assignment.service.AssignmentService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/assignment")
public class AssignmentController {

    private final AssignmentService assignmentService;

    public AssignmentController(AssignmentService assignmentService) {
        this.assignmentService = assignmentService;
    }

    @PostMapping("/guiding")
    public ResponseEntity<AssignmentGuidingResponse> guiding(@Valid @RequestBody AssignmentGuidingRequest request) {
        return ResponseEntity.ok(assignmentService.generateGuidance(request));
    }

    @PostMapping("/grading")
    public ResponseEntity<AssignmentGradingResponse> grading(@Valid @RequestBody AssignmentGradingRequest request) {
        return ResponseEntity.ok(assignmentService.generateGradingSuggestion(request));
    }

    @PostMapping("/detect-ai")
    public ResponseEntity<AssignmentAiDetectionResponse> detectAi(
            @Valid @RequestBody AssignmentAiDetectionRequest request
    ) {
        return ResponseEntity.ok(assignmentService.detectAiContent(request));
    }
}
