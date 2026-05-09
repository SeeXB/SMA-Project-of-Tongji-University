package com.sma.course.dto;

import java.util.List;

public record GenerateQuizResponse(
        String quizId,
        String courseId,
        List<QuizQuestion> questions,
        String generationNotes,
        String traceId
) {
}
