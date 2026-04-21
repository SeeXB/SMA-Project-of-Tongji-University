package com.sma.course.dto;

import java.util.List;

public record QuizQuestion(
        String questionId,
        String stem,
        List<String> options,
        String answer,
        String explanation
) {
}
