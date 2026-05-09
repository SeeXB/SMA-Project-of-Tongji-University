package com.sma.course.service;

import com.sma.course.dto.GenerateQuizRequest;
import com.sma.course.dto.GenerateQuizResponse;
import com.sma.course.dto.SummarizeCourseRequest;
import com.sma.course.dto.SummarizeCourseResponse;

public interface CourseSummarizationService {

    SummarizeCourseResponse summarizeSlides(SummarizeCourseRequest request);

    GenerateQuizResponse generateQuiz(GenerateQuizRequest request);
}
