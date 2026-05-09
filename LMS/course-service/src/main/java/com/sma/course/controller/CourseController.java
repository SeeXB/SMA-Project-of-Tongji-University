package com.sma.course.controller;

import com.sma.course.dto.GenerateQuizRequest;
import com.sma.course.dto.GenerateQuizResponse;
import com.sma.course.dto.SummarizeCourseRequest;
import com.sma.course.dto.SummarizeCourseResponse;
import com.sma.course.service.CourseSummarizationService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/course")
public class CourseController {

    private final CourseSummarizationService courseSummarizationService;

    public CourseController(CourseSummarizationService courseSummarizationService) {
        this.courseSummarizationService = courseSummarizationService;
    }

    @PostMapping("/summarize")
    public ResponseEntity<SummarizeCourseResponse> summarizeSlides(
            @Valid @RequestBody SummarizeCourseRequest request
    ) {
        return ResponseEntity.ok(courseSummarizationService.summarizeSlides(request));
    }

    @PostMapping("/generate-quiz")
    public ResponseEntity<GenerateQuizResponse> generateQuiz(
            @Valid @RequestBody GenerateQuizRequest request
    ) {
        return ResponseEntity.ok(courseSummarizationService.generateQuiz(request));
    }
}
